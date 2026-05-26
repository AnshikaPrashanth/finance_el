import React, { useState } from "react";
import InputForm from "../components/InputForm";
import Dashboard from "../components/Dashboard";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorState from "../components/ErrorState";
import DataSyncPanel from "../components/DataSyncPanel";
import { runTwinAnalysis } from "../services/api";
import { transformResults, generateFallbackScenarios } from "../utils/transformResults";
import { TrendingUp, BarChart2 } from "lucide-react";

const VIEW = { FORM: "form", LOADING: "loading", RESULTS: "results", ERROR: "error" };

export default function Home() {
  const [view, setView] = useState(VIEW.FORM);
  const [loadingMsg, setLoadingMsg] = useState("Initializing…");
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState(null);
  const [syncedData, setSyncedData] = useState(null);

  const handleSubmit = async (data) => {
    setFormData(data);
    setView(VIEW.LOADING);
    setError(null);

    try {
      const raw = await runTwinAnalysis(data, null, (msg) => setLoadingMsg(msg));
      const normalized = transformResults(raw);

      // If backend didn't return scenarios, generate estimated fallbacks
      if (!normalized.scenarios?.length) {
        normalized.scenarios = generateFallbackScenarios(
          normalized.metrics,
          data.preferences
        );
      }

      setResults(normalized);
      setView(VIEW.RESULTS);
    } catch (err) {
      setError(err.message);
      setView(VIEW.ERROR);
    }
  };

  const handleRetry = () => {
    if (formData) handleSubmit(formData);
    else setView(VIEW.FORM);
  };

  const handleNewSimulation = () => {
    setView(VIEW.FORM);
    setResults(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 font-body">
      {/* Top nav */}
      <header className="border-b border-slate-800/60 bg-slate-950/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-white" />
            </div>
            <span className="font-display text-white text-lg">FinTwin</span>
            <span className="hidden sm:block text-slate-600 text-xs font-body">
              Personal Financial Digital Twin
            </span>
          </div>
          <div className="flex items-center gap-3">
            {view === VIEW.RESULTS && (
              <button
                onClick={handleNewSimulation}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-body text-sm font-medium transition-colors"
              >
                <BarChart2 className="w-4 h-4" />
                New Simulation
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-5 py-10">
        {view === VIEW.FORM && (
          <div className="animate-fade-in">
            <div className="mb-8 text-center">
              <h1 className="font-display text-4xl text-white mb-3">
                Your Financial Digital Twin
              </h1>
              <p className="text-slate-400 font-body text-base max-w-xl mx-auto">
                Enter your complete financial profile. We'll simulate thousands of market
                scenarios and give you a clear, data-driven financial roadmap.
              </p>
            </div>
            
            {/* Data Sync Panel */}
            <DataSyncPanel 
              onDataReceived={(data) => setSyncedData(data)}
            />
            
            {/* Input Form with synced data */}
            <InputForm 
              onSubmit={handleSubmit} 
              isSubmitting={false}
              initialData={syncedData}
            />
          </div>
        )}

        {view === VIEW.LOADING && (
          <LoadingSpinner
            message={loadingMsg}
            submessage="Simulating 1,000+ market scenarios. This may take a few seconds."
          />
        )}

        {view === VIEW.ERROR && (
          <ErrorState message={error} onRetry={handleRetry} />
        )}

        {view === VIEW.RESULTS && results && (
          <Dashboard
            results={results}
            userName={formData?.personal?.fullName || (results.userSummary?.personal?.name) || "User"}
            formData={formData}
            onTwinUpdate={(rawResult) => {
              const normalized = transformResults(rawResult);
              if (normalized) {
                if (!normalized.scenarios?.length) {
                  normalized.scenarios = generateFallbackScenarios(
                    normalized.metrics,
                    formData?.preferences
                  );
                }
                setResults(normalized);
              }
            }}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 mt-20 py-6">
        <p className="text-center text-slate-600 font-body text-xs">
          FinTwin — For educational and planning purposes only. Not financial advice.
        </p>
      </footer>
    </div>
  );
}
