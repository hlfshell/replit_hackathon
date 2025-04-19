import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { AdFeedback, Personality } from "@shared/schema";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// Define feedback result type that extends from submitted feedback
interface FeedbackResult {
  adFeedback: AdFeedback;
  personalityFeedback: PersonalityFeedback[];
}

// Define personality feedback interface
interface PersonalityFeedback {
  personalityId: string;
  personality: Personality;
  rating: number;
  thought: string;
  emotionalResponse: string;
  emotions: string[];
  categories: string[];
}

// Define rating levels for color coding
const getRatingLevel = (rating: number) => {
  if (rating >= 9) return { label: "Strong Match", color: "bg-green-100 text-green-800", icon: "✅" };
  if (rating >= 7) return { label: "Good Fit", color: "bg-blue-100 text-blue-800", icon: "👍" };
  if (rating >= 4) return { label: "Neutral/Okay", color: "bg-yellow-100 text-yellow-800", icon: "🤔" };
  if (rating >= 2) return { label: "Low Fit", color: "bg-orange-100 text-orange-800", icon: "⚠️" };
  return { label: "Not Relevant", color: "bg-red-100 text-red-800", icon: "❌" };
};

// Define emotion tooltips for hover explanations
const emotionTooltips: Record<string, string> = {
  Interested: "Shows engagement and attention to the ad content",
  Confident: "Feels assured about the product/service quality",
  Inspired: "Feels motivated or creatively stimulated",
  Curious: "Wants to learn more about the offering",
  Critical: "Has concerns or questions about certain aspects",
  Hopeful: "Sees potential value in the product/service",
  Happy: "Feels positive about the overall message",
  Excited: "Enthusiastic about trying the product/service",
  Eager: "Ready to take action or make a purchase",
  Respected: "Feels valued and understood by the brand",
  Disappointed: "Expected more from the ad or offering",
  Bored: "Finds the content unengaging or too familiar",
  Indifferent: "Neither positive nor negative reaction",
  Fulfilled: "Feels the ad addresses a specific need",
};

// Mock data generator based on personalities
const generateFeedback = (personalities: Personality[]): FeedbackResult => {
  const mockAdFeedback: AdFeedback = {
    id: 1,
    description: "Modern furniture ad showcasing minimalist design with affordable pricing for young professionals and new homeowners.",
    image_url: "/uploads/furniture-ad.jpg",
    personality_ids: personalities.map(p => p.id),
    created_at: new Date().toISOString(),
  };

  const personalityTypes = ["Professional", "Creative", "Casual"];
  
  const mockFeedback: PersonalityFeedback[] = personalities.map(personality => {
    // Determine personality type from traits
    const type = personality.personality_traits?.find((trait: string) => 
      personalityTypes.includes(trait)
    ) || "Professional";
    
    let rating = 0;
    let thought = "";
    let emotionalResponse = "";
    let emotions: string[] = [];
    let categories: string[] = [];
    
    // Generate different feedback based on personality type
    if (type === "Professional") {
      rating = Math.floor(Math.random() * 4) + 7; // 7-10
      thought = "This ad effectively communicates the product's value proposition with a clean, professional aesthetic.";
      emotionalResponse = "Positively impressed by the design quality and messaging clarity.";
      emotions = ["Interested", "Confident", "Respected"];
      categories = ["Design", "Messaging", "Professional Appeal"];
    } else if (type === "Creative") {
      const isPositive = Math.random() > 0.5;
      rating = isPositive ? Math.floor(Math.random() * 4) + 6 : Math.floor(Math.random() * 4) + 2; // 6-9 or 2-5
      thought = isPositive 
        ? "The color palette is appealing, but the typography lacks originality. The composition could be more dynamic."
        : "The designs are too conventional and don't offer anything new to the market. I was hoping for more innovative pieces.";
      emotionalResponse = isPositive 
        ? "Somewhat inspired but wanting more creative risks."
        : "Underwhelmed by the lack of originality.";
      emotions = isPositive 
        ? ["Curious", "Critical", "Hopeful"] 
        : ["Disappointed", "Bored", "Indifferent"];
      categories = isPositive 
        ? ["Visual Design", "Typography", "Innovation"] 
        : ["Innovation", "Uniqueness", "Design Trends"];
    } else if (type === "Casual") {
      rating = Math.floor(Math.random() * 3) + 8; // 8-10
      thought = "Love how approachable this makes furniture shopping feel! The prices seem reasonable and the style is exactly what I'm looking for.";
      emotionalResponse = "Excited about the possibility of purchasing these items.";
      emotions = ["Happy", "Excited", "Eager"];
      categories = ["Affordability", "Style", "Approachability"];
    }
    
    return {
      personalityId: personality.id,
      personality,
      rating,
      thought,
      emotionalResponse,
      emotions,
      categories,
    };
  });

  return {
    adFeedback: mockAdFeedback,
    personalityFeedback: mockFeedback,
  };
};

export default function FeedbackResults() {
  const [, setLocation] = useLocation();
  const [selectedPersonalityType, setSelectedPersonalityType] = useState<string | null>(null);
  
  // Fetch personalities from API
  const { data: personalities, isLoading } = useQuery<Personality[]>({
    queryKey: ["/api/personalities"],
  });
  
  // Generate mock feedback once personalities are loaded
  const feedbackResult = personalities ? generateFeedback(personalities) : null;
  
  // Filter feedback by selected personality type
  const filteredFeedback = selectedPersonalityType
    ? feedbackResult?.personalityFeedback.filter(feedback => 
        feedback.personality.personality_traits?.includes(selectedPersonalityType)
      )
    : feedbackResult?.personalityFeedback;
  
  if (isLoading || !feedbackResult) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Generating Feedback...</h1>
          <p className="text-gray-600">Please wait while we analyze your advertisement</p>
        </div>
      </div>
    );
  }
  
  // Extract unique personality types
  const personalityTypes = Array.from(new Set(
    personalities?.flatMap(p => p.personality_traits || []) || []
  )).filter((type: string) => ["Professional", "Creative", "Casual", "Formal", "Technical", "Humorous"].includes(type));
  
  return (
    <div className="container mx-auto py-8 px-4">
      {/* Ad Preview Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Ad Feedback Results</h1>
          <Button 
            variant="outline" 
            onClick={() => setLocation("/")}
          >
            Create New Ad
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            {feedbackResult.adFeedback.image_url && (
              <div className="mb-4 rounded-md overflow-hidden border border-gray-200">
                <img 
                  src={feedbackResult.adFeedback.image_url} 
                  alt="Advertisement" 
                  className="w-full h-auto object-cover"
                />
              </div>
            )}
          </div>
          
          <div className="md:col-span-2">
            <h2 className="text-lg font-semibold mb-2">Ad Description</h2>
            <p className="text-gray-700 mb-4">{feedbackResult.adFeedback.description}</p>
            
            <h3 className="text-md font-medium mb-2">Filter by personality type:</h3>
            <div className="flex flex-wrap gap-2 mb-4">
              <Badge 
                className={`cursor-pointer ${!selectedPersonalityType ? 'bg-purple-600' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
                onClick={() => setSelectedPersonalityType(null)}
              >
                All
              </Badge>
              
              {personalityTypes.map((type) => (
                <Badge 
                  key={type}
                  className={`cursor-pointer ${selectedPersonalityType === type ? 'bg-purple-600' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
                  onClick={() => setSelectedPersonalityType(type)}
                >
                  {type}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Personality Feedback Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredFeedback?.map((feedback) => {
          const rating = getRatingLevel(feedback.rating);
          
          return (
            <div 
              key={feedback.personalityId} 
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h2 className="text-xl font-semibold">
                    {feedback.personality.name.split(' ')[0]}, {feedback.personality.age}
                  </h2>
                  <p className="text-gray-600 text-sm">
                    {feedback.personality.summary?.substring(0, 60)}
                    {feedback.personality.summary && feedback.personality.summary.length > 60 ? '...' : ''}
                  </p>
                </div>
                
                {feedback.personality.personality_traits?.map((trait: string, index: number) => (
                  personalityTypes.includes(trait) && (
                    <Badge key={index} className="bg-gray-800 text-white">
                      {trait}
                    </Badge>
                  )
                ))}
              </div>
              
              <div className="mb-4">
                <div className="flex justify-between mb-1">
                  <span className="font-medium">Rating</span>
                  <span className="font-medium">
                    {feedback.rating === 10 ? (
                      <span className="text-green-600">10/10</span>
                    ) : (
                      <span>{feedback.rating}/10</span>
                    )}
                  </span>
                </div>
                
                <div className="relative h-2 bg-gray-200 rounded-full mb-2">
                  <div 
                    className="absolute top-0 left-0 h-2 bg-purple-600 rounded-full" 
                    style={{ width: `${feedback.rating * 10}%` }}
                  ></div>
                </div>
                
                <div className={`${rating.color} px-3 py-1 rounded-full text-sm inline-flex items-center`}>
                  <span className="mr-1">{rating.icon}</span> {rating.label}
                </div>
              </div>
              
              <div className="mb-4">
                <h3 className="font-medium mb-1">Thought</h3>
                <p className="text-gray-700 text-sm">{feedback.thought}</p>
              </div>
              
              <div className="mb-4">
                <h3 className="font-medium mb-1">Emotional Response</h3>
                <p className="text-gray-700 text-sm">{feedback.emotionalResponse}</p>
              </div>
              
              <div className="mb-4">
                <h3 className="font-medium mb-1">Emotions</h3>
                <div className="flex flex-wrap gap-2">
                  <TooltipProvider>
                    {feedback.emotions.map((emotion, index) => (
                      <Tooltip key={index}>
                        <TooltipTrigger asChild>
                          <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">
                            {emotion}
                          </span>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p className="text-sm">{emotionTooltips[emotion] || emotion}</p>
                        </TooltipContent>
                      </Tooltip>
                    ))}
                  </TooltipProvider>
                </div>
              </div>
              
              <div>
                <h3 className="font-medium mb-1">Categories</h3>
                <div className="flex flex-wrap gap-2">
                  {feedback.categories.map((category, index) => (
                    <span key={index} className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-xs">
                      {category}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="text-center text-gray-500 text-xs mt-8">
        <p>This feedback is generated based on personality profiles and may not represent actual consumer opinions.</p>
        <p>© 2023 Ad Feedback Platform. All rights reserved.</p>
      </div>
    </div>
  );
}