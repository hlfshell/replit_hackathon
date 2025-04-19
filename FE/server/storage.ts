import { 
  users, type User, type InsertUser, 
  personalities, type Personality, type InsertPersonality,
  adFeedback, type AdFeedback, type InsertAdFeedback
} from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // Personality methods
  getAllPersonalities(): Promise<Personality[]>;
  getPersonality(id: string): Promise<Personality | undefined>;
  createPersonality(personality: InsertPersonality): Promise<Personality>;
  
  // Ad Feedback methods
  createAdFeedback(feedback: InsertAdFeedback): Promise<AdFeedback>;
  getAdFeedback(id: number): Promise<AdFeedback | undefined>;
  getAllAdFeedback(): Promise<AdFeedback[]>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private personalities: Map<string, Personality>;
  private adFeedbacks: Map<number, AdFeedback>;
  private userId: number;
  private adFeedbackId: number;

  constructor() {
    this.users = new Map();
    this.personalities = new Map();
    this.adFeedbacks = new Map();
    this.userId = 1;
    this.adFeedbackId = 1;
    
    // Initialize with some sample personalities
    this.initializePersonalities();
  }

  // User methods
  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.userId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  // Personality methods
  async getAllPersonalities(): Promise<Personality[]> {
    return Array.from(this.personalities.values());
  }

  async getPersonality(id: string): Promise<Personality | undefined> {
    return this.personalities.get(id);
  }

  async createPersonality(personality: InsertPersonality): Promise<Personality> {
    const id = personality.id || randomUUID();
    const newPersonality: Personality = { ...personality, id };
    this.personalities.set(id, newPersonality);
    return newPersonality;
  }

  // Ad Feedback methods
  async createAdFeedback(feedback: InsertAdFeedback): Promise<AdFeedback> {
    const id = this.adFeedbackId++;
    const newFeedback: AdFeedback = { ...feedback, id };
    this.adFeedbacks.set(id, newFeedback);
    return newFeedback;
  }

  async getAdFeedback(id: number): Promise<AdFeedback | undefined> {
    return this.adFeedbacks.get(id);
  }

  async getAllAdFeedback(): Promise<AdFeedback[]> {
    return Array.from(this.adFeedbacks.values());
  }

  private initializePersonalities() {
    const samplePersonalities: InsertPersonality[] = [
      {
        id: "p1",
        name: "Emma Johnson",
        age: 32,
        gender: "Female",
        location: "New York, NY",
        occupation: "Marketing Specialist",
        job_title: "Digital Marketing Manager",
        industry: "Technology",
        personality_traits: ["Professional", "Creative", "Analytical"],
        summary: "Digital marketing specialist who values authenticity and innovation in advertising."
      },
      {
        id: "p2",
        name: "Alex Chen",
        age: 28,
        gender: "Male",
        location: "San Francisco, CA",
        occupation: "UX Designer",
        job_title: "Senior UX Designer",
        industry: "Software",
        personality_traits: ["Creative", "Detail-oriented", "User-focused"],
        summary: "User experience designer focused on accessibility and intuitive interfaces."
      },
      {
        id: "p3",
        name: "Sarah Williams",
        age: 45,
        gender: "Female",
        location: "Chicago, IL",
        occupation: "Senior Manager",
        job_title: "Finance Director",
        industry: "Finance",
        personality_traits: ["Professional", "Serious", "Detail-oriented"],
        summary: "Conservative decision-maker who appreciates data-driven marketing approaches."
      },
      {
        id: "p4",
        name: "Michael Rodriguez",
        age: 39,
        gender: "Male",
        location: "Austin, TX",
        occupation: "Small Business Owner",
        job_title: "CEO",
        industry: "Retail",
        personality_traits: ["Practical", "Enthusiastic", "Value-conscious"],
        summary: "Practical entrepreneur looking for cost-effective marketing solutions with proven ROI."
      },
      {
        id: "p5",
        name: "Jamal Foster",
        age: 24,
        gender: "Male",
        location: "Portland, OR",
        occupation: "Content Creator",
        job_title: "Social Media Influencer",
        industry: "Entertainment",
        personality_traits: ["Creative", "Humorous", "Trendsetting"],
        summary: "Trendsetting content creator who values authenticity and social impact in brand messaging."
      },
      {
        id: "p6",
        name: "Lisa Patel",
        age: 36,
        gender: "Female",
        location: "Seattle, WA",
        occupation: "IT Professional",
        job_title: "Systems Architect",
        industry: "Technology",
        personality_traits: ["Technical", "Analytical", "Practical"],
        summary: "Tech-savvy professional who appreciates straightforward, fact-based advertising."
      },
      {
        id: "p7",
        name: "David Kim",
        age: 41,
        gender: "Male",
        location: "Boston, MA",
        occupation: "Professor",
        job_title: "Associate Professor of Marketing",
        industry: "Education",
        personality_traits: ["Analytical", "Formal", "Detail-oriented"],
        summary: "Academic with a critical eye for marketing claims and evidence-based messaging."
      },
      {
        id: "p8",
        name: "Maria Gonzalez",
        age: 29,
        gender: "Female",
        location: "Miami, FL",
        occupation: "Healthcare Worker",
        job_title: "Registered Nurse",
        industry: "Healthcare",
        personality_traits: ["Compassionate", "Practical", "Serious"],
        summary: "Healthcare professional who responds to emotional appeals and social impact messaging."
      },
      {
        id: "p9",
        name: "Robert Johnson",
        age: 52,
        gender: "Male",
        location: "Denver, CO",
        occupation: "Construction Manager",
        job_title: "Site Supervisor",
        industry: "Construction",
        personality_traits: ["Practical", "Direct", "Traditional"],
        summary: "No-nonsense professional who values straightforward, practical advertising."
      },
      {
        id: "p10",
        name: "Jennifer Wu",
        age: 33,
        gender: "Female",
        location: "Los Angeles, CA",
        occupation: "Art Director",
        job_title: "Creative Director",
        industry: "Advertising",
        personality_traits: ["Creative", "Enthusiastic", "Trendsetting"],
        summary: "Visual creative who appreciates innovative design and bold brand statements."
      }
    ];

    samplePersonalities.forEach(personality => {
      this.personalities.set(personality.id!, {
        ...personality,
        id: personality.id!
      });
    });
  }
}

export const storage = new MemStorage();
