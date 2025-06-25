import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    tailwindcss(),  // inject Tailwind v4
    react(),        // enable React HMR, JSX, etc.
  ],
  // (optional) if you ever need to alias paths, add here:
//   resolve: { alias: { "@": "/src" } }
});
