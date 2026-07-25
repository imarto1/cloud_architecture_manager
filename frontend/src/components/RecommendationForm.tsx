import type { FormEventHandler } from "react";
import { keyframes, styled } from "styled-components";

import {
  fieldLabels,
  humanize,
  options,
} from "../recommendationData";
import type {
  FieldName,
  Preferences,
} from "../recommendationData";
import { ActionButton, ErrorMessage } from "../ui";

type RecommendationFormProps = {
  preferences: Preferences;
  hidden: boolean;
  isLoading: boolean;
  error: string | null;
  onChange: <Field extends FieldName>(
    field: Field,
    value: Preferences[Field],
  ) => void;
  onSubmit: FormEventHandler<HTMLFormElement>;
};

const panelEnter = keyframes`
  from {
    opacity: 0;
    transform: translateY(1rem) scale(0.98);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
`;

const panelExit = keyframes`
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }

  to {
    opacity: 0;
    transform: translateY(-1rem) scale(0.98);
  }
`;

const Panel = styled.section<{ $hidden: boolean }>`
  max-width: 70rem;
  max-height: ${({ $hidden }) => ($hidden ? "0" : "55rem")};
  margin-top: ${({ $hidden }) => ($hidden ? "0" : "3rem")};
  overflow: hidden;
  padding: ${({ $hidden }) => ($hidden ? "0 2rem" : "2rem")};
  border: ${({ $hidden }) => ($hidden ? "0" : "1px solid #2a3b57")};
  border-radius: 1rem;
  background: #111f35;
  pointer-events: ${({ $hidden }) => ($hidden ? "none" : "auto")};
  animation: ${({ $hidden }) => ($hidden ? panelExit : panelEnter)}
    ${({ $hidden }) => ($hidden ? "500ms ease-in" : "560ms ease-out")} both;
  transition:
    max-height 500ms ease,
    margin-top 500ms ease,
    padding 500ms ease,
    border-width 500ms ease;

  @media (prefers-reduced-motion: reduce) {
    animation: none;
    transition: none;
  }
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;

  @media (max-width: 44rem) {
    grid-template-columns: 1fr;
  }
`;

const FieldLabel = styled.label`
  display: grid;
  gap: 0.4rem;
  color: #b8c5d9;
  font-size: 0.9rem;
`;

const Select = styled.select`
  width: 100%;
  border: 1px solid #3b5072;
  border-radius: 0.5rem;
  padding: 0.65rem;
  color: #e6edf7;
  background: #0d1627;
  font: inherit;
`;

export function RecommendationForm({
  preferences,
  hidden,
  isLoading,
  error,
  onChange,
  onSubmit,
}: RecommendationFormProps) {
  return (
    <Panel
      $hidden={hidden}
      aria-labelledby="recommendation-title"
      aria-hidden={hidden}
    >
      <h2 id="recommendation-title">Describe your workload</h2>
      <form onSubmit={onSubmit}>
        <FormGrid>
          {(Object.keys(options) as FieldName[]).map((field) => (
            <FieldLabel key={field}>
              {fieldLabels[field]}
              <Select
                value={preferences[field]}
                onChange={(event) => {
                  onChange(
                    field,
                    event.target.value as Preferences[typeof field],
                  );
                }}
              >
                {options[field].map((option) => (
                  <option key={option} value={option}>
                    {humanize(option)}
                  </option>
                ))}
              </Select>
            </FieldLabel>
          ))}
        </FormGrid>
        <ActionButton type="submit" disabled={isLoading}>
          {isLoading ? "Finding matches..." : "Find architectures"}
        </ActionButton>
      </form>
      {error && <ErrorMessage role="alert">{error}</ErrorMessage>}
    </Panel>
  );
}
