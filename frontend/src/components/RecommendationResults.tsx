import { faCrown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { keyframes, styled } from "styled-components";

import type { Recommendation } from "../recommendationData";
import { humanize } from "../recommendationData";
import { SecondaryButton } from "../ui";

type RecommendationResultsProps = {
  recommendations: Recommendation[];
  onReturn: () => void;
};

const resultsEnter = keyframes`
  from {
    opacity: 0;
    transform: translateY(1rem);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const cardEnter = keyframes`
  from {
    opacity: 0;
    transform: translateY(2.5rem) scale(0.96);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
`;

const crownCelebration = keyframes`
  0%,
  100% {
    filter: brightness(1) drop-shadow(0 0 0.35rem rgb(245 196 81 / 45%));
    transform: translateX(-50%) translateY(0) rotate(-2deg);
  }

  50% {
    filter: brightness(1.3) drop-shadow(0 0 0.85rem rgb(255 232 146 / 85%));
    transform: translateX(-50%) translateY(-0.35rem) rotate(2deg);
  }
`;

const ResultsSection = styled.section`
  width: 100%;
  max-width: 84rem;
  margin: 3rem auto 0;
  padding: 3rem;
  border: 1px solid #2a3b57;
  border-radius: 1rem;
  background: #111f35;
  text-align: center;
  animation: ${resultsEnter} 500ms ease-out 525ms both;

  h2 {
    font-size: clamp(1.75rem, 3vw, 2.5rem);
    transform: translateY(-0.5rem);
  }

  @media (max-width: 44rem) {
    padding: 1.5rem;
  }

  @media (prefers-reduced-motion: reduce) {
    animation: none;
  }
`;

const Podium = styled.div`
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  align-items: end;
  gap: 1.5rem;
  margin: 4.75rem 0 0;

  @media (max-width: 44rem) {
    grid-template-columns: 1fr;
  }
`;

const ResultCard = styled.article<{ $overall: boolean; $rank: number }>`
  position: relative;
  display: flex;
  grid-column: ${({ $overall, $rank }) => {
    if ($overall) return "2";
    if ($rank === 2) return "1";
    return "3";
  }};
  grid-row: 1;
  min-height: ${({ $overall, $rank }) => {
    if ($overall) return "24rem";
    if ($rank === 3) return "16rem";
    return "19rem";
  }};
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  border: ${({ $overall }) => ($overall ? "2px solid #69d2e7" : "0")};
  border-radius: 0.75rem;
  background: ${({ $overall }) => ($overall ? "#193653" : "#172944")};
  box-shadow: ${({ $overall }) =>
    $overall ? "0 0 2.5rem rgb(105 210 231 / 18%)" : "none"};
  text-align: center;
  animation: ${cardEnter} 750ms cubic-bezier(0.2, 0.8, 0.2, 1) both;
  animation-delay: ${({ $rank }) => {
    if ($rank === 1) return "800ms";
    if ($rank === 2) return "650ms";
    return "950ms";
  }};

  p {
    color: #b8c5d9;
  }

  @media (max-width: 44rem) {
    grid-column: auto;
    grid-row: auto;
    min-height: auto;
  }

  @media (prefers-reduced-motion: reduce) {
    animation: none;
  }
`;

const Rank = styled.span<{ $rank: number }>`
  position: absolute;
  top: -1.2rem;
  left: 50%;
  display: grid;
  width: 2.4rem;
  height: 2.4rem;
  place-items: center;
  border-radius: 50%;
  color: #07101f;
  background: ${({ $rank }) => {
    if ($rank === 1) return "#f5c451";
    if ($rank === 2) return "#c3cad4";
    return "#c87c45";
  }};
  box-shadow: ${({ $rank }) => {
    if ($rank === 1) return "0 0 1rem rgb(245 196 81 / 45%)";
    if ($rank === 2) return "0 0 1rem rgb(195 202 212 / 30%)";
    return "0 0 1rem rgb(200 124 69 / 30%)";
  }};
  font-weight: 800;
  transform: translateX(-50%);
`;

const Crown = styled(FontAwesomeIcon)`
  position: absolute;
  top: -3.6rem;
  left: 50%;
  color: #f5c451;
  font-size: 2rem;
  line-height: 1;
  text-shadow: 0 0 1rem rgb(245 196 81 / 55%);
  transform: translateX(-50%);
  animation: ${crownCelebration} 4s ease-in-out infinite;
  will-change: filter, transform;

  @media (prefers-reduced-motion: reduce) {
    animation: none;
  }
`;

const RecommendationType = styled.p`
  color: #69d2e7 !important;
  font-weight: 700;
  text-transform: capitalize;
`;

const MatchScore = styled(RecommendationType)``;

export function RecommendationResults({
  recommendations,
  onReturn,
}: RecommendationResultsProps) {
  return (
    <ResultsSection
      aria-live="polite"
      aria-labelledby="results-title"
    >
      <h2 id="results-title">Your recommended architectures</h2>
      <Podium>
        {recommendations.map((recommendation, index) => {
          const rank = index + 1;
          const isOverall =
            recommendation.recommendation_type === "best_overall_match";

          return (
            <ResultCard
              $overall={isOverall}
              $rank={rank}
              key={recommendation.architecture_id}
            >
              {rank === 1 && <Crown icon={faCrown} aria-hidden="true" />}
              <Rank $rank={rank} aria-label={`Rank ${rank}`}>
                {rank}
              </Rank>
              <RecommendationType>
                {humanize(recommendation.recommendation_type)}
              </RecommendationType>
              <h3>{recommendation.name}</h3>
              <p>{recommendation.reason}</p>
              <MatchScore>
                {Math.round(recommendation.match_score * 100)}% match
              </MatchScore>
            </ResultCard>
          );
        })}
      </Podium>
      <SecondaryButton type="button" onClick={onReturn}>
        Return to main screen
      </SecondaryButton>
    </ResultsSection>
  );
}
