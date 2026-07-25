import { createGlobalStyle, styled } from "styled-components";

export const GlobalStyle = createGlobalStyle`
  :root {
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
    color: #e6edf7;
    background: #0d1627;
    font-synthesis: none;
  }

  * {
    box-sizing: border-box;
  }

  body {
    margin: 0;
  }

  h2,
  h3 {
    margin-top: 0;
  }
`;

export const Page = styled.main`
  min-height: 100vh;
  padding: 5rem max(2rem, calc((100vw - 84rem) / 2));

  @media (max-width: 44rem) {
    padding: 3rem 1.25rem;
  }
`;

export const ActionButton = styled.button`
  border: 0;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  color: #07101f;
  background: #69d2e7;
  font: inherit;
  font-weight: 700;
  cursor: pointer;

  &:disabled {
    cursor: wait;
    opacity: 0.7;
  }
`;

export const SecondaryButton = styled(ActionButton)`
  margin-top: 2.5rem;
  border: 1px solid #3b5072;
  color: #e6edf7;
  background: transparent;
  transition:
    border-color 225ms ease,
    color 225ms ease,
    transform 225ms ease;

  &:hover {
    border-color: #69d2e7;
    color: #69d2e7;
    transform: translateY(-0.125rem);
  }

  &:focus-visible {
    outline: 3px solid rgb(105 210 231 / 45%);
    outline-offset: 3px;
  }

  @media (prefers-reduced-motion: reduce) {
    transition: none;
  }
`;

export const Eyebrow = styled.p`
  margin: 0;
  color: #69d2e7;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
`;

export const ErrorMessage = styled.p`
  color: #ff9b9b;
`;
