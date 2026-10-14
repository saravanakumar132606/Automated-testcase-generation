import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import CodeEditor from './components/CodeEditor';
import AnalysisPanel from './components/AnalysisPanel';
import MetricsDashboard from './components/MetricsDashboard';
import TestCaseList from './components/TestCaseList';
import SettingsModal from './components/SettingsModal';
import ReportModal from './components/ReportModal';
import { fetchConfig, fetchSamples, generateTestCases } from './utils/api';
import { AlertCircle, Sparkles, CheckCircle2, FileText, Brain, ShieldAlert } from 'lucide-react';

export default function App() {
  const [config, setConfig] = useState({
    gemini_configured: false,
    default_model: 'gemini-3.8-flash',
    supported_languages: ['python', 'java', 'cpp', 'c'],
  });
  const [samples, setSamples] = useState([]);
  const [selectedSampleId, setSelectedSampleId] = useState('');
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');

  // Generation state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationPhase, setGenerationPhase] = useState('');
  const [error, setError] = useState('');

  // Results
  const [analysis, setAnalysis] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [reportText, setReportText] = useState('');

  // Modals & active tabs
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('tests'); // 'tests' | 'analysis'

  useEffect(() => {
    // Initial data load
    fetchConfig()
      .then((cfg) => setConfig(cfg))
      .catch((err) => console.error('Config fetch failed:', err));

    fetchSamples()
      .then((data) => {
        setSamples(data.samples || []);
        // Pre-load the first sample (Anagram Checker) for instant evaluation!
        if (data.samples && data.samples.length > 0) {
          const first = data.samples[0];
          setSelectedSampleId(first.id);
          setCode(first.code);
          setLanguage(first.language || 'python');
        }
      })
      .catch((err) => console.error('Samples fetch failed:', err));
  }, []);

  const handleSelectSample = (sampleId) => {
    setSelectedSampleId(sampleId);
    const sample = samples.find((s) => s.id === sampleId);
    if (sample) {
      setCode(sample.code);
      setLanguage(sample.language || 'python');
      setError('');
    }
  };

  const handleGenerate = async () => {
    if (!code.trim()) {
      setError('Source code cannot be empty. Please paste your solution or upload a file.');
      return;
    }

    if (code.trim().length < 15) {
      setError('The submitted code is too incomplete or ambiguous to analyze reliably.');
      return;
    }

    setError('');
    setIsGenerating(true);
    setGenerationPhase('Analyzing source code & inferring semantic contracts...');

    try {
      // Simulate sequential phase feedback for rich UX
      setTimeout(() => {
        setGenerationPhase('Synthesizing logic-based test cases and boundary conditions...');
      }, 700);

      setTimeout(() => {
        setGenerationPhase('Executing solution in isolated subprocess sandbox...');
      }, 1400);

      const resp = await generateTestCases({
        code,
        language,
        apiKey: null, // Will use runtime key from backend
      });

      setAnalysis(resp.analysis);
      setTestCases(resp.test_cases || []);
      setMetrics(resp.metrics);
      setReportText(resp.report_text || '');
      setActiveTab('tests');
    } catch (err) {
      setError(err.message || 'An error occurred during test generation.');
    } finally {
      setIsGenerating(false);
      setGenerationPhase('');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <Navbar
        config={config}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenReport={() => setIsReportOpen(true)}
        hasReport={Boolean(reportText)}
        samples={samples}
        onSelectSample={handleSelectSample}
        selectedSampleId={selectedSampleId}
      />

      {/* Main Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col space-y-6">
        {/* Error Banner */}
        {error && (
          <div className="bg-red-950/30 border border-red-500/40 rounded-xl p-4 flex items-center justify-between text-red-300 text-xs sm:text-sm animate-shake">
            <div className="flex items-center space-x-2.5">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => setError('')}
              className="text-red-400 hover:text-white font-semibold text-xs ml-4"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* 2-Column Split Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start flex-1">
          {/* Left Column: Code Input & Editor (5 cols) */}
          <div className="lg:col-span-5 h-[680px] flex flex-col">
            <CodeEditor
              code={code}
              onChangeCode={(newCode) => {
                setCode(newCode);
                setError('');
                setSelectedSampleId('');
              }}
              language={language}
              onChangeLanguage={setLanguage}
              onGenerate={handleGenerate}
              isGenerating={isGenerating}
              generationPhase={generationPhase}
            />
          </div>

          {/* Right Column: Output & Analysis & Tests (7 cols) */}
          <div className="lg:col-span-7 flex flex-col space-y-4">
            {/* View Switcher Tabs (Only when results exist) */}
            {testCases.length > 0 && (
              <div className="flex items-center justify-between bg-slate-900 border border-slate-800 p-1 rounded-xl">
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => setActiveTab('tests')}
                    className={`flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                      activeTab === 'tests'
                        ? 'bg-brand-600 text-white shadow-sm'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Test Suite & Results ({testCases.length})</span>
                  </button>
                  <button
                    onClick={() => setActiveTab('analysis')}
                    className={`flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                      activeTab === 'analysis'
                        ? 'bg-brand-600 text-white shadow-sm'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    <Brain className="w-4 h-4" />
                    <span>Inferred Semantics & Bugs</span>
                  </button>
                </div>

                {reportText && (
                  <button
                    onClick={() => setIsReportOpen(true)}
                    className="flex items-center space-x-1 text-xs text-brand-400 hover:text-brand-300 px-3 py-1.5 font-medium transition"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">Preview Report</span>
                  </button>
                )}
              </div>
            )}

            {/* Metrics Dashboard */}
            {metrics && <MetricsDashboard metrics={metrics} />}

            {/* Content Area */}
            {testCases.length > 0 ? (
              activeTab === 'tests' ? (
                <TestCaseList testCases={testCases} reportText={reportText} />
              ) : (
                <AnalysisPanel analysis={analysis} />
              )
            ) : (
              /* Empty state placeholder */
              <div className="h-[520px] bg-slate-900/60 border border-slate-800/80 border-dashed rounded-2xl flex flex-col items-center justify-center p-8 text-center space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-slate-800/80 border border-slate-700/80 flex items-center justify-center text-slate-400">
                  <Sparkles className="w-8 h-8 text-brand-400" />
                </div>
                <div className="max-w-md space-y-1.5">
                  <h3 className="text-base font-semibold text-slate-200">
                    Awaiting Source Code Submission
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Paste your solution or choose a sample problem on the left, then click{' '}
                    <strong className="text-slate-200">"Generate Test Cases"</strong>. The system
                    will autonomously infer specifications, generate targeted logic-based tests,
                    and validate against an independent reference oracle.
                  </p>
                </div>
                <button
                  onClick={handleGenerate}
                  disabled={!code.trim() || isGenerating}
                  className="inline-flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-4 py-2 rounded-xl border border-slate-700 transition"
                >
                  <Sparkles className="w-3.5 h-3.5 text-brand-400" />
                  <span>Run Evaluation on Current Code</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Modals */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        currentKey=""
        onSaved={() => {
          fetchConfig().then(setConfig);
        }}
      />

      <ReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        reportText={reportText}
      />
    </div>
  );
}
