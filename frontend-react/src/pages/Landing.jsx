import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Landing() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="mx-auto max-w-prose px-6 py-20">
      <p className="mb-3 text-sm text-teal">A symptom-based nutrient log</p>
      <h1 className="text-4xl leading-tight sm:text-5xl">
        What your body might be asking for.
      </h1>
      <p className="mt-6 text-lg text-ink/80">
        Select what you've been feeling, and a Random Forest model trained on
        symptom patterns will suggest which nutrients you may be low on —
        along with foods and real recipes to help.
      </p>
      <p className="mt-6 text-sm text-ink/60">
        Educational project, not medical advice. Persistent, unexplained
        symptoms are worth a real conversation with a doctor.
      </p>
      <Link
        to={isAuthenticated ? "/predict" : "/register"}
        className="mt-10 inline-block rounded bg-amber px-6 py-3 font-medium text-paper hover:bg-ink transition-colors"
      >
        {isAuthenticated ? "Check your symptoms" : "Get started"}
      </Link>
    </div>
  );
}
