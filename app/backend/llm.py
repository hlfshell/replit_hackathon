from arkaine.llms.llm import LLM, Prompt
import google.generativeai as genai

import os
from typing import Optional


class MultiModalLLM(LLM):
    MODELS = {
        "gemini-pro": {"context_length": 30720},
        "gemini-1.0-pro": {"context_length": 30720},
        "gemini-2.0-flash-001": {"context_length": 1_000_000},
        "gemini-2.0-pro-exp-02-05": {"context_length": 2_000_000},
        "gemini-2.5-flash-preview-04-17": {"context_length": 2_000_000},
    }

    def __init__(
        self,
        model: str = "gemini-pro",
        api_key: Optional[str] = None,
        context_length: Optional[int] = None,
    ):
        if api_key is None:
            api_key = os.environ.get("GOOGLE_AISTUDIO_API_KEY")
            if api_key is None:
                api_key = os.environ.get("GOOGLE_API_KEY")
            if api_key is None:
                raise ValueError(
                    "No Google API key found. Please set "
                    "GOOGLE_AISTUDIO_API_KEY or GOOGLE_API_KEY "
                    "environment variable"
                )

        genai.configure(api_key=api_key)
        self.__model = genai.GenerativeModel(model_name=model)

        if context_length:
            self.__context_length = context_length
        elif model in MultiModalLLM.MODELS:
            self.__context_length = MultiModalLLM.MODELS[model]["context_length"]
        else:
            raise ValueError(
                f"Unknown model: {model} - must specify context length"
            )

        super().__init__(name=f"gemini:{model}")

    @property
    def context_length(self) -> int:
        return self.__context_length

    def completion(self, prompt: Prompt, image_path: Optional[str] = None) -> str:
        # Convert the chat format to Gemini's expected format
        history = []
        for message in prompt:
            role = message["role"]
            content = message["content"]

            # Map OpenAI roles to Gemini roles
            if role == "system":
                history.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                history.append({"role": "model", "parts": [content]})
            elif role == "user":
                history.append({"role": "user", "parts": [content]})

        # Create a chat session and send the entire history
        chat = self.__model.start_chat(history=history[:-1])
        
        # Handle the last message which might include an image
        last_message = history[-1]["parts"][0]
        
        if image_path and os.path.exists(image_path):
            try:
                import google.ai.generativelanguage as glm
                
                # Read the image file
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                
                # Determine MIME type based on file extension
                mime_type = "image/jpeg"  # Default
                if image_path.lower().endswith(".png"):
                    mime_type = "image/png"
                elif image_path.lower().endswith(".gif"):
                    mime_type = "image/gif"
                
                # Create a blob for the image
                image_blob = glm.Blob(
                    mime_type=mime_type,
                    data=image_bytes
                )
                
                # Create parts with both image and text
                parts = [
                    image_blob,
                    last_message
                ]
                
                # Send message with image
                response = chat.send_message(parts)
            except Exception as e:
                print(f"Error processing image: {e}")
                # Fallback to text-only if image processing fails
                response = chat.send_message(last_message)
        else:
            # Text-only message
            response = chat.send_message(last_message)

        print(response.text)
        return response.text

    def __str__(self) -> str:
        return self.name

    def __call__(self, *args, **kwargs) -> str:
        context, prompt = self.extract_arguments(args, kwargs)

        with self._init_context_(context, prompt) as ctx:
            image_path = ctx.x["ad_filepath"]
            result = self.completion(prompt, image_path)

            if isinstance(result, tuple):
                response, reasoning = result
            else:
                response = result
                reasoning = ""

            ctx["estimated_tokens"] = {
                "prompt": self.estimate_tokens(prompt),
                "image": self.estimate_tokens(image_path),
                "response": self.estimate_tokens(response),
            }
            ctx.output = response
            if reasoning:
                ctx["reasoning"] = reasoning
            return response