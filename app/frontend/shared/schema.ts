import { pgTable, text, serial, integer, array } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const personalities = pgTable("personalities", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  age: integer("age"),
  gender: text("gender"),
  location: text("location"),
  education_level: text("education_level"),
  marital_status: text("marital_status"),
  occupation: text("occupation"),
  job_title: text("job_title"),
  industry: text("industry"),
  income: text("income"),
  seniority_level: text("seniority_level"),
  personality_traits: array(text("personality_traits")),
  values: array(text("values")),
  attitudes: array(text("attitudes")),
  interests: array(text("interests")),
  lifestyle: text("lifestyle"),
  habits: text("habits"),
  frustrations: text("frustrations"),
  summary: text("summary"),
});

export const adFeedback = pgTable("ad_feedback", {
  id: serial("id").primaryKey(),
  description: text("description"), // No longer required
  image_url: text("image_url"),
  personality_ids: array(text("personality_ids")).notNull(),
  created_at: text("created_at").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertPersonalitySchema = createInsertSchema(personalities);

export const insertAdFeedbackSchema = createInsertSchema(adFeedback).pick({
  description: true,
  image_url: true,
  personality_ids: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

export type Personality = typeof personalities.$inferSelect;
export type InsertPersonality = z.infer<typeof insertPersonalitySchema>;

export type AdFeedback = typeof adFeedback.$inferSelect;
export type InsertAdFeedback = z.infer<typeof insertAdFeedbackSchema>;
