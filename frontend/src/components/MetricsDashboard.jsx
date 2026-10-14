import React from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  Bug,
  Timer,
  Layers,
  BarChart3,
} from 'lucide-react';

export default function MetricsDashboard({ metrics }) {
  if (!metrics) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-brand-400" />
          <h3 className="text-sm font-semibold text-slate-100">
            Execution & Validation Metrics
          </h3>
        </div>
        <div className="flex items-center space-x-1.5 text-xs text-slate-400">
          <Timer className="w-4 h-4 text-slate-500" />
          <span>Execution Latency: <strong className="text-slate-200">{metrics.total_time_ms} ms</strong></span>
        </div>
      </div>

      {/* Grid of Key Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Total Cases */}
        <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
          <span className="text-[11px] text-slate-400 block mb-1">Generated</span>
          <span className="text-xl font-bold text-slate-100 font-mono">
            {metrics.total_cases}
          </span>
        </div>

        {/* Passed */}
        <div className="bg-emerald-950/20 p-3 rounded-xl border border-emerald-500/20 text-center">
          <span className="text-[11px] text-emerald-400 block mb-1 flex items-center justify-center space-x-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>Passed</span>
          </span>
          <span className="text-xl font-bold text-emerald-400 font-mono">
            {metrics.passed_count}
          </span>
        </div>

        {/* Failed */}
        <div className="bg-red-950/20 p-3 rounded-xl border border-red-500/20 text-center">
          <span className="text-[11px] text-red-400 block mb-1 flex items-center justify-center space-x-1">
            <XCircle className="w-3 h-3" />
            <span>Failed</span>
          </span>
          <span className="text-xl font-bold text-red-400 font-mono">
            {metrics.failed_count}
          </span>
        </div>

        {/* Errors */}
        <div className="bg-amber-950/20 p-3 rounded-xl border border-amber-500/20 text-center">
          <span className="text-[11px] text-amber-400 block mb-1 flex items-center justify-center space-x-1">
            <AlertTriangle className="w-3 h-3" />
            <span>Errors</span>
          </span>
          <span className="text-xl font-bold text-amber-400 font-mono">
            {metrics.error_count}
          </span>
        </div>

        {/* Bugs Exposed */}
        <div className="bg-purple-950/20 p-3 rounded-xl border border-purple-500/20 text-center">
          <span className="text-[11px] text-purple-300 block mb-1 flex items-center justify-center space-x-1">
            <Bug className="w-3 h-3" />
            <span>Bugs Caught</span>
          </span>
          <span className="text-xl font-bold text-purple-400 font-mono">
            {metrics.bugs_exposed_count}
          </span>
        </div>

        {/* Pass Rate */}
        <div className="bg-brand-950/20 p-3 rounded-xl border border-brand-500/20 text-center">
          <span className="text-[11px] text-brand-300 block mb-1">Pass Rate</span>
          <span className="text-xl font-bold text-brand-400 font-mono">
            {metrics.pass_rate}%
          </span>
        </div>
      </div>

      {/* Visual Progress Bar */}
      <div>
        <div className="flex justify-between text-xs text-slate-400 mb-1.5">
          <span>Test Suite Partition Distribution</span>
          <span>
            {metrics.passed_count} Pass / {metrics.failed_count} Fail / {metrics.error_count} Error
          </span>
        </div>
        <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden flex">
          {metrics.passed_count > 0 && (
            <div
              style={{ width: `${(metrics.passed_count / metrics.total_cases) * 100}%` }}
              className="bg-emerald-500 transition-all duration-500"
              title={`${metrics.passed_count} Passed`}
            />
          )}
          {metrics.failed_count > 0 && (
            <div
              style={{ width: `${(metrics.failed_count / metrics.total_cases) * 100}%` }}
              className="bg-red-500 transition-all duration-500"
              title={`${metrics.failed_count} Failed (Bugs Identified)`}
            />
          )}
          {metrics.error_count > 0 && (
            <div
              style={{ width: `${(metrics.error_count / metrics.total_cases) * 100}%` }}
              className="bg-amber-500 transition-all duration-500"
              title={`${metrics.error_count} Runtime Exceptions`}
            />
          )}
          {metrics.unverified_count > 0 && (
            <div
              style={{ width: `${(metrics.unverified_count / metrics.total_cases) * 100}%` }}
              className="bg-slate-700 transition-all duration-500"
              title={`${metrics.unverified_count} Unverified`}
            />
          )}
        </div>
      </div>

      {metrics.coverage_summary && (
        <p className="text-[11px] text-slate-400 italic">
          {metrics.coverage_summary}
        </p>
      )}
    </div>
  );
}
