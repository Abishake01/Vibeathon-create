import React, { useState, useEffect } from 'react';

const PreviewPanel = ({ projectId, previewUrl, isLoading }) => {
  const [iframeKey, setIframeKey] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (previewUrl) {
      setIframeKey((prev) => prev + 1);
      setError(null);
    }
  }, [previewUrl]);

  const handleIframeError = () => {
    setError('Failed to load preview. Please try refreshing.');
  };

  return (
    <div className="flex flex-col h-full bg-[#0a0a0a] relative">
      {isLoading ? (
        <div className="flex-1 flex flex-col items-center justify-center text-[#444]">
          <div className="w-10 h-10 border-[3px] border-[#2a2a2a] border-t-blue-500 rounded-full animate-spin mb-4"></div>
          <p className="text-[#666] text-base m-0">Creating project...</p>
        </div>
      ) : error ? (
        <div className="flex-1 flex flex-col items-center justify-center text-[#444]">
          <div className="text-[120px] font-bold text-[#1a1a1a] opacity-30 mb-5">⚠</div>
          <p className="text-[#666] text-base m-0">{error}</p>
          <button onClick={() => window.location.reload()} className="mt-2.5 px-4 py-2 cursor-pointer bg-blue-500 text-white rounded hover:bg-blue-600">
            Refresh
          </button>
        </div>
      ) : previewUrl ? (
        <iframe
          key={iframeKey}
          src={previewUrl}
          className="flex-1 w-full border-none bg-white"
          title="Preview"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          onError={handleIframeError}
          onLoad={() => setError(null)}
        />
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center text-[#444]">
          <p className="text-[#666] text-base m-0">Your preview will appear here</p>
        </div>
      )}
    </div>
  );
};

export default PreviewPanel;
