import React, { useState } from 'react';
import {
  Download,
  Filter,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  Bug,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import TestCaseCard from './TestCaseCard';
import { downloadReport } from '../utils/api';

export default function TestCaseList({ testCases, reportText }) {
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [downloading, setDownloading] = useState(false);
  const [pageSize, setPageSize] = useState(25); // 25, 50, or 'ALL'
  const [currentPage, setCurrentPage] = useState(1);

  if (!testCases || testCases.length === 0) return null;

  // Compute counts
  const totalCount = testCases.length;
  const passCount = testCases.filter((t) => t.status === 'PASS').length;
  const failCount = testCases.filter((t) => t.status === 'FAIL').length;
  const errorCount = testCases.filter((t) => t.status === 'ERROR').length;
  const unverifiedCount = testCases.filter((t) => t.status === 'UNVERIFIED').length;
  const bugCount = testCases.filter((t) => t.is_bug_exposing).length;

  // Extract unique categories
  const categories = Array.from(new Set(testCases.map((t) => t.category)));

  // Filter test cases
  const filteredCases = testCases.filter((tc) => {
    if (statusFilter === 'PASS' && tc.status !== 'PASS') return false;
    if (statusFilter === 'FAIL' && tc.status !== 'FAIL') return false;
    if (statusFilter === 'ERROR' && tc.status !== 'ERROR') return false;
    if (statusFilter === 'UNVERIFIED' && tc.status !== 'UNVERIFIED') return false;
    if (statusFilter === 'BUGS' && !tc.is_bug_exposing) return false;

    if (categoryFilter !== 'ALL' && tc.category !== categoryFilter) return false;

    return true;
  });

  // Calculate pagination
  const effectivePageSize = pageSize === 'ALL' ? filteredCases.length : pageSize;
  const totalPages = Math.ceil(filteredCases.length / (effectivePageSize || 1)) || 1;
  const safePage = Math.min(currentPage, totalPages);
  const startIndex = (safePage - 1) * effectivePageSize;
  const paginatedCases =
    pageSize === 'ALL'
      ? filteredCases
      : filteredCases.slice(startIndex, startIndex + effectivePageSize);

  const handleDownload = async () => {
    if (!reportText) return;
    try {
      setDownloading(true);
      await downloadReport(reportText);
    } catch (err) {
      alert('Download error: ' + err.message);
    } finally {
      setDownloading(false);
    }
  };

  const handleFilterChange = (setter, val) => {
    setter(val);
    setCurrentPage(1);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      {/* Top Header & Download */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
            <span>Generated Test Cases</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 font-mono">
              {filteredCases.length} of {totalCount}
            </span>
          </h3>
          <p className="text-xs text-slate-400">
            Deduplicated and verified against independent reference oracle (Minimum 100 cases guaranteed)
          </p>
        </div>

        {/* Download Button */}
        {reportText && (
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="inline-flex items-center space-x-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition shadow-lg shadow-brand-500/25 shrink-0"
          >
            <Download className="w-4 h-4" />
            <span>{downloading ? 'Downloading...' : `Download testcases.txt (${totalCount} cases)`}</span>
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <button
            onClick={() => handleFilterChange(setStatusFilter, 'ALL')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              statusFilter === 'ALL'
                ? 'bg-slate-800 text-white border border-slate-700'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            All ({totalCount})
          </button>
          <button
            onClick={() => handleFilterChange(setStatusFilter, 'PASS')}
            className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center space-x-1 ${
              statusFilter === 'PASS'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'text-emerald-400/80 hover:text-emerald-300 hover:bg-emerald-950/20'
            }`}
          >
            <CheckCircle2 className="w-3 h-3" />
            <span>Passed ({passCount})</span>
          </button>
          <button
            onClick={() => handleFilterChange(setStatusFilter, 'FAIL')}
            className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center space-x-1 ${
              statusFilter === 'FAIL'
                ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                : 'text-red-400/80 hover:text-red-300 hover:bg-red-950/20'
            }`}
          >
            <XCircle className="w-3 h-3" />
            <span>Failed ({failCount})</span>
          </button>
          {errorCount > 0 && (
            <button
              onClick={() => handleFilterChange(setStatusFilter, 'ERROR')}
              className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center space-x-1 ${
                statusFilter === 'ERROR'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'text-amber-400/80 hover:text-amber-300 hover:bg-amber-950/20'
              }`}
            >
              <AlertTriangle className="w-3 h-3" />
              <span>Errors ({errorCount})</span>
            </button>
          )}
          {unverifiedCount > 0 && (
            <button
              onClick={() => handleFilterChange(setStatusFilter, 'UNVERIFIED')}
              className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center space-x-1 ${
                statusFilter === 'UNVERIFIED'
                  ? 'bg-slate-800 text-slate-300 border border-slate-700'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <HelpCircle className="w-3 h-3" />
              <span>Unverified ({unverifiedCount})</span>
            </button>
          )}
          <button
            onClick={() => handleFilterChange(setStatusFilter, 'BUGS')}
            className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center space-x-1 ${
              statusFilter === 'BUGS'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                : 'text-purple-400/80 hover:text-purple-300 hover:bg-purple-950/20'
            }`}
          >
            <Bug className="w-3 h-3" />
            <span>Defect Hunters ({bugCount})</span>
          </button>
        </div>

        {/* Category selector & Page size controls */}
        <div className="flex items-center space-x-2 text-xs text-slate-400">
          <div className="flex items-center space-x-1">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            <select
              value={categoryFilter}
              onChange={(e) => handleFilterChange(setCategoryFilter, e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 text-xs focus:ring-1 focus:ring-brand-500 focus:outline-none"
            >
              <option value="ALL">All Categories</option>
              {categories.map((c, i) => (
                <option key={i} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-1 border-l border-slate-800 pl-2">
            <span className="text-[11px] text-slate-500">Show:</span>
            <select
              value={pageSize}
              onChange={(e) => {
                const val = e.target.value === 'ALL' ? 'ALL' : Number(e.target.value);
                setPageSize(val);
                setCurrentPage(1);
              }}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-slate-200 text-xs focus:ring-1 focus:ring-brand-500 focus:outline-none"
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value="ALL">All ({filteredCases.length})</option>
            </select>
          </div>
        </div>
      </div>

      {/* Cards List */}
      <div className="space-y-2.5 pt-2">
        {filteredCases.length === 0 ? (
          <div className="p-8 text-center bg-slate-950/50 rounded-xl border border-slate-800 text-slate-500 text-xs">
            No test cases found matching the active filter.
          </div>
        ) : (
          paginatedCases.map((tc) => <TestCaseCard key={tc.id} testCase={tc} />)
        )}
      </div>

      {/* Pagination Controls */}
      {pageSize !== 'ALL' && totalPages > 1 && (
        <div className="flex items-center justify-between pt-3 border-t border-slate-800 text-xs text-slate-400">
          <div>
            Showing <span className="text-slate-200 font-medium">{startIndex + 1}</span> to{' '}
            <span className="text-slate-200 font-medium">
              {Math.min(startIndex + effectivePageSize, filteredCases.length)}
            </span>{' '}
            of <span className="text-slate-200 font-medium">{filteredCases.length}</span> cases
          </div>

          <div className="flex items-center space-x-1.5">
            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={safePage === 1}
              className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 text-slate-300 disabled:opacity-30 disabled:hover:bg-transparent"
              title="Previous Page"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-2 py-1 text-slate-300 font-medium bg-slate-950 rounded-lg border border-slate-800">
              Page {safePage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={safePage === totalPages}
              className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 text-slate-300 disabled:opacity-30 disabled:hover:bg-transparent"
              title="Next Page"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
