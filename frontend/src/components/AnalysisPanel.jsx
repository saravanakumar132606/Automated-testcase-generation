import React from 'react';
import {
  Brain,
  Code2,
  Bug,
  AlertTriangle,
  HelpCircle,
  Clock,
  Layers,
  CheckCircle2,
} from 'lucide-react';

export default function AnalysisPanel({ analysis }) {
  if (!analysis) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-brand-500/10 text-brand-400 border border-brand-500/20">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">
              Inferred Program Semantics & Code Analysis
            </h3>
            <p className="text-xs text-slate-400">
              Autonomous reasoning over algorithmic logic and contracts
            </p>
          </div>
        </div>

        {/* Confidence Score */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400">Confidence:</span>
          <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-brand-500/10 text-brand-400 border border-brand-500/20">
            {Math.round((analysis.confidence_score || 0.85) * 100)}%
          </span>
        </div>
      </div>

      {/* Purpose & Signature */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800/80">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
            Inferred Purpose
          </span>
          <p className="text-xs text-slate-200 leading-relaxed">
            {analysis.purpose}
          </p>
        </div>

        <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800/80">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
            Function Signature & Return
          </span>
          <div className="font-mono text-xs text-brand-300 bg-slate-900 px-2.5 py-1.5 rounded border border-slate-800 truncate">
            {analysis.signature}
          </div>
          <div className="flex items-center space-x-3 mt-2 text-[11px] text-slate-400">
            <span>
              Return Type: <code className="text-slate-200 font-mono">{analysis.output_type}</code>
            </span>
            {analysis.time_complexity && (
              <span>
                Time: <code className="text-slate-200 font-mono">{analysis.time_complexity}</code>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Input Parameters */}
      {analysis.input_parameters && analysis.input_parameters.length > 0 && (
        <div className="bg-slate-950/50 p-3.5 rounded-xl border border-slate-800/80">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-2">
            Identified Input Parameters ({analysis.input_parameters.length})
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {analysis.input_parameters.map((param, idx) => (
              <div
                key={idx}
                className="flex items-center space-x-2 text-xs bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-lg"
              >
                <code className="text-brand-300 font-mono font-semibold">{param.name}</code>
                <span className="text-slate-500">:</span>
                <span className="text-slate-400 font-mono text-[11px]">{param.type_name}</span>
                {param.description && (
                  <span className="text-slate-500 text-[11px] truncate">
                    — {param.description}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Algorithmic Logic & Variables */}
      <div className="bg-slate-950/50 p-3.5 rounded-xl border border-slate-800/80 space-y-2">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">
          Algorithmic Logic & Flow
        </span>
        <p className="text-xs text-slate-300 leading-relaxed">
          {analysis.algorithmic_logic}
        </p>
        {analysis.variables_and_loops && analysis.variables_and_loops.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {analysis.variables_and_loops.map((item, idx) => (
              <span
                key={idx}
                className="text-[11px] bg-slate-900 text-slate-400 border border-slate-800 px-2 py-0.5 rounded"
              >
                {item}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Potential Bugs & Missing Edge Cases Alert */}
      {(analysis.potential_bugs?.length > 0 || analysis.missing_edge_cases?.length > 0) && (
        <div className="bg-amber-950/20 border border-amber-500/30 p-3.5 rounded-xl space-y-2">
          <div className="flex items-center space-x-2 text-amber-400 text-xs font-semibold">
            <Bug className="w-4 h-4 shrink-0" />
            <span>Targeted Defect Hypotheses & Missing Edge Cases:</span>
          </div>
          <ul className="space-y-1.5 text-xs text-amber-200/90 pl-6 list-disc">
            {analysis.potential_bugs?.map((bug, idx) => (
              <li key={`bug-${idx}`}>
                <span className="font-medium text-amber-300">Suspected Bug:</span> {bug}
              </li>
            ))}
            {analysis.missing_edge_cases?.map((edge, idx) => (
              <li key={`edge-${idx}`}>
                <span className="font-medium text-amber-300">Edge Case Gap:</span> {edge}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Uncertainties (Explicitly stated per specification) */}
      {analysis.uncertainties && analysis.uncertainties.length > 0 && (
        <div className="bg-slate-950/80 border border-slate-800 p-3 rounded-xl flex items-start space-x-2.5 text-xs text-slate-400">
          <HelpCircle className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
          <div>
            <span className="font-medium text-slate-300 block mb-0.5">
              Explicit Semantic Uncertainties:
            </span>
            <ul className="list-disc pl-4 space-y-0.5 text-[11px]">
              {analysis.uncertainties.map((u, idx) => (
                <li key={idx}>{u}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
