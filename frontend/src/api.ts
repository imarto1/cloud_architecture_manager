import type {
  Preferences,
  Recommendation,
  SavedArchitecture,
} from "./recommendationData";

async function requestJson<ResponseBody>(
  input: RequestInfo | URL,
  init: RequestInit,
  errorMessage: string,
): Promise<ResponseBody> {
  const response = await fetch(input, init);
  if (!response.ok) {
    throw new Error(errorMessage);
  }
  return response.json() as Promise<ResponseBody>;
}

export function getArchitectures(
  signal: AbortSignal,
): Promise<SavedArchitecture[]> {
  return requestJson(
    "/architectures",
    { signal },
    "The architecture gallery is unavailable right now.",
  );
}

export function recommendArchitectures(
  preferences: Preferences,
): Promise<Recommendation[]> {
  return requestJson(
    "/architectures/recommendations",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(preferences),
    },
    "We could not find recommendations right now.",
  );
}
