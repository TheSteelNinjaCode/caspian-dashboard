import "/js/pp-reactive-v2.min.js";
import { twMerge } from "/js/tailwind-merge.mjs";

const pp = (globalThis).pp;

globalThis.twMerge = twMerge;

if (document.readyState !== "loading") {
  pp?.mount?.();
} else {
  document.addEventListener(
    "DOMContentLoaded",
    () => pp?.mount?.(),
    { once: true },
  );
}
