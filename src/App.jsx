import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./Navbar";
import Upload from "./Upload";
import About from "./About";
import HowItWorks from "./HowItWorks";
import AmbientBackground from "./AmbientBackground";
import "./App.css";

function TypewriterText({ text, speed = 120 }) {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setDisplayedText(text.slice(0, i));
      i++;
      if (i > text.length) clearInterval(interval);
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <span>
      {displayedText}
      <span className="cursor-blink">_</span>
    </span>
  );
}

function Home() {
  return (
    <main className="container fade-in" style={{ marginTop: "90px", textAlign: "center", paddingBottom: "4rem" }}>
      <h1 style={{ fontSize: "clamp(2rem, 5vw, 3.2rem)", marginBottom: "10px" }}>
        Find Your Perfect <span className="text-gradient"><TypewriterText text="Style" /></span>
      </h1>
      <p style={{ color: "var(--text-dim)", marginBottom: "40px", fontSize: "1.1rem", maxWidth: "560px", margin: "0 auto 40px" }}>
        Upload a full-body photo and get AI-powered fashion recommendations tailored to your body shape.
      </p>
      <Upload />
    </main>
  );
}

function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem("wearwisely-theme") || "dark");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("wearwisely-theme", theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  return (
    <BrowserRouter>
      <AmbientBackground />
      <div className="app-container">
        <Navbar theme={theme} toggleTheme={toggleTheme} />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/how-it-works" element={<HowItWorks />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
