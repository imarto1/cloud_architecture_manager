import { useEffect, useRef } from "react";

const AUTO_SCROLL_PIXELS_PER_SECOND = 18;
const WHEEL_SCROLL_FACTOR = 0.6;

export function useLoopingScroll(itemCount: number) {
  const scrollerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const scroller = scrollerRef.current;
    let scrollPosition = scroller?.scrollLeft ?? 0;
    let animationFrame = 0;
    let previousTime: number | null = null;

    function handleMouseWheel(event: WheelEvent) {
      if (!scroller) {
        return;
      }

      const distance =
        Math.abs(event.deltaX) > Math.abs(event.deltaY)
          ? event.deltaX
          : event.deltaY;
      let pixelDistance = distance;
      if (event.deltaMode === WheelEvent.DOM_DELTA_LINE) {
        pixelDistance *= 16;
      } else if (event.deltaMode === WheelEvent.DOM_DELTA_PAGE) {
        pixelDistance *= scroller.clientWidth;
      }
      const scrollDistance = pixelDistance * WHEEL_SCROLL_FACTOR;

      if (scrollDistance === 0) {
        return;
      }

      event.preventDefault();

      if (reducedMotion.matches) {
        scroller.scrollLeft += scrollDistance;
        return;
      }

      const loopWidth = scroller.scrollWidth / 2;
      if (loopWidth === 0) {
        return;
      }
      scrollPosition =
        (((scrollPosition + scrollDistance) % loopWidth) + loopWidth) %
        loopWidth;
      scroller.scrollLeft = scrollPosition;
    }

    function animate(timestamp: number) {
      if (scroller && previousTime !== null && !reducedMotion.matches) {
        const elapsedSeconds = (timestamp - previousTime) / 1000;
        const loopWidth = scroller.scrollWidth / 2;
        scrollPosition += elapsedSeconds * AUTO_SCROLL_PIXELS_PER_SECOND;

        if (scrollPosition >= loopWidth) {
          scrollPosition -= loopWidth;
        }
        scroller.scrollLeft = scrollPosition;
      }

      previousTime = timestamp;
      animationFrame = window.requestAnimationFrame(animate);
    }

    scroller?.addEventListener("wheel", handleMouseWheel, { passive: false });
    animationFrame = window.requestAnimationFrame(animate);
    return () => {
      scroller?.removeEventListener("wheel", handleMouseWheel);
      window.cancelAnimationFrame(animationFrame);
    };
  }, [itemCount]);

  return scrollerRef;
}
