import { useState } from "react";
import "./App.css";

export default function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    const text = question.trim();

    if (!text || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", text }
    ]);

    setQuestion("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: text })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "AI request failed");
      }

      setMessages((previous) => [
        ...previous,
        { role: "ai", text: data.answer }
      ]);
    } catch (err) {
      setError(err.message || "Could not connect to backend");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header>
        <h1>AI Assistant</h1>
        <p>React + Express + Gemini</p>
      </header>

      <section className="chat" aria-live="polite">
        {messages.length === 0 && (
          <p className="empty">Ask your first question.</p>
        )}

        {messages.map((message, index) => (
          <article
            key={index}
            className={`message ${message.role}`}
          >
            <strong>
              {message.role === "user" ? "You" : "AI"}
            </strong>
            <p>{message.text}</p>
          </article>
        ))}

        {loading && <p>AI is thinking...</p>}
        {error && <p className="error">{error}</p>}
      </section>

      <form onSubmit={handleSubmit}>
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask a question..."
          aria-label="Your question"
          maxLength={4000}
          disabled={loading}
        />

        <button disabled={loading || !question.trim()}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>
    </main>
  );
}