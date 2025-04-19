import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { PersonalityTag } from "./PersonalityTag";
import { Personality } from "@shared/schema";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search } from "lucide-react";

const PERSONALITY_TYPES = [
  "Professional", "Creative", "Casual", "Formal", 
  "Humorous", "Serious", "Enthusiastic", "Technical"
];

interface PersonalitySelectorProps {
  value: string[];
  onChange: (value: string[]) => void;
}

export function PersonalitySelector({ value, onChange }: PersonalitySelectorProps) {
  const [searchTerm, setSearchTerm] = useState("");
  // Removed filter dropdown
  
  const { data: personalities, isLoading, error } = useQuery<Personality[]>({
    queryKey: ["/api/personalities"],
  });

  const getSelectedPersonalities = () => {
    if (!personalities) return [];
    return personalities.filter(p => value.includes(p.id));
  };

  const addPersonality = (personality: Personality) => {
    if (value.length >= 10) {
      alert("You can select up to 10 personalities");
      return;
    }
    
    if (!value.includes(personality.id)) {
      onChange([...value, personality.id]);
    }
  };

  const removePersonality = (id: string) => {
    onChange(value.filter(p => p !== id));
  };

  const handleQuickSelect = (type: string) => {
    if (!personalities) return;
    
    // Find a personality with matching traits
    const matchingPersonality = personalities.find(p => 
      p.personality_traits?.some((trait: string) => 
        trait.toLowerCase() === type.toLowerCase()
      )
    );
    
    if (matchingPersonality && !value.includes(matchingPersonality.id)) {
      addPersonality(matchingPersonality);
    }
  };

  const filteredPersonalities = () => {
    if (!personalities) return [];
    
    // Only apply search filtering
    return personalities.filter(personality => {
      const searchTermLower = searchTerm.trim().toLowerCase();
      
      return searchTerm.trim() === "" || 
        personality.name.toLowerCase().includes(searchTermLower) ||
        (personality.summary && personality.summary.toLowerCase().includes(searchTermLower)) ||
        (personality.age && personality.age.toString().includes(searchTerm.trim())) ||
        (personality.occupation && personality.occupation.toLowerCase().includes(searchTermLower)) ||
        (personality.location && personality.location.toLowerCase().includes(searchTermLower)) ||
        (personality.industry && personality.industry.toLowerCase().includes(searchTermLower));
    });
  };

  return (
    <div>
      <div className="flex flex-col md:flex-row gap-3 mb-3">
        <div className="flex-grow">
          <div className="relative">
            <Input
              id="personalitySearch"
              placeholder="Search by name, age, location, occupation..."
              className="pl-10 w-full focus:border-purple-400 focus:ring-purple-400"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <div className="absolute left-3 top-2.5 text-gray-400">
              <Search className="w-5 h-5" />
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-3 min-h-8">
        {getSelectedPersonalities().map(personality => (
          <PersonalityTag
            key={personality.id}
            id={personality.id}
            name={personality.name}
            onRemove={removePersonality}
          />
        ))}
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {PERSONALITY_TYPES.map(type => (
          <span
            key={type}
            className={`
              px-3 py-1 bg-gray-100 text-gray-700 rounded-full cursor-pointer 
              hover:bg-purple-600 hover:text-white transition-colors
            `}
            onClick={() => handleQuickSelect(type)}
          >
            {type}
          </span>
        ))}
      </div>

      <div className="border border-gray-300 rounded-lg max-h-60 overflow-y-auto">
        {isLoading && (
          <div className="p-4 text-center text-gray-500">Loading personalities...</div>
        )}
        
        {error && (
          <div className="p-4 text-center text-red-500">
            Error loading personalities. Please try again.
          </div>
        )}
        
        {filteredPersonalities().map(personality => (
          <div 
            key={personality.id}
            className={`
              personality-item border-b border-gray-200 last:border-b-0 p-4 
              ${value.includes(personality.id) ? 'bg-purple-50' : 'hover:bg-gray-50'} 
              cursor-pointer transition-colors
            `}
            onClick={() => {
              // Toggle selection - if already selected, remove it
              if (value.includes(personality.id)) {
                removePersonality(personality.id);
              } else {
                addPersonality(personality);
              }
            }}
          >
            <div className="flex items-start">
              <div className="flex-shrink-0 mt-0.5">
                <div className={`
                  w-5 h-5 border rounded flex items-center justify-center
                  ${value.includes(personality.id) 
                    ? 'bg-purple-600 border-purple-600' 
                    : 'border-gray-300'}
                `}>
                  {value.includes(personality.id) && (
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                    </svg>
                  )}
                </div>
              </div>
              <div className="ml-3">
                <div className="flex items-center flex-wrap gap-y-1">
                  <h4 className="font-medium text-gray-900">{personality.name}</h4>
                  {personality.age && (
                    <span className="ml-2 text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded-full">
                      {personality.age} years
                    </span>
                  )}
                  {personality.occupation && (
                    <span className="ml-2 text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full">
                      {personality.occupation}
                    </span>
                  )}
                </div>
                {personality.summary && (
                  <p className="text-sm text-gray-600 mt-1">{personality.summary}</p>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {!isLoading && filteredPersonalities().length === 0 && (
          <div className="p-4 text-center text-gray-500">
            No personalities match your search criteria.
          </div>
        )}
      </div>
    </div>
  );
}
