import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Bug,
  Clock,
} from 'lucide-react';

export default function TestCaseCard({ testCase, defaultOpen = true }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [copied, setCopied] = useState(false);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'PASS':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>PASS</span>
          </span>
        );
      case 'FAIL':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20 animate-pulse">
            <XCircle className="w-3.5 h-3.5" />
            <span>FAIL</span>
          </span>
        );
      case 'ERROR':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>ERROR</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>UNVERIFIED</span>
          </span>
        );
    }
  };

  const handleCopyInput = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(testCase.input_formatted);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatVal = (v) => {
    if (v === null || v === undefined) return 'None';
    if (typeof v === 'boolean') return v ? 'true' : 'false';
    return String(v);
  };

  return (
    <div
      className={`border rounded-xl transition-all duration-200 overflow-hidden ${
        testCase.status === 'FAIL'
          ? 'bg-red-950/10 border-red-500/30 shadow-lg shadow-red-950/20'
          : testCase.status === 'ERROR'
          ? 'bg-amber-950/10 border-amber-500/30'
          : 'bg-slate-900 border-slate-800'
      }`}
    >
      {/* Header bar */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-3 flex items-center justify-between cursor-pointer select-none hover:bg-slate-800/40 transition"
      >
        <div className="flex items-center space-x-3 min-w-0">
          <span className="font-mono text-xs font-bold text-slate-500 shrink-0">
            #{testCase.id}
          </span>
          <div className="truncate">
            <span className="text-xs sm:text-sm font-semibold text-slate-200 truncate mr-2">
              {testCase.title}
            </span>
            <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/80 inline-block">
              {testCase.category}
            </span>
            {testCase.is_bug_exposing && (
              <span className="ml-1.5 text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20 font-medium inline-flex items-center space-x-0.5">
                <Bug className="w-2.5 h-2.5 mr-0.5" />
                Defect Hunter
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          {testCase.execution_time_ms !== null && (
            <span className="text-[11px] text-slate-500 hidden sm:flex items-center space-x-1 font-mono">
              <Clock className="w-3 h-3 text-slate-600" />
              <span>{testCase.execution_time_ms} ms</span>
            </span>
          )}
          {getStatusBadge(testCase.status)}
          {isOpen ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {isOpen && (
        <div className="px-4 pb-4 pt-1 border-t border-slate-800/80 space-y-3 text-xs">
          {/* Input block */}
          <div>
            <div className="flex items-center justify-between text-slate-400 text-[11px] font-medium uppercase tracking-wider mb-1">
              <span>Input Values:</span>
              <button
                onClick={handleCopyInput}
                className="text-slate-400 hover:text-white flex items-center space-x-1 font-sans capitalize text-[11px]"
                title="Copy inputs"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 font-mono text-slate-300 whitespace-pre">
              {testCase.input_formatted}
            </div>
          </div>

          {/* Side by side outputs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {/* Expected */}
            <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[11px] font-semibold text-slate-400 block mb-1 uppercase tracking-wider">
                Expected Output
              </span>
              <div className="font-mono text-emerald-400 font-semibold break-all">
                {formatVal(testCase.expected_output)}
              </div>
            </div>

            {/* Actual */}
            <div
              className={`p-2.5 rounded-lg border font-mono ${
                testCase.status === 'PASS'
                  ? 'bg-slate-950 border-slate-800 text-emerald-400'
                  : testCase.status === 'FAIL'
                  ? 'bg-red-950/20 border-red-500/30 text-red-400 font-semibold'
                  : 'bg-amber-950/20 border-amber-500/30 text-amber-400'
              }`}
            >
              <span className="text-[11px] font-semibold text-slate-400 block mb-1 uppercase tracking-wider font-sans">
                Actual Output
              </span>
              <div className="break-all">
                {testCase.actual_output !== null
                  ? formatVal(testCase.actual_output)
                  : testCase.error_message || 'N/A'}
              </div>
            </div>
          </div>

          {/* Reason / Explanation */}
          <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800/80">
            <span className="text-[11px] font-semibold text-slate-400 block mb-1 uppercase tracking-wider">
              Reason & Defect Analysis
            </span>
            <p className="text-slate-300 text-xs leading-relaxed">
              {testCase.reason}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
