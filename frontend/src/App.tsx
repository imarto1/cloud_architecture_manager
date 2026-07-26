import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { getArchitectures, recommendArchitectures } from "./api";
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
        setArchitectures(await getArchitectures(request.signal));
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

    void loadArchitectures();
    return () => request.abort();
  }, []);

  async function submitPreferences(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      setRecommendations(await recommendArchitectures(preferences));
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

  function handlePreferenceSubmit(event: FormEvent<HTMLFormElement>) {
    void submitPreferences(event);
  }

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
            onSubmit={handlePreferenceSubmit}
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
