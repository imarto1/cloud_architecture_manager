import { faCrown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import type { FormEvent } from "react";

const options = {
  use_case: ["web_application", "public_api", "ecommerce", "real_time_analytics", "batch_processing", "event_processing", "media_delivery", "internal_tool", "iot_ingestion", "ml_inference"],
  scale: ["small", "medium", "large"],
  traffic_pattern: ["steady", "bursty", "spiky", "scheduled", "unpredictable"],
  latency_sensitivity: ["low", "medium", "high"],
  processing_style: ["request_response", "event_driven", "batch", "streaming"],
  data_intensity: ["low", "medium", "high"],
  availability_requirement: ["standard", "high", "critical"],
  ops_preference: ["managed_services", "balanced", "self_managed_ok"],
  budget_sensitivity: ["low", "medium", "high"],
} as const;

type FieldName = keyof typeof options;
type Preferences = { [Field in FieldName]: (typeof options)[Field][number] };

type Recommendation = {
  architecture_id: string;
  name: string;
  match_score: number;
  recommendation_type: string;
  reason: string;
};

const initialPreferences: Preferences = {
  use_case: "web_application",
  scale: "medium",
  traffic_pattern: "steady",
  latency_sensitivity: "medium",
  processing_style: "request_response",
  data_intensity: "medium",
  availability_requirement: "high",
  ops_preference: "balanced",
  budget_sensitivity: "medium",
};

const fieldLabels: Record<FieldName, string> = {
  use_case: "Use case",
  scale: "Expected scale",
  traffic_pattern: "Traffic pattern",
  latency_sensitivity: "Latency sensitivity",
  processing_style: "Processing style",
  data_intensity: "Data intensity",
  availability_requirement: "Availability requirement",
  ops_preference: "Operations preference",
  budget_sensitivity: "Budget sensitivity",
};

function humanize(value: string) {
  return value.replaceAll("_", " ");
}

function App() {
  const [showForm, setShowForm] = useState(false);
  const [preferences, setPreferences] = useState<Preferences>(initialPreferences);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submitPreferences(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/architectures/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(preferences),
      });
      if (!response.ok) {
        throw new Error("We could not find recommendations right now.");
      }
      setRecommendations(await response.json() as Recommendation[]);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="page">
      <section
        className={`hero ${recommendations.length > 0 ? "hero--hidden" : ""}`}
        aria-labelledby="page-title"
        aria-hidden={recommendations.length > 0}
      >
        <p className="eyebrow">Cloud Architecture Manager</p>
        <h1 id="page-title">Find the right architecture for your workload.</h1>
        <p className="description">
          Tell us what you are building and we will rank the saved architectures
          against your needs.
        </p>
        {!showForm && (
          <button type="button" onClick={() => setShowForm(true)}>
            Find the right architecture for me
          </button>
        )}
      </section>

      {showForm && (
        <section
          className={`recommendation-panel ${
            recommendations.length > 0 ? "recommendation-panel--hidden" : ""
          }`}
          aria-labelledby="recommendation-title"
          aria-hidden={recommendations.length > 0}
        >
          <h2 id="recommendation-title">Describe your workload</h2>
          <form onSubmit={submitPreferences}>
            <div className="form-grid">
              {(Object.keys(options) as FieldName[]).map((field) => (
                <label key={field}>
                  {fieldLabels[field]}
                  <select
                    value={preferences[field]}
                    onChange={(event) => setPreferences({ ...preferences, [field]: event.target.value as Preferences[typeof field] })}
                  >
                    {options[field].map((option) => (
                      <option key={option} value={option}>{humanize(option)}</option>
                    ))}
                  </select>
                </label>
              ))}
            </div>
            <button type="submit" disabled={isLoading}>
              {isLoading ? "Finding matches..." : "Find architectures"}
            </button>
          </form>
          {error && <p className="error" role="alert">{error}</p>}
        </section>
      )}

      {recommendations.length > 0 && (
        <section className="results" aria-live="polite" aria-labelledby="results-title">
          <h2 id="results-title">Your recommended architectures</h2>
          <div className="podium">
            {recommendations.map((recommendation, index) => (
              <article
                className={`result-card ${
                  recommendation.recommendation_type === "best_overall_match"
                    ? "result-card--overall"
                    : "result-card--alternative"
                } result-card--rank-${index + 1}`}
                key={recommendation.architecture_id}
              >
                {index === 0 && (
                  <FontAwesomeIcon className="podium-crown" icon={faCrown} aria-hidden="true" />
                )}
                <span className="podium-rank" aria-label={`Rank ${index + 1}`}>
                  {index + 1}
                </span>
                <p className="recommendation-type">{humanize(recommendation.recommendation_type)}</p>
                <h3>{recommendation.name}</h3>
                <p>{recommendation.reason}</p>
                <p className="match-score">
                  {Math.round(recommendation.match_score * 100)}% match
                </p>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;
