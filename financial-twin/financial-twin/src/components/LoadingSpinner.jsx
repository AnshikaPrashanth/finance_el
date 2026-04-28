import React from "react";

export default function LoadingSpinner({ message = "Loading…", submessage = "" }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] gap-6 animate-fade-in">
      {/* Concentric ring animation */}
      <div className="relative w-20 h-20">
        <div className="absolute inset-0 rounded-full border-4 border-brand-800 opacity-20" />
        <div className="absolute inset-0 rounded-full border-4 border-t-brand-400 border-r-transparent border-b-transparent border-l-transparent animate-spin" />
        <div className="absolute inset-3 rounded-full border-4 border-t-transparent border-r-brand-300 border-b-transparent border-l-transparent animate-spin [animation-duration:1.5s]" />
      </div>

      <div className="text-center">
        <p className="text-slate-100 font-body text-lg font-medium">{message}</p>
        {submessage && (
          <p className="text-slate-400 font-body text-sm mt-1">{submessage}</p>
        )}
      </div>

      {/* Progress dots */}
      <div className="flex gap-2">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2 h-2 rounded-full bg-brand-500 animate-pulse"
            style={{ animationDelay: `${i * 0.25}s` }}
          />
        ))}
      </div>
    </div>
  );
}

/** Skeleton loader for card placeholders */
export function SkeletonCard({ className = "" }) {
  return (
    <div className={`rounded-2xl bg-slate-800/50 p-5 animate-pulse ${className}`}>
      <div className="h-3 w-24 bg-slate-700 rounded mb-3" />
      <div className="h-7 w-36 bg-slate-600 rounded mb-2" />
      <div className="h-2 w-20 bg-slate-700 rounded" />
    </div>
  );
}
