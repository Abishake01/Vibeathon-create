import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Chatbot from "./pages/Chatbot";
import Build from "./pages/Build";
import ViewAllPage from "./pages/ViewAllPage";
import SubtleParticles from "./components/SubtleParticles";
import CustomCursor from "./components/CustomCursor";

export default function App() {
  return (
    <BrowserRouter>
      <div className="relative min-h-screen bg-black">
        <CustomCursor />
        <SubtleParticles />
        <div className="relative z-10">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chatbot" element={<Chatbot />} />
            <Route path="/build" element={<Build />} />
            <Route path="/view-all/:type" element={<ViewAllPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
