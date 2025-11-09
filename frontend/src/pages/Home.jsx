import React from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import Sidebar from "../components/SideBar";

export default function Home() {
  return (
    <div className="relative w-full h-screen flex items-center justify-center bg-transparent overflow-hidden">
      <Sidebar />
      <div className="relative z-10 w-full h-full flex items-center justify-center pl-[70px] pr-6 overflow-x-hidden">
        <div className="w-full max-w-6xl flex items-center justify-center px-4">
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="glass-container rounded-2xl p-6 md:p-8 w-full max-w-full"
          >
          <div className="flex flex-col items-start bg-transparent">
            <h1 className="text-4xl md:text-5xl font-bold mb-2 text-white">
              👋 Welcome To the ZeroCodeX!
            </h1>
            <p className="text-base text-gray-400 mb-8">
              Create your first workflow
            </p>

            <div className="flex gap-4 md:gap-6 flex-col md:flex-row items-stretch w-full">
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="flex-1 min-w-0 md:min-w-[250px] h-[180px] md:h-[200px] rounded-xl glass-card flex flex-col items-center justify-center p-4 md:p-6 cursor-pointer"
              >
                <div className="text-5xl mb-4">✨</div>
                <div className="font-semibold text-lg mb-2">Try an AI Workflow</div>
                <div className="text-sm text-gray-400 text-center">
                  Start with prebuilt AI steps
                </div>
              </motion.div>

              <motion.div
                whileHover={{ scale: 1.02 }}
                className="flex-1 min-w-0 md:min-w-[250px] h-[180px] md:h-[200px] rounded-xl glass-card flex flex-col items-center justify-center p-4 md:p-6 cursor-pointer"
              >
                <div className="text-5xl mb-4">📄</div>
                <div className="font-semibold text-lg mb-2">Start from scratch</div>
                <div className="text-sm text-gray-400 text-center">
                  Build your flow step-by-step
                </div>
              </motion.div>
            </div>
          </div>
        </motion.div>
        </div>
      </div>
    </div>
  );
}
