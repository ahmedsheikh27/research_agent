// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ["purple-toys-tap.loca.lt", "empty-rings-end.loca.lt"]
  }
});