import React, { useState, useEffect } from "react";
import { recentBuilds } from "../data/recentBuild";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Workflow, Puzzle, Rocket, X, ChevronRight } from "lucide-react";

const mappings = {
  workflow: {
    title: "Recent Workflows",
    listKey: "ai",
    IconComponent: Workflow,
  },
  nocode: { title: "No-Code Builds", listKey: "nocode", IconComponent: Puzzle },
  fullstack: {
    title: "Full-Stack Apps",
    listKey: "fullstack",
    IconComponent: Rocket,
  },
};

const ExpandedView = ({ type, onBack, title, IconComponent }) => {
  const list = recentBuilds[type] || [];
  const gradients = {
    ai: `linear-gradient(135deg, var(--accent-purple), var(--accent-blue))`,
    nocode: `linear-gradient(135deg, var(--accent-green), var(--accent-blue))`,
    fullstack: `linear-gradient(135deg, var(--accent-blue), var(--accent-purple))`,
  };

  return (
    <div className="expanded-view">
      <div className="expanded-view__header">
        <button onClick={onBack} className="expanded-view__back">
          <ChevronRight size={20} />
        </button>
        <h3 className="expanded-view__title">
          {IconComponent && <IconComponent size={20} strokeWidth={2} />}
          {title}
        </h3>
        <button onClick={onBack} className="expanded-view__close" aria-label="Close">
          <X size={20} />
        </button>
      </div>
      <div className="expanded-view__content custom-scrollbar">
        {list.length > 0 ? (
          <div className="expanded-view__list">
            {list.map((item) => (
              <div key={item.id} className="expanded-view__item">
                <div className="expanded-view__item-icon" style={{ background: gradients[type] }}>
                  {item.icon}
                </div>
                <div className="expanded-view__item-details">
                  <h4>{item.title}</h4>
                  <p>Last edited • 2d</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="expanded-view__empty">No items found</div>
        )}
      </div>
    </div>
  );
};

export default function HoverPopup({ type, onClose, isExpanded = false }) {
  const popupRef = React.useRef(null);
  const map = mappings[type] || mappings.workflow;
  const list = recentBuilds[map.listKey] || [];

  // Close popup when pressing Escape key or when navigating away
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === "Escape") {
        onClose?.();
      }
    };

    // Close popup when route changes
    const unlisten = () => {
      onClose?.();
    };

    document.addEventListener("keydown", handleEscape);
    const unlistenHistory = window.addEventListener('popstate', unlisten);
    
    return () => {
      document.removeEventListener("keydown", handleEscape);
      if (unlistenHistory) {
        window.removeEventListener('popstate', unlistenHistory);
      }
    };
  }, [onClose]);

  const navigate = useNavigate();

  const handlePlusClick = (e) => {
    e.stopPropagation();
    if (type === "fullstack") {
      navigate("/chatbot");
    } else {
      navigate("/");
    }
    onClose?.();
  };

  const handleItemClick = (e, item) => {
    e.stopPropagation();
    // Handle item click here
    console.log("Item clicked:", item);
  };

  const gradients = {
    workflow: `linear-gradient(135deg, var(--accent-purple), var(--accent-blue))`,
    nocode: `linear-gradient(135deg, var(--accent-green), var(--accent-blue))`,
    fullstack: `linear-gradient(135deg, var(--accent-blue), var(--accent-purple))`,
  };

  const handleViewMore = (e) => {
    e.stopPropagation();
    navigate(`/view-all/${map.listKey}`);
    onClose?.();
  };


  return (
    <AnimatePresence mode="wait">
      <motion.div
          key="popup-view"
          ref={popupRef}
          data-type={type}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -10 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
          className={`hover-popup ${
            isExpanded ? "hover-popup--from-expanded" : ""
          }`}
          onClick={(e) => e.stopPropagation()}
        >
        {/* Header with gradient (handled by CSS via data-type) */}
        <div className="hover-popup__header">
          <div
            style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}
          >
            {map.IconComponent && (
              <map.IconComponent size={20} strokeWidth={2} />
            )}
            <h3 className="hover-popup__title">{map.title}</h3>
          </div>
          <button
            onClick={onClose}
            className="hover-popup__close"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="hover-popup__content custom-scrollbar">
          {list.length > 0 ? (
            <div style={{ display: "grid", gap: "0.35rem" }}>
              {list.map((item) => (
                <div
                  key={item.id}
                  className="hover-popup__item"
                  onClick={(e) => handleItemClick(e, item)}
                >
                  <div className="icon" style={{ background: gradients[type] }}>
                    {map.IconComponent && (
                      <map.IconComponent size={16} strokeWidth={2} />
                    )}
                  </div>
                  <div className="meta">
                    <h4 className="truncate">{item.title}</h4>
                    <p>Last edited • {item.lastEdited || "2d"}</p>
                  </div>
                  <div className="hover-popup__indicator" />
                </div>
              ))}
            </div>
          ) : (
            <div
              style={{
                padding: "1rem",
                textAlign: "center",
                color: "var(--muted-text)",
              }}
            >
              No recent items
            </div>
          )}
        </div>

          {/* Footer */}
          <div className="hover-popup__footer">
            <div className="hover-popup__footer-buttons">
              <button onClick={handleViewMore} className="hover-popup__view-more">
                <span>View More</span>
                <ChevronRight size={16} />
              </button>
              <button onClick={handlePlusClick} className="hover-popup__new-btn">
                <span>+</span>
                <span>
                  New{" "}
                  {type === "fullstack"
                    ? "App"
                    : type === "workflow"
                    ? "Workflow"
                    : "Build"}
                </span>
              </button>
            </div>
          </div>
        </motion.div>
      ){"}"}
    </AnimatePresence>
  );
}
