
import { useState } from "react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setResult(null);
    setError("");

    if (!text.trim()) {
      setError("Please enter a sentence.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Prediction failed.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Could not reach the backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1 className="title">Sentiment Finder</h1>
      <p>Analyze a sentence using your hosted DistilBERT model.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="sentence">Your sentence</label>
        <textarea
          id="sentence"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="I love learning artificial intelligence."
          maxLength={5000}
          rows={5}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Analyze sentiment"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <section className="result" aria-live="polite">
          <h2 className="result-title">Prediction: {result.label}</h2>
          <p>Model score: {(result.score * 100).toFixed(2)}%</p>
          <p className="note">
            The score indicates model confidence, not a guarantee of accuracy.
          </p>
        </section>
      )}
    </main>
  );
}

export default App;
