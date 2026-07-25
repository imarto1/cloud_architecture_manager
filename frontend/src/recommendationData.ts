export const options = {
  use_case: [
    "web_application",
    "public_api",
    "ecommerce",
    "real_time_analytics",
    "batch_processing",
    "event_processing",
    "media_delivery",
    "internal_tool",
    "iot_ingestion",
    "ml_inference",
  ],
  scale: ["small", "medium", "large"],
  traffic_pattern: ["steady", "bursty", "spiky", "scheduled", "unpredictable"],
  latency_sensitivity: ["low", "medium", "high"],
  processing_style: ["request_response", "event_driven", "batch", "streaming"],
  data_intensity: ["low", "medium", "high"],
  availability_requirement: ["standard", "high", "critical"],
  ops_preference: ["managed_services", "balanced", "self_managed_ok"],
  budget_sensitivity: ["low", "medium", "high"],
} as const;

export type FieldName = keyof typeof options;
export type Preferences = {
  [Field in FieldName]: (typeof options)[Field][number];
};

export type Recommendation = {
  architecture_id: string;
  name: string;
  match_score: number;
  recommendation_type: string;
  reason: string;
};

export type SavedArchitecture = {
  id: string;
  name: string;
  scale: string;
  traffic_pattern: string;
  processing_style: string;
  availability_requirement: string;
  ops_preference: string;
};

export const initialPreferences: Preferences = {
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

export const fieldLabels: Record<FieldName, string> = {
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

export function humanize(value: string) {
  return value.replaceAll("_", " ");
}
