import { useState } from "react";
import { FileUploader } from "./FileUploader";
import { PersonalitySelector } from "./PersonalitySelector";
import { useToast } from "@/hooks/use-toast";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Personality } from "@shared/schema";
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useLocation } from "wouter";

const formSchema = z.object({
  description: z.string().optional(),
  imageFile: z.instanceof(File, { message: "Please upload an image" }).optional(),
  selectedPersonalities: z.array(z.string()).min(1, "Please select at least one personality")
}).refine(data => !!data.description || !!data.imageFile, {
  message: "Either description or image is required",
  path: ["description"] // Show error on the description field
});

type FormData = z.infer<typeof formSchema>;

export function AdFeedbackForm() {
  const { toast } = useToast();
  const [, setLocation] = useLocation();
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      description: "",
      selectedPersonalities: []
    }
  });

  const handleImageChange = (file: File | null) => {
    if (file) {
      form.setValue("imageFile", file);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      form.setValue("imageFile", undefined as any);
      setImagePreview(null);
    }
  };

  const submitMutation = useMutation({
    mutationFn: async (data: FormData) => {
      console.log("Submitting form data:", data);
      const formData = new FormData();
      
      // Add description (empty string if not provided)
      if (data.description) {
        formData.append("description", data.description);
        console.log("Added description:", data.description);
      }
      
      // Only add image if it exists
      if (data.imageFile) {
        formData.append("image", data.imageFile);
        console.log("Added image file:", data.imageFile.name);
      }
      
      formData.append("personalities", JSON.stringify(data.selectedPersonalities));
      console.log("Added personalities:", data.selectedPersonalities);
      
      // Log the FormData entries for debugging
      console.log("FormData entries:");
      // Use Array.from to avoid TypeScript iterator issues
      Array.from(formData.entries()).forEach(entry => {
        console.log(entry[0], entry[1]);
      });
      
      return await apiRequest("POST", "/api/feedback", formData);
    },
    onSuccess: () => {
      toast({
        title: "Success!",
        description: "Your ad has been submitted for feedback."
      });
      form.reset();
      setImagePreview(null);
      
      // Redirect to feedback results page
      setLocation("/feedback-results");
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message || "There was an error submitting your ad.",
        variant: "destructive"
      });
    }
  });

  const onSubmit = (data: FormData) => {
    submitMutation.mutate(data);
  };

  return (
    <div className="bg-white rounded-xl shadow-md w-full max-w-2xl p-5 md:p-8">
      <h1 className="text-purple-600 text-2xl md:text-3xl font-bold text-center mb-2">
        Please upload your AD here
      </h1>
      <p className="text-gray-600 text-center mb-8">
        Upload your ad to receive valuable feedback from our diverse audience
      </p>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-gray-700 font-medium">Tell us about your ad (optional if image is uploaded)</FormLabel>
                <FormControl>
                  <Textarea 
                    placeholder="Describe your ad, target audience, and what kind of feedback you're looking for..."
                    className="h-32 resize-none"
                    {...field}
                  />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="imageFile"
            render={() => (
              <FormItem>
                <FormLabel className="text-gray-700 font-medium">Upload your ad image (optional if description is provided)</FormLabel>
                <FormControl>
                  <FileUploader 
                    onFileChange={handleImageChange} 
                    imagePreview={imagePreview}
                  />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="selectedPersonalities"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-gray-700 font-medium">Select target personalities (multiple)</FormLabel>
                <FormControl>
                  <PersonalitySelector
                    value={field.value}
                    onChange={field.onChange}
                  />
                </FormControl>
              </FormItem>
            )}
          />

          <Button 
            type="submit" 
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-6"
            disabled={submitMutation.isPending}
          >
            {submitMutation.isPending ? "Submitting..." : "Get Feedback"}
          </Button>
        </form>
      </Form>

      <div className="mt-8 text-center">
        <div className="flex justify-center space-x-4 text-sm mb-3">
          <a href="#" className="text-purple-600 hover:underline">Terms</a>
          <a href="#" className="text-purple-600 hover:underline">Privacy</a>
          <a href="#" className="text-purple-600 hover:underline">Help</a>
        </div>
        <p className="text-gray-500 text-sm">We respect your privacy and will never share your data.</p>
      </div>
    </div>
  );
}
