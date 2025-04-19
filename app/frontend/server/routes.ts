import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { z } from "zod";
import multer from "multer";
import path from "path";
import fs from "fs/promises";
import { randomUUID } from "crypto";

// Configure multer storage
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

export async function registerRoutes(app: Express): Promise<Server> {
  // API endpoint to get all personalities
  app.get("/api/personalities", async (_req, res) => {
    try {
      const personalities = await storage.getAllPersonalities();
      res.json(personalities);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch personalities" });
    }
  });

  // API endpoint to submit ad feedback
  app.post("/api/feedback", upload.single("image"), async (req, res) => {
    try {
      console.log("Request body:", req.body);
      console.log("Request file:", req.file);
      
      const description = req.body.description || "";
      const personalities = JSON.parse(req.body.personalities || "[]");
      
      // Validate request
      if (description === "" && !req.file) {
        return res.status(400).json({ error: "Either description or image is required" });
      }
      
      if (!personalities.length) {
        return res.status(400).json({ error: "At least one personality must be selected" });
      }

      let imageUrl = null;
      if (req.file) {
        const uploadsDir = await ensureUploadsDir();
        const filename = `${randomUUID()}${path.extname(req.file.originalname)}`;
        const filepath = path.join(uploadsDir, filename);
        
        await fs.writeFile(filepath, req.file.buffer);
        imageUrl = `/uploads/${filename}`;
      }

      // Create a new ad feedback entry
      const feedback = await storage.createAdFeedback({
        description,
        image_url: imageUrl,
        personality_ids: personalities,
        created_at: new Date().toISOString(),
      });

      res.status(201).json(feedback);
    } catch (error) {
      res.status(500).json({ error: "Failed to submit feedback request" });
    }
  });

  // Serve uploaded files
  app.use("/uploads", (req, res, next) => {
    express.static(path.join(process.cwd(), "uploads"))(req, res, next);
  });

  const httpServer = createServer(app);
  return httpServer;
}
