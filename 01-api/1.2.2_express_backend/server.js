import "dotenv/config";
import express from "express";
import { GoogleGenAI } from "@google/genai";
import rateLimit from "express-rate-limit";

const app = express();
const PORT = 3000;

if (!process.env.GEMINI_API_KEY) {
  throw new Error("GEMINI_API_KEY is missing from .env");
}

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY
});

app.use(express.json({ limit: "10kb" }));

// Health-check endpoint
app.get("/", (req, res) => {
  res.json({
    message: "AI backend is running"
  });
});

const askLimiter = rateLimit({
  windowMs: 60 * 1000,
  limit: 10,
  standardHeaders: "draft-8",
  legacyHeaders: false,
  message: {
    error: "Too many requests. Please try again later."
  }
});
// AI question endpoint
app.post("/api/ask", askLimiter, async (req, res) => {
  const { question } = req.body ?? {};

  if (
    typeof question !== "string" ||
    question.trim().length === 0 ||
    question.length > 4000
  ) {
    return res.status(400).json({
      error: "Provide a question between 1 and 4000 characters."
    });
  }

  try {
    const response = await ai.models.generateContent({
      model: process.env.GEMINI_MODEL || "gemini-2.5-flash",
      contents: question.trim()
    });

    if (!response.text) {
      return res.status(502).json({
        error: "The AI returned no text response."
      });
    }

    return res.json({
      question,
      answer: response.text
    });
  } catch (error) {
    console.error("AI request failed:", error.message);

    return res.status(502).json({
      error: "Unable to get an answer from the AI service."
    });
  }
});

app.listen(PORT, "127.0.0.1", () => {
  console.log(`AI backend running at http://127.0.0.1:${PORT}`);
});
