import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { recentBuilds } from '../data/recentBuild';
import { Workflow, Puzzle, Rocket, ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';

const typeIcons = {
  ai: Workflow,
  nocode: Puzzle,
  fullstack: Rocket,
};

const typeTitles = {
  ai: 'Workflows',
  nocode: 'No-Code Builds',
  fullstack: 'Full-Stack Apps',
};

export default function ViewAllPage() {
  const navigate = useNavigate();
  const { type } = useParams();
  const items = recentBuilds[type] || [];
  const IconComponent = typeIcons[type] || Workflow;
  const title = typeTitles[type] || 'Items';

  const gradients = {
    ai: 'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))',
    nocode: 'linear-gradient(135deg, var(--accent-green), var(--accent-blue))',
    fullstack: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/50 backdrop-blur-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 rounded-lg p-2 text-blue-400 hover:bg-white/5 transition-colors"
            >
              <ArrowLeft size={20} />
              <span>Back</span>
            </button>
            <div className="flex items-center gap-2">
              <div 
                className="p-2 rounded-lg"
                style={{ background: gradients[type] || gradients.ai }}
              >
                <IconComponent size={24} />
              </div>
              <h1 className="text-2xl font-bold">All {title}</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-gray-900/50 rounded-xl p-6 border border-white/10 hover:border-blue-500/30 transition-all hover:shadow-lg hover:shadow-blue-500/10 cursor-pointer"
              onClick={() => {
                // Handle item click
                console.log('Item clicked:', item);
              }}
            >
              <div className="flex items-start gap-4">
                <div 
                  className="p-3 rounded-lg flex-shrink-0"
                  style={{ background: gradients[type] || gradients.ai }}
                >
                  <span className="text-xl">{item.icon}</span>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{item.title}</h3>
                  <p className="text-sm text-gray-400 mt-1">Last edited • 2d</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {items.length === 0 && (
          <div className="text-center py-16">
            <p className="text-gray-400">No items found</p>
          </div>
        )}
      </main>
    </div>
  );
}
