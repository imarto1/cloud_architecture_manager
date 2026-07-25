import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { ArchitectureGallery } from "./components/ArchitectureGallery";
import { Hero } from "./components/Hero";
import { RecommendationForm } from "./components/RecommendationForm";
import { RecommendationResults } from "./components/RecommendationResults";
import {
  initialPreferences,
} from "./recommendationData";
import type {
  FieldName,
  Preferences,
  Recommendation,
  SavedArchitecture,
} from "./recommendationData";
import { GlobalStyle, Page } from "./ui";

function App() {
  const [showForm, setShowForm] = useState(false);
  const [preferences, setPreferences] = useState<Preferences>(initialPreferences);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [architectures, setArchitectures] = useState<SavedArchitecture[]>([]);
  const [isGalleryLoading, setIsGalleryLoading] = useState(true);
  const [galleryError, setGalleryError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const request = new AbortController();

    async function loadArchitectures() {
      try {
        const response = await fetch("/architectures", {
          signal: request.signal,
        });
        if (!response.ok) {
          throw new Error("The architecture gallery is unavailable right now.");
        }
        setArchitectures(await response.json() as SavedArchitecture[]);
      } catch (requestError) {
        if (!request.signal.aborted) {
          setGalleryError(
            requestError instanceof Error
              ? requestError.message
              : "The architecture gallery is unavailable right now.",
          );
        }
      } finally {
        if (!request.signal.aborted) {
          setIsGalleryLoading(false);
        }
      }
    }

    loadArchitectures();
    return () => request.abort();
  }, []);

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
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Something went wrong.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  function updatePreference<Field extends FieldName>(
    field: Field,
    value: Preferences[Field],
  ) {
    setPreferences((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function returnToMainScreen() {
    setRecommendations([]);
    setShowForm(false);
    setError(null);
  }

  const hasRecommendations = recommendations.length > 0;

  return (
    <>
      <GlobalStyle />
      <Page>
        <Hero
          hidden={hasRecommendations}
          showForm={showForm}
          onStart={() => setShowForm(true)}
        />

        {!showForm && !hasRecommendations && (
          <ArchitectureGallery
            architectures={architectures}
            isLoading={isGalleryLoading}
            error={galleryError}
          />
        )}

        {showForm && (
          <RecommendationForm
            preferences={preferences}
            hidden={hasRecommendations}
            isLoading={isLoading}
            error={error}
            onChange={updatePreference}
            onSubmit={submitPreferences}
          />
        )}

        {hasRecommendations && (
          <RecommendationResults
            recommendations={recommendations}
            onReturn={returnToMainScreen}
          />
        )}
      </Page>
    </>
  );
}

export default App;
