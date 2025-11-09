import React, { useState } from "react";
import { motion } from "framer-motion";
import { Plus } from "lucide-react";
import Sidebar from "../components/SideBar";

/**
 * Chatbot builder page template
 * - Glass effect background with particles
 * - Clean UI without chat functionality
 */

export default function Chatbot() {
  const [input, setInput] = useState("");
  const navigate = useNavigate();

  const handleBuild = () => {
    if (input.trim()) {
      // Navigate to Build page with the prompt
      navigate("/build", { state: { prompt: input.trim() } });
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-transparent">
      <Sidebar />

      <div className="relative z-10 w-full min-h-screen flex items-center justify-center pl-[90px] px-6 py-8">
        <div className="w-full max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="glass-container rounded-2xl p-8 w-full"
          >
            <motion.h1
              initial={{ y: -30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6 }}
              className="text-center text-3xl md:text-4xl font-bold text-white mb-3"
            >
              What will you{" "}
              <span className="bg-linear-to-r from-sky-400 to-sky-200 bg-clip-text text-transparent">
                build
              </span>{" "}
              today?
            </motion.h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.15, duration: 0.6 }}
              className="text-center text-gray-300 mb-6"
            >
              Create stunning apps & websites by chatting with AI.
            </motion.p>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="glass-card rounded-xl p-4 w-full"
            >
              {/* Input area - visual only */}
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  className="w-10 h-10 rounded-md bg-white/5 backdrop-blur-md border border-white/10 flex items-center justify-center 
                  text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
                  title="New chat"
                >
                  <Plus className="w-5 h-5" />
                </button>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && input.trim()) {
                      handleBuild();
                    }
                  }}
                  className="flex-1 bg-white/5 backdrop-blur-md outline-none text-gray-200 placeholder-gray-400 px-3 py-3
                  border border-white/10 rounded-lg focus:border-blue-400/50 focus:bg-white/10 transition-all"
                  placeholder="Let's build a data visualization tool for..."
                />
                <button
                  type="button"
                  onClick={handleBuild}
                  className={`px-5 py-2 rounded-lg text-white font-semibold 
                  ${
                    input.trim()
                      ? "bg-blue-600/80 backdrop-blur-md border border-blue-400/30 hover:bg-blue-600/90 hover:scale-105"
                      : "bg-gray-600/50 backdrop-blur-md border border-gray-500/30 cursor-not-allowed"
                  } transition-all`}
                  disabled={!input.trim()}
                >
                  Build
                </button>
              </div>
              <div className="mt-3 text-xs text-gray-400 text-center">
                Agent: Claude Agent • Plan mode
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
