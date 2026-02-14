// src/hooks/useAutoScroll.js
import { useEffect } from "react";

export default function useAutoScroll(ref, dep) {
  useEffect(() => {
    ref.current?.scrollIntoView({ behavior: "smooth" });
  }, [dep]);
}
