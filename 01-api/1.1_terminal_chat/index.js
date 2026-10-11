import "dotenv/config";
import { GoogleGenAI } from "@google/genai";
import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
  console.error("Error: GEMINI_API_KEY is missing from .env");
  process.exit(1);
}

const ai = new GoogleGenAI({ apiKey });

const rl = readline.createInterface({ input, output });

async function main() {
  console.log("=== AI Assistant ===");
  console.log("Ask any question. Type 'exit or q' to quit.\n");

  try {
    while (true) {
      const question = await rl.question("You: ");

      if (question.trim().toLowerCase() === "exit"|| question.trim().toLowerCase() === "q") {
        console.log("AI: ok bye!");
        break;
      }

      if (!question.trim()) {
        console.log("Please enter a question.\n");
        continue;
      }

      try {
        console.log("\nAI is thinking...\n");

        const response = await ai.models.generateContent({
          model: process.env.GEMINI_MODEL || "gemini-2.5-flash",
          contents: question
        });

        console.log("AI:", response.text || "No text response received.");
        console.log();
      } catch (error) {
        console.error("AI request failed:", error.message);
        console.log();
      }
    }
  } finally {
    rl.close();
  }
}

main().catch(console.error);