import React from 'react';
import { Cpu, Settings, FileText, Sparkles, Code2, ShieldAlert } from 'lucide-react';

export default function Navbar({
  config,
  onOpenSettings,
  onOpenReport,
  hasReport,
  samples,
  onSelectSample,
  selectedSampleId,
}) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-slate-100 tracking-tight">
                AutoTest<span className="text-brand-400">Gen</span>
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20 font-medium">
                LLM Powered
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Automated Test Case Generation from Source Code
            </p>
          </div>
        </div>

        {/* Center / Samples */}
        <div className="flex items-center space-x-3">
          <div className="hidden md:flex items-center space-x-2 bg-slate-950/60 border border-slate-800 rounded-lg p-1">
            <span className="text-xs text-slate-400 pl-2 pr-1 font-medium flex items-center">
              <Code2 className="w-3.5 h-3.5 mr-1 text-slate-500" />
              Demo Samples:
            </span>
            <select
              value={selectedSampleId}
              onChange={(e) => onSelectSample(e.target.value)}
              className="bg-slate-900 text-xs text-slate-200 border-none rounded px-2.5 py-1 focus:ring-1 focus:ring-brand-500 focus:outline-none cursor-pointer"
            >
              <option value="">-- Choose Sample Problem --</option>
              {samples.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.title} ({s.language})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center space-x-2.5">
          {/* Status Indicator */}
          <div
            className={`flex items-center space-x-1.5 text-xs px-2.5 py-1 rounded-full border ${
              config.gemini_configured
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
            }`}
            title={
              config.gemini_configured
                ? 'Gemini 3.8 Flash LLM active for semantic analysis and test generation'
                : 'Using built-in AST and Semantic Heuristic engine (Add API Key in settings for full LLM power)'
            }
          >
            <span
              className={`w-2 h-2 rounded-full ${
                config.gemini_configured ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            />
            <span className="font-medium hidden sm:inline">
              {config.gemini_configured ? 'Gemini LLM Ready' : 'Semantic Heuristics'}
            </span>
          </div>

          {/* View Report Button */}
          {hasReport && (
            <button
              onClick={onOpenReport}
              className="inline-flex items-center space-x-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition"
              title="Preview testcases.txt"
            >
              <FileText className="w-3.5 h-3.5 text-brand-400" />
              <span className="font-medium hidden sm:inline">Report</span>
            </button>
          )}

          {/* Settings Modal */}
          <button
            onClick={onOpenSettings}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
            title="Configure Gemini API Key"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
