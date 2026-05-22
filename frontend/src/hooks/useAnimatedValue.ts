import { useEffect, useRef, useState } from "react";
import gsap from "gsap";

import { prefersReducedMotion } from "../lib/motion";

/** Contador numérico suave (solo transform vía texto; sin layout thrashing). */
export function useAnimatedValue(target: number, duration = 0.55) {
  const [display, setDisplay] = useState(target);
  const proxy = useRef({ value: target });
  const prev = useRef(target);

  useEffect(() => {
    if (prefersReducedMotion()) {
      setDisplay(target);
      proxy.current.value = target;
      prev.current = target;
      return;
    }
    if (target === prev.current) return;
    gsap.killTweensOf(proxy.current);
    gsap.to(proxy.current, {
      value: target,
      duration,
      ease: "power2.out",
      onUpdate: () => setDisplay(Math.round(proxy.current.value)),
      onComplete: () => {
        prev.current = target;
      },
    });
  }, [target, duration]);

  return display;
}
