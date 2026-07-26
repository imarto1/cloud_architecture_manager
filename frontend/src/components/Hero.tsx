import { styled } from "styled-components";

import { ActionButton, Eyebrow } from "../ui";

interface HeroProps {
  hidden: boolean;
  showForm: boolean;
  onStart: () => void;
}

const HeroSection = styled.section<{ $hidden: boolean }>`
  max-width: 42rem;
  max-height: ${({ $hidden }) => ($hidden ? "0" : "30rem")};
  visibility: ${({ $hidden }) => ($hidden ? "hidden" : "visible")};
  overflow: hidden;
  opacity: ${({ $hidden }) => ($hidden ? "0" : "1")};
  pointer-events: ${({ $hidden }) => ($hidden ? "none" : "auto")};
  transform: translateY(${({ $hidden }) => ($hidden ? "-1rem" : "0")});
  transition:
    max-height 560ms ease,
    opacity 320ms ease,
    transform 440ms ease,
    visibility 0s linear ${({ $hidden }) => ($hidden ? "560ms" : "0s")};

  @media (prefers-reduced-motion: reduce) {
    transition: none;
  }
`;

const Title = styled.h1`
  margin: 0.75rem 0;
  font-size: clamp(2.5rem, 8vw, 5rem);
  line-height: 1;
`;

const Description = styled.p`
  max-width: 34rem;
  margin: 0 0 1.5rem;
  color: #b8c5d9;
  font-size: 1.125rem;
  line-height: 1.6;
`;

export function Hero({ hidden, showForm, onStart }: HeroProps) {
  return (
    <HeroSection
      $hidden={hidden}
      aria-labelledby="page-title"
      aria-hidden={hidden}
    >
      <Eyebrow>Cloud Architecture Manager</Eyebrow>
      <Title id="page-title">Find the right architecture for your workload.</Title>
      <Description>
        Tell us what you are building and we will rank the saved architectures
        against your needs.
      </Description>
      {!showForm && (
        <ActionButton type="button" onClick={onStart}>
          Find the right architecture for me
        </ActionButton>
      )}
    </HeroSection>
  );
}
