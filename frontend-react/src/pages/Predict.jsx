import { useEffect, useState } from "react";
import { fetchSymptoms, predictDeficiencies, apiErrorMessage } from "../api/client";

const RANK_LABELS = ["Most likely", "Also consider", "Worth noting"];

export default function Predict() {
  const [allSymptoms, setAllSymptoms] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSymptoms()
      .then(setAllSymptoms)
      .catch((err) => setError(apiErrorMessage(err)));
  }, []);

  function toggle(symptom) {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(symptom) ? next.delete(symptom) : next.add(symptom);
      return next;
    });
  }

  async function handlePredict() {
    setError("");
    setResults(null);
    setLoading(true);
    try {
      const data = await predictDeficiencies([...selected]);
      setResults(data);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="text-3xl">Select your symptoms</h1>
      <p className="mt-2 text-ink/70">Choose everything that applies — the more you select, the sharper the read.</p>

      <div className="mt-8 flex flex-wrap gap-2">
        {allSymptoms.map((symptom) => {
          const active = selected.has(symptom);
          return (
            <button
              key={symptom}
              onClick={() => toggle(symptom)}
              className={`rounded-full border px-3.5 py-1.5 text-sm transition-colors ${
                active
                  ? "border-amber bg-amber text-paper"
                  : "border-line bg-white text-ink/80 hover:border-teal"
              }`}
            >
              {symptom.replaceAll("_", " ")}
            </button>
          );
        })}
      </div>

      <button
        onClick={handlePredict}
        disabled={selected.size === 0 || loading}
        className="mt-8 rounded bg-ink px-6 py-3 font-medium text-paper hover:bg-teal transition-colors disabled:opacity-40"
      >
        {loading ? "Analyzing..." : `Check ${selected.size || ""} symptom${selected.size === 1 ? "" : "s"}`.trim()}
      </button>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      {results && (
        <div className="fade-in mt-12 space-y-10 border-t border-line pt-10">
          {results.predictions.map((pred, i) => (
            <article key={pred.nutrient}>
              <p className="text-xs uppercase tracking-wide text-teal">
                {RANK_LABELS[i] || `Option ${i + 1}`}
              </p>
              <h2 className="mt-1 text-2xl">
                {pred.nutrient} <span className="text-ink/40 text-base">{Math.round(pred.confidence * 100)}%</span>
              </h2>

              <p className="mt-3 text-sm text-ink/70">
                <span className="font-medium text-ink">Foods to try: </span>
                {pred.recommended_foods.slice(0, 6).join(", ")}
              </p>

              {pred.recipes.length > 0 && (
                <ul className="mt-3 flex flex-wrap gap-3">
                  {pred.recipes.map((recipe) => (
                    <li key={recipe.url}>
                      <a
                        href={recipe.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-sm text-teal underline underline-offset-2 hover:text-amber"
                      >
                        {recipe.title}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
