import React, { useState, useEffect, useRef } from "react";
import HoverPopup from "./HoverPopup";
import { useLocation } from "react-router-dom";
import { Zap, Workflow, Puzzle, Rocket } from "lucide-react";

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
      className={`sidebar fixed left-0 top-0 h-screen flex flex-col items-center py-6 z-40 glass ${
        expanded ? "sidebar--expanded" : ""
      }`}
      onMouseLeave={handleMouseLeave}
    >
      {expanded && (
        <button
          className="sidebar-close"
          aria-label="Close"
          onClick={() => setExpanded(false)}
        >
          ×
        </button>
      )}
      {/* top logo / home */}
      <div className="mb-8">
        <div
          className="sidebar-logo"
          title="App"
          onClick={() => {
            setActive(null);
            setExpanded((e) => !e);
          }}
        >
          <Zap size={24} strokeWidth={2.5} />
        </div>
      </div>

      <div className="flex flex-col gap-4 items-stretch flex-1 w-full pr-2">
        {icons.slice(1).map((item) => {
          const IconComponent = item.icon;
          return (
            <div key={item.id} className="relative group sidebar-row">
              <button
                onClick={() => handleIconClick(item.id)}
                onMouseEnter={() => handleMouseEnter(item.id)}
                className={`sidebar-icon ${
                  active === item.id || clickedItem === item.id ? "active" : ""
                }`}
                aria-label={item.label}
              >
                <IconComponent size={24} strokeWidth={2} />
              </button>
              {/* label shows when expanded - now with hover functionality */}
              {expanded && (
                <span
                  className="sidebar-label"
                  onMouseEnter={() => handleMouseEnter(item.id)}
                  onMouseLeave={() => !clickedItem && setActive(null)}
                  onClick={() => handleIconClick(item.id)}
                  style={{ cursor: "pointer" }}
                >
                  {item.label}
                </span>
              )}

              {/* Tooltip */}
              <div className={`sidebar-tooltip`}>{item.label}</div>

              {/* Popup */}
              {(active === item.id || clickedItem === item.id) && (
                <div
                  onMouseEnter={() => setActive(item.id)}
                  onMouseLeave={() => !clickedItem && setActive(null)}
                  className={expanded ? "popup-wrapper-expanded" : ""}
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

      {/* bottom icons */}
      <div className="mt-auto flex flex-col gap-6 items-center w-full px-2">
        <div className="sidebar-bottom w-10 h-10">PM</div>
      </div>
    </div>
  );
}
