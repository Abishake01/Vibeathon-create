import React, { useState, useEffect, useRef } from "react";
import HoverPopup from "./HoverPopup";
import { useLocation } from "react-router-dom";
import { Zap, Workflow, Puzzle, Rocket, X } from "lucide-react";

const icons = [
  { id: "logo", icon: Zap, label: "App" },
  { id: "workflow", icon: Workflow, label: "Workflow" },
  { id: "nocode", icon: Puzzle, label: "No-code" },
  { id: "fullstack", icon: Rocket, label: "Full-stack" },
];

export default function Sidebar() {
  const [active, setActive] = useState(null);
  const [clickedItem, setClickedItem] = useState(null);
  const [expanded, setExpanded] = useState(false);
  const location = useLocation();
  const sidebarRef = useRef(null);

  // Close popup when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (sidebarRef.current && !sidebarRef.current.contains(event.target)) {
        setClickedItem(null);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleIconClick = (id) => {
    // Toggle clicked item - close if same, open if different
    setClickedItem(clickedItem === id ? null : id);
    setActive(id);
  };

  const handleMouseEnter = (id) => {
    // Only show on hover if no item is clicked
    if (!clickedItem) {
      setActive(id);
    }
  };

  const handleMouseLeave = () => {
    // Only hide if no item is clicked
    if (!clickedItem) {
      setActive(null);
    }
  };

  return (
    <div
      ref={sidebarRef}
      className={`fixed left-0 top-0 h-screen w-[70px] flex flex-col items-center py-6 z-40 bg-[#2B2E33] border-r border-[#3a3a3a] ${
        expanded ? "w-[240px]" : ""
      } transition-all duration-300`}
      onMouseLeave={handleMouseLeave}
    >
      {/* Top section with logo and close button */}
      <div className="w-full flex items-center justify-between px-3 mb-8">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer border-2 border-sky-400/30 bg-sky-400/10 hover:bg-sky-400/20 transition-colors"
          title="App"
          onClick={() => {
            setActive(null);
            setExpanded((e) => !e);
          }}
        >
          <Zap size={20} strokeWidth={2.5} className="text-white" />
        </div>
        {expanded && (
          <button
            className="w-8 h-8 rounded-full flex items-center justify-center cursor-pointer border-2 border-sky-400/30 bg-transparent hover:bg-sky-400/10 transition-colors text-white"
            aria-label="Close"
            onClick={() => setExpanded(false)}
          >
            <X size={18} strokeWidth={2.5} />
          </button>
        )}
      </div>

      {/* Navigation items */}
      <div className="flex flex-col gap-2 items-stretch flex-1 w-full px-2">
        {icons.slice(1).map((item) => {
          const IconComponent = item.icon;
          const isActive = active === item.id || clickedItem === item.id;
          return (
            <div key={item.id} className="relative group">
              <button
                onClick={() => handleIconClick(item.id)}
                onMouseEnter={() => handleMouseEnter(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  isActive
                    ? "bg-sky-500/20 border border-sky-400/30"
                    : "bg-transparent hover:bg-white/5 border border-transparent"
                }`}
                aria-label={item.label}
              >
                <IconComponent 
                  size={20} 
                  strokeWidth={2} 
                  className={isActive ? "text-sky-400" : "text-white/70"} 
                />
                {expanded && (
                  <span className={`text-sm font-medium ${isActive ? "text-sky-400" : "text-white/90"}`}>
                    {item.label}
                  </span>
                )}
              </button>

              {/* Tooltip - shows when not expanded */}
              {!expanded && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-[#141416] text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 border border-white/10">
                  {item.label}
                </div>
              )}

              {/* Popup */}
              {(active === item.id || clickedItem === item.id) && (
                <div
                  onMouseEnter={() => setActive(item.id)}
                  onMouseLeave={() => !clickedItem && setActive(null)}
                  className="absolute left-full ml-2 top-0 z-50"
                >
                  <HoverPopup
                    type={item.id}
                    onClose={() => setClickedItem(null)}
                    isExpanded={expanded}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Bottom user avatar */}
      
    </div>
  );
}
