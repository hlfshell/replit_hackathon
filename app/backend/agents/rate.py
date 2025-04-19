from arkaine.tools.agent import Agent, Argument
from arkaine.utils.templater import PromptLoader
from arkaine.utils.parser import Parser, Label
from arkaine.llms.llm import LLM, Prompt
from arkaine.tools.context import Context
from typing import Optional, Any
from app.backend.models.rating import Rating
from app.backend.store import Store
from arkaine.flow import ParallelList




class RateAgent(Agent):

    EMOTIONS = [
        # Happy emotions
        "Happy", "Joyful", "Excited", "Interested", "Proud", "Accepted", "Powerful",
        "Peaceful", "Intimate", "Loving", "Hopeful", "Playful", "Inspired", "Open",
        "Confident", "Important", "Fulfilled", "Respected", "Courageous", "Provocative",
        "Sensitive", "Energetic", "Liberated", "Ecstatic", "Eager", "Awe", "Astonished",
        "Perplexed", "Dismayed", "Shocked", "Terrified", "Frightened", "Worried",
        "Overwhelmed", "Inadequate", "Inferior", "Worthless", "Insignificant",
        "Alienated", "Disrespected", "Ridiculed", "Embarrassed", "Devastated",
        "Resentful", "Jealous", "Violated",

        # Fearful emotions
        "Fear", "Scared", "Anxious", "Insecure", "Submissive", "Hurt", "Humiliated",
        "Threatened",

        # Angry emotions
        "Anger", "Mad", "Hateful", "Aggressive", "Frustrated", "Hostile", "Enraged",
        "Furious", "Violent", "Irritated", "Infuriated", "Provoked", "Withdrawn",
        "Suspicious", "Skeptical", "Sarcastic", "Judgmental",

        # Disgusted emotions
        "Disgust", "Critical", "Distant", "Disappointed", "Awful", "Loathing",
        "Repugnant", "Revolted", "Revulsion", "Detestable", "Aversion",

        # Sad emotions
        "Sad", "Lonely", "Bored", "Depressed", "Despair", "Abandoned", "Ignored",
        "Victimized", "Powerless", "Vulnerable", "Inferior", "Empty", "Isolated",
        "Apathetic", "Indifferent",

        # Guilt/Shame related emotions
        "Guilty", "Remorseful", "Ashamed", "Hesitant", "Avoidance",

        # Surprise related emotions
        "Surprise", "Startled", "Confused", "Amazed", "Excited" # Excited is also under happy, context matters
    ]

    EFFECTIVENESS = [
        "Not Relevant",
        "Low Fit",
        "Neutral/Okay",
        "Good Fit",
        "Strong Match"
    ]

    def __init__(self, llm: LLM, store: Store):
        
        self.__store = store

        self.parser = Parser([
            Label("thought", data_type="str"),
            Label("emotionalresponse", data_type="str"),
            Label("emotions", data_type="str"),
            Label("effectiveness", data_type="str"),
        ])

        super().__init__(
            name="RateAgent",
            description="Rate an ad based on the given personality.",
            args=[
                Argument(
                    "personality",
                    description="The personality to rate the ad for.",
                    required=True,
                    type=str
                ),
                Argument(
                    name="ad",
                    description="The ad to rate.",
                    required=True,
                    type=str
                )
            ],
            llm=llm
        )

    def prepare_prompt(self, context: Context, personality: str, ad: str) -> Prompt:
        context.x["personality"] = personality
        context.x["ad"] = ad

        prompt = PromptLoader.load_prompt("rate")

        persona = self.__store.personality.get(personality)
        if not persona:
            raise ValueError(f"Personality {personality} not found")

        ad_obj = self.__store.ad.get(ad)
        if not ad_obj:
            raise ValueError(f"Ad {ad} not found")

        personality_str = f"{persona.name}:\n"
        personality_str += f"\t - Age: {persona.age}\n"
        personality_str += f"\t - Gender: {persona.gender}\n"
        personality_str += f"\t - Location: {persona.location}\n"
        personality_str += f"\t - Education Level: {persona.education_level}\n"
        personality_str += f"\t - Marital Status: {persona.marital_status}\n"
        personality_str += f"\t - Children: {persona.children}\n"
        personality_str += f"\t - Occupation: {persona.occupation}\n"
        personality_str += f"\t - Job Title: {persona.job_title}\n"
        personality_str += f"\t - Industry: {persona.industry}\n"
        personality_str += f"\t - Income: {persona.income}\n"
        personality_str += f"\t - Seniority Level: {persona.seniority_level}\n"
        personality_str += f"\t - Personality Traits: {', '.join(persona.personality_traits)}\n"
        personality_str += f"\t - Values: {', '.join(persona.values)}\n"
        personality_str += f"\t - Attitudes: {', '.join(persona.attitudes)}\n"
        personality_str += f"\t - Interests: {', '.join(persona.interests)}\n"
        personality_str += f"\t - Lifestyle: {', '.join(persona.lifestyle)}\n"
        personality_str += f"\t - Habits: {', '.join(persona.habits)}\n"
        personality_str += f"\t - Frustrations: {', '.join(persona.frustrations)}\n"
        personality_str += f"\t - Summary: {persona.summary}\n"

        context.x["ad_filepath"] = ad_obj.image

        return prompt.render({
            "emotions_list": ", ".join(self.EMOTIONS),
            "personality": personality_str,
        })

    def extract_result(self, context: Context, output: str) -> Optional[Any]:
        values, errors = self.parser.parse(output)
        if errors:
            raise ValueError(errors)
        
        # Try and split apart the emotions as a list. It should
        # be comma separated
        emotions = values["emotions"].split(",")
        
        # Filter out non matching
        emotions = [e.lower().strip() for e in emotions if e.lower().strip() in self.EMOTIONS]

        return Rating(
            personality=context.x["personality"],
            ad=context.x["ad"],
            thought=values["thought"],
            emotional_response=values["emotionalresponse"],
            emotions=emotions,
            effectiveness=values["effectiveness"]
        )
