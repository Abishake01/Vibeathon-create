import React from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import Sidebar from "../components/SideBar";

export default function Home() {
  return (
    <div className="relative min-h-screen flex items-center justify-center bg-transparent">
      <Sidebar />
      <div className="relative z-10 w-full max-w-4xl min-h-[70vh] flex items-center justify-center pl-[90px]">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="glass-container rounded-2xl p-8 w-full"
        >
          <div className="flex flex-col items-center text-center">
            <h1 className="text-3xl md:text-4xl font-semibold mb-2">
              👋 Welcome Prabhagaran!
            </h1>
            <p className="text-sm text-gray-400 mb-8">
              Create your first workflow
            </p>

            <div className="flex gap-6 flex-col md:flex-row items-center justify-center">
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="w-[250px] h-[200px] rounded-xl glass-card flex flex-col items-center justify-center p-6 cursor-pointer"
              >
                <div className="text-4xl mb-3">✨</div>
                <div className="font-medium">Try an AI Workflow</div>
                <div className="text-xs text-gray-400 mt-2">
                  Start with prebuilt AI steps
                </div>
              </motion.div>

              <motion.div
                whileHover={{ scale: 1.02 }}
                className="w-[250px] h-[200px] rounded-xl glass-card flex flex-col items-center justify-center p-6 cursor-pointer"
              >
                <div className="text-4xl mb-3">📄</div>
                <div className="font-medium">Start from scratch</div>
                <div className="text-xs text-gray-400 mt-2">
                  Build your flow step-by-step
                </div>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
