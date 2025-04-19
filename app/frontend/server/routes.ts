import type { Express, Request, Response, NextFunction } from "express";
import { createServer, type Server } from "http";
import path from "path";
import multer from "multer";
import axios from "axios";
import fs from "fs/promises";
import { randomUUID } from "crypto";
import express from "express";

// Configure multer storage for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB limit
  },
  fileFilter: (_req, file, cb) => {
    const allowedTypes = ["image/jpeg", "image/png", "image/gif"];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error("Invalid file type. Only JPG, PNG, and GIF are allowed.") as any);
    }
  },
});

// Create uploads directory if it doesn't exist
const ensureUploadsDir = async () => {
  const uploadsDir = path.join(process.cwd(), "uploads");
  try {
    await fs.access(uploadsDir);
  } catch (error) {
    await fs.mkdir(uploadsDir, { recursive: true });
  }
  return uploadsDir;
};

// Mock data for personalities
const mockPersonalities = [
  {
    id: "p1",
    name: "Sarah Chen",
    age: 34,
    gender: "female",
    occupation: "Marketing Manager",
    location: "San Francisco",
    industry: "Technology",
    summary: "Tech-savvy professional who values innovation and ethical brands",
    personality_traits: ["Professional", "Analytical", "Curious"],
  },
  {
    id: "p2",
    name: "Carlos Rodriguez",
    age: 28,
    gender: "male",
    occupation: "Graphic Designer",
    location: "New York",
    industry: "Creative Arts",
    summary: "Creative mind seeking visually stunning and unique products",
    personality_traits: ["Creative", "Visual", "Trend-conscious"],
  },
  {
    id: "p3",
    name: "Emma Johnson",
    age: 42,
    gender: "female",
    occupation: "Senior Accountant",
    location: "Chicago",
    industry: "Finance",
    summary: "Practical professional who values clear messaging and proven quality",
    personality_traits: ["Professional", "Analytical", "Detail-oriented"],
  },
  {
    id: "p4",
    name: "Miguel Sanchez",
    age: 25,
    gender: "male",
    occupation: "Content Creator",
    location: "Los Angeles",
    industry: "Social Media",
    summary: "Influencer focused on lifestyle trends and authentic storytelling",
    personality_traits: ["Creative", "Casual", "Trend-setter"],
  },
  {
    id: "p5",
    name: "Jordan Taylor",
    age: 31,
    gender: "non-binary",
    occupation: "Software Engineer",
    location: "Seattle",
    industry: "Technology",
    summary: "Tech enthusiast who values functionality and innovation",
    personality_traits: ["Technical", "Analytical", "Direct"],
  },
  {
    id: "p6",
    name: "Rebecca Wong",
    age: 38,
    gender: "female",
    occupation: "School Teacher",
    location: "Boston",
    industry: "Education",
    summary: "Practical consumer who values educational content and family-friendly messaging",
    personality_traits: ["Casual", "Thoughtful", "Community-oriented"],
  },
  {
    id: "p7",
    name: "Alex Martinez",
    age: 22,
    gender: "male",
    occupation: "College Student",
    location: "Austin",
    industry: "Education",
    summary: "Budget-conscious student passionate about social causes",
    personality_traits: ["Casual", "Enthusiastic", "Value-oriented"],
  },
  {
    id: "p8",
    name: "Liam Kennedy",
    age: 45,
    gender: "male",
    occupation: "Business Executive",
    location: "Denver",
    industry: "Corporate",
    summary: "Decision-maker who values professionalism and efficiency",
    personality_traits: ["Professional", "Direct", "Status-conscious"],
  }
];

export async function registerRoutes(app: Express): Promise<Server> {
  // Mock endpoint to fetch all personalities
  app.get("/personalities", (_req, res) => {
    res.json(mockPersonalities);
  });

  // Mock endpoint to get a specific personality
  app.get("/personalities/:id", (req, res) => {
    const { id } = req.params;
    const personality = mockPersonalities.find(p => p.id === id);
    
    if (!personality) {
      return res.status(404).json({ error: "Personality not found" });
    }
    
    res.json(personality);
  });

  // Mock endpoint to create ads with either image or copy
  app.post("/ads", upload.single("image"), async (req, res) => {
    try {
      console.log("Request body:", req.body);
      console.log("Request file:", req.file);
      
      const copy = req.body.copy || "";
      
      // Validate request - either copy or image must be provided
      if (copy === "" && !req.file) {
        return res.status(400).json({ error: "Either copy or image is required" });
      }

      let imageUrl = null;
      if (req.file) {
        // Save the file locally
        const uploadsDir = await ensureUploadsDir();
        const filename = `${randomUUID()}${path.extname(req.file.originalname || ".jpg")}`;
        const filepath = path.join(uploadsDir, filename);
        
        await fs.writeFile(filepath, req.file.buffer);
        imageUrl = `/uploads/${filename}`;
      }
      
      // Generate a random UUID for the ad ID
      const adId = randomUUID();
      
      res.status(201).json(adId);
    } catch (error: any) {
      console.error("Error creating ad:", error.message);
      res.status(500).json({ error: "Failed to create ad" });
    }
  });

  // Mock endpoint to rate ads
  app.post("/rate", upload.single("image"), async (req, res) => {
    try {
      console.log("Rate request body:", req.body);
      console.log("Rate request file:", req.file);
      
      const personality_ids = req.body.personality_ids || "";
      
      // Validate request
      if (!req.file) {
        return res.status(400).json({ error: "Image is required for rating" });
      }
      
      if (!personality_ids) {
        return res.status(400).json({ error: "At least one personality must be selected" });
      }

      let imageUrl = null;
      if (req.file) {
        // Save the file locally
        const uploadsDir = await ensureUploadsDir();
        const filename = `${randomUUID()}${path.extname(req.file.originalname || ".jpg")}`;
        const filepath = path.join(uploadsDir, filename);
        
        await fs.writeFile(filepath, req.file.buffer);
        imageUrl = `/uploads/${filename}`;
      }
      
      // Generate mock ratings for the selected personalities
      const personalityIdList = personality_ids.split(',');
      const adId = randomUUID();
      
      // Generate mock rating responses
      const ratings = personalityIdList.map((personalityId: string) => {
        const personality = mockPersonalities.find(p => p.id === personalityId);
        const isProfessional = personality?.personality_traits?.includes("Professional") || false;
        const isCreative = personality?.personality_traits?.includes("Creative") || false;
        const isCasual = personality?.personality_traits?.includes("Casual") || false;
        
        let thought = "";
        let emotional_response = "";
        let emotions = "";
        let effectiveness = "";
        
        if (isProfessional) {
          thought = "This ad effectively communicates the product's value proposition with a clean, professional aesthetic.";
          emotional_response = "Positively impressed by the design quality and messaging clarity.";
          emotions = "Interested, Confident, Respected";
          effectiveness = "Good Fit";
        } else if (isCreative) {
          thought = "The color palette is appealing, but the typography lacks originality. The composition could be more dynamic.";
          emotional_response = "Somewhat inspired but wanting more creative risks.";
          emotions = "Curious, Critical, Hopeful";
          effectiveness = "Neutral/Okay";
        } else if (isCasual) {
          thought = "Love how approachable this makes shopping feel! The style is exactly what I'm looking for.";
          emotional_response = "Excited about the possibility of purchasing these items.";
          emotions = "Happy, Excited, Eager";
          effectiveness = "Strong Match";
        } else {
          thought = "This advertisement is clear and informative, though it could be more engaging.";
          emotional_response = "Generally positive, but not entirely convinced.";
          emotions = "Interested, Thoughtful, Curious";
          effectiveness = "Neutral/Okay";
        }
        
        return {
          id: randomUUID(),
          personality: personalityId,
          ad: adId,
          thought,
          emotional_response,
          emotions,
          effectiveness
        };
      });
      
      const response = {
        ad_id: adId,
        ad: { 
          id: adId,
          image: imageUrl,
          copy: req.body.copy || null
        },
        ratings
      };
      
      res.json(response);
    } catch (error: any) {
      console.error("Error rating ad:", error.message);
      res.status(500).json({ error: "Failed to rate ad" });
    }
  });

  // Serve static files from the uploads directory
  app.use("/uploads", express.static(path.join(process.cwd(), "uploads")));

  // Legacy API endpoints that map to the new ones
  app.get("/api/personalities", (_req, res) => {
    // Return the mock personalities
    res.json(mockPersonalities);
  });

  app.post("/api/feedback", upload.single("image"), async (req, res) => {
    try {
      // This is a compatibility layer for the old API
      console.log("Legacy feedback request body:", req.body);
      console.log("Legacy feedback request file:", req.file);
      
      const description = req.body.description || "";
      const personalities = JSON.parse(req.body.personalities || "[]");
      
      if (!req.file && !description) {
        return res.status(400).json({ error: "Either description or image is required" });
      }
      
      if (!personalities.length) {
        return res.status(400).json({ error: "At least one personality must be selected" });
      }
      
      let imageUrl = null;
      if (req.file) {
        // Save the file locally
        const uploadsDir = await ensureUploadsDir();
        const filename = `${randomUUID()}${path.extname(req.file.originalname || ".jpg")}`;
        const filepath = path.join(uploadsDir, filename);
        
        await fs.writeFile(filepath, req.file.buffer);
        imageUrl = `/uploads/${filename}`;
      }
      
      // Generate mock ratings for the selected personalities
      const adId = randomUUID();
      
      // Generate mock rating responses similar to the /rate endpoint
      const ratings = personalities.map((personalityId: string) => {
        const personality = mockPersonalities.find(p => p.id === personalityId);
        const isProfessional = personality?.personality_traits?.includes("Professional") || false;
        const isCreative = personality?.personality_traits?.includes("Creative") || false;
        const isCasual = personality?.personality_traits?.includes("Casual") || false;
        
        let thought = "";
        let emotional_response = "";
        let emotions = "";
        let effectiveness = "";
        
        if (isProfessional) {
          thought = "This ad effectively communicates the product's value proposition with a clean, professional aesthetic.";
          emotional_response = "Positively impressed by the design quality and messaging clarity.";
          emotions = "Interested, Confident, Respected";
          effectiveness = "Good Fit";
        } else if (isCreative) {
          thought = "The color palette is appealing, but the typography lacks originality. The composition could be more dynamic.";
          emotional_response = "Somewhat inspired but wanting more creative risks.";
          emotions = "Curious, Critical, Hopeful";
          effectiveness = "Neutral/Okay";
        } else if (isCasual) {
          thought = "Love how approachable this makes shopping feel! The style is exactly what I'm looking for.";
          emotional_response = "Excited about the possibility of purchasing these items.";
          emotions = "Happy, Excited, Eager";
          effectiveness = "Strong Match";
        } else {
          thought = "This advertisement is clear and informative, though it could be more engaging.";
          emotional_response = "Generally positive, but not entirely convinced.";
          emotions = "Interested, Thoughtful, Curious";
          effectiveness = "Neutral/Okay";
        }
        
        return {
          id: randomUUID(),
          personality: personalityId,
          ad: adId,
          thought,
          emotional_response,
          emotions,
          effectiveness
        };
      });
      
      const response = {
        ad_id: adId,
        ad: { 
          id: adId,
          image: imageUrl,
          copy: description
        },
        ratings
      };
      
      res.json(response);
    } catch (error: any) {
      console.error("Error in legacy feedback endpoint:", error.message);
      res.status(500).json({ error: "Failed to process feedback request" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
