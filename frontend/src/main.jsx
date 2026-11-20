import React from "react";
import { createRoot } from "react-dom/client";

function App() {
  return (
    <main>
      <h1>NIFTY Seller Intelligence</h1>
      <p>Frontend foundation is ready for implementation.</p>
    </main>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
