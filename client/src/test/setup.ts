import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach } from "vitest";

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
});

// jsdom não implementa rolagem nem matchMedia; os componentes só precisam
// que as funções existam para não quebrar durante os testes.
Element.prototype.scrollIntoView = () => {};
window.scrollTo = () => {};
if (!window.matchMedia) {
  window.matchMedia = (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList;
}
