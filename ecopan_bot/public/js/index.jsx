// public/js/index.jsx
import React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";

// 🚨 Debug: logga subito
console.log("🎬 frontend.js caricato, montiamo React");

// Montaggio
const container = document.getElementById("root");
const root = createRoot(container);
root.render(<App />);