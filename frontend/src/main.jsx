import React from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

function App() {
  return (
    <main className="app-shell">
      <p className="eyebrow">Historical EOD Analysis</p>
      <h1>NIFTY Seller Intelligence</h1>
      <p className="description">
        The application foundation is ready. Analytical features will be added
        in their approved development phases.
      </p>
      <span className="status">Foundation environment</span>
    </main>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
