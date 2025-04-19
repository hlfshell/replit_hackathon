import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface PersonalityTagProps {
  id: string;
  name: string;
  onRemove: (id: string) => void;
  className?: string;
}

export function PersonalityTag({ id, name, onRemove, className }: PersonalityTagProps) {
  return (
    <span 
      className={cn(
        "px-3 py-1 bg-purple-600 text-white rounded-full flex items-center text-sm",
        className
      )}
    >
      {name}
      <button 
        type="button" 
        className="ml-1 focus:outline-none"
        onClick={() => onRemove(id)}
      >
        <X className="w-4 h-4" />
      </button>
    </span>
  );
}
