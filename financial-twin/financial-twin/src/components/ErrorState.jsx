import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function ErrorState({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[360px] gap-5 animate-fade-in">
      <div className="w-16 h-16 rounded-full bg-red-900/30 border border-red-700/50 flex items-center justify-center">
        <AlertTriangle className="w-7 h-7 text-red-400" />
      </div>

      <div className="text-center max-w-md">
        <h3 className="text-slate-100 font-display text-xl mb-2">
          Something went wrong
        </h3>
        <p className="text-slate-400 font-body text-sm leading-relaxed">{message}</p>
      </div>

      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-700 hover:bg-brand-600 text-white font-body text-sm font-medium transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      )}
    </div>
  );
}
