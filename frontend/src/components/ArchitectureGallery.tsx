import { keyframes, styled } from "styled-components";

import { useLoopingScroll } from "../hooks/useLoopingScroll";
import type { SavedArchitecture } from "../recommendationData";
import { humanize } from "../recommendationData";
import { Eyebrow } from "../ui";

interface ArchitectureGalleryProps {
  architectures: SavedArchitecture[];
  isLoading: boolean;
  error: string | null;
}

const galleryEnter = keyframes`
  from {
    opacity: 0;
    transform: translateY(1.5rem);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const GallerySection = styled.section`
  max-width: 84rem;
  margin: 5rem auto 0;
  animation: ${galleryEnter} 700ms ease-out both;

  @media (prefers-reduced-motion: reduce) {
    animation: none;
  }
`;

const GalleryHeading = styled.div`
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 2rem;
  margin-bottom: 1.5rem;

  h2 {
    margin: 0.5rem 0 0;
    font-size: clamp(1.75rem, 3vw, 2.5rem);
  }

  @media (max-width: 44rem) {
    align-items: start;
    flex-direction: column;
    gap: 0.75rem;
  }
`;

const GalleryCount = styled.span`
  flex: none;
  color: #b8c5d9;
`;

const GalleryTrack = styled.div`
  display: flex;
  width: max-content;
`;

const GalleryWindow = styled.div`
  width: 100%;
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  scrollbar-width: none;
  mask-image: linear-gradient(to right, transparent, black 4%, black 96%, transparent);

  &::-webkit-scrollbar {
    display: none;
  }

  @media (prefers-reduced-motion: reduce) {
    mask-image: none;
  }
`;

const GalleryGroup = styled.div<{ $duplicate: boolean }>`
  display: flex;
  gap: 1rem;
  padding-right: 1rem;

  @media (prefers-reduced-motion: reduce) {
    display: ${({ $duplicate }) => ($duplicate ? "none" : "flex")};
  }
`;

const ArchitectureCard = styled.article`
  flex: 0 0 18rem;
  padding: 1.5rem;
  border: 1px solid #2a3b57;
  border-radius: 0.75rem;
  background: #111f35;
  transition:
    border-color 250ms ease,
    box-shadow 250ms ease;

  &:hover {
    border-color: #3b6680;
    box-shadow: 0 1rem 2rem rgb(0 0 0 / 18%);
  }

  h3 {
    color: #e6edf7;
    font-size: 1.15rem;
  }

  dl {
    display: grid;
    gap: 0.7rem;
    margin: 0;
  }

  dl div {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding-top: 0.7rem;
    border-top: 1px solid #223451;
  }

  dt {
    color: #8190a8;
  }

  dd {
    margin: 0;
    color: #b8c5d9;
    text-align: right;
    text-transform: capitalize;
  }

  @media (prefers-reduced-motion: reduce) {
    transition: none;
  }
`;

const GalleryStatus = styled.p<{ $error?: boolean }>`
  padding: 2rem;
  border: 1px dashed #3b5072;
  border-radius: 0.75rem;
  color: ${({ $error }) => ($error ? "#ff9b9b" : "#b8c5d9")};
  text-align: center;
`;

function ArchitectureCards({
  architectures,
  duplicate,
}: {
  architectures: SavedArchitecture[];
  duplicate: boolean;
}) {
  return (
    <GalleryGroup $duplicate={duplicate} aria-hidden={duplicate}>
      {architectures.map((architecture) => (
        <ArchitectureCard
          key={`${duplicate ? "duplicate" : "original"}-${architecture.id}`}
        >
          <h3>{architecture.name}</h3>
          <dl>
            <div>
              <dt>Scale</dt>
              <dd>{humanize(architecture.scale)}</dd>
            </div>
            <div>
              <dt>Traffic</dt>
              <dd>{humanize(architecture.traffic_pattern)}</dd>
            </div>
            <div>
              <dt>Processing</dt>
              <dd>{humanize(architecture.processing_style)}</dd>
            </div>
            <div>
              <dt>Availability</dt>
              <dd>{humanize(architecture.availability_requirement)}</dd>
            </div>
            <div>
              <dt>Operations</dt>
              <dd>{humanize(architecture.ops_preference)}</dd>
            </div>
          </dl>
        </ArchitectureCard>
      ))}
    </GalleryGroup>
  );
}

export function ArchitectureGallery({
  architectures,
  isLoading,
  error,
}: ArchitectureGalleryProps) {
  const galleryWindow = useLoopingScroll(architectures.length);

  return (
    <GallerySection aria-labelledby="gallery-title">
      <GalleryHeading>
        <div>
          <Eyebrow>Saved architectures</Eyebrow>
          <h2 id="gallery-title">Explore the architecture gallery</h2>
        </div>
        {!isLoading && !error && (
          <GalleryCount>
            {architectures.length}{" "}
            {architectures.length === 1 ? "architecture" : "architectures"}
          </GalleryCount>
        )}
      </GalleryHeading>

      {isLoading && <GalleryStatus>Loading architectures...</GalleryStatus>}
      {error && (
        <GalleryStatus $error role="status">
          {error}
        </GalleryStatus>
      )}
      {!isLoading && !error && architectures.length === 0 && (
        <GalleryStatus>No architectures have been saved yet.</GalleryStatus>
      )}

      {architectures.length > 0 && (
        <GalleryWindow ref={galleryWindow}>
          <GalleryTrack>
            <ArchitectureCards architectures={architectures} duplicate={false} />
            <ArchitectureCards architectures={architectures} duplicate />
          </GalleryTrack>
        </GalleryWindow>
      )}
    </GallerySection>
  );
}
