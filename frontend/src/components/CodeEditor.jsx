import React, { useRef, useState } from 'react';
import { Upload, Code, Trash2, Sparkles, CheckCircle2, FileCode, AlertCircle } from 'lucide-react';
import { uploadCodeFile } from '../utils/api';

export default function CodeEditor({
  code,
  onChangeCode,
  language,
  onChangeLanguage,
  onGenerate,
  isGenerating,
  generationPhase,
}) {
  const fileInputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');

  const handleFileUpload = async (file) => {
    if (!file) return;
    setUploadError('');
    setUploadSuccess('');
    try {
      const data = await uploadCodeFile(file);
      onChangeCode(data.code);
      if (data.language) {
        onChangeLanguage(data.language);
      }
      setUploadSuccess(`Loaded "${data.filename || file.name}" (${(data.language || 'code').toUpperCase()} detected)`);
      setTimeout(() => setUploadSuccess(''), 4000);
    } catch (err) {
      setUploadError(err.message || 'Failed to upload code file');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  // Compute line numbers
  const lines = code.split('\n');
  const lineCount = lines.length;

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      {/* Top Bar */}
      <div className="px-4 py-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center space-x-2">
          <FileCode className="w-4 h-4 text-brand-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Source Code
          </span>
          <span className="text-[11px] text-slate-500">
            ({lineCount} lines, {code.length} chars)
          </span>
        </div>

        <div className="flex items-center space-x-2">
          {/* Language Selector */}
          <select
            value={language}
            onChange={(e) => onChangeLanguage(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-lg px-2.5 py-1.5 focus:ring-1 focus:ring-brand-500 focus:outline-none"
          >
            <option value="auto">Auto-Detect</option>
            <option value="python">Python (.py)</option>
            <option value="java">Java (.java)</option>
            <option value="cpp">C++ (.cpp)</option>
            <option value="c">C (.c)</option>
          </select>

          {/* Upload Button */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFileUpload(e.target.files[0]);
              }
              // Reset value so user can re-upload the same file repeatedly
              e.target.value = '';
            }}
            accept=".py,.java,.cpp,.cc,.cxx,.c,.h,.hpp,.hh,.hxx,.txt,.pyw,text/plain,text/*"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center space-x-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1.5 rounded-lg border border-slate-700 transition"
            title="Upload code file (.py, .java, .cpp, .c, .txt)"
          >
            <Upload className="w-3.5 h-3.5 text-slate-400" />
            <span className="hidden sm:inline">Upload</span>
          </button>

          {/* Clear Button */}
          {code && (
            <button
              onClick={() => {
                onChangeCode('');
                setUploadError('');
                setUploadSuccess('');
              }}
              className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-800 transition"
              title="Clear editor"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {uploadSuccess && (
        <div className="bg-emerald-500/10 border-b border-emerald-500/20 px-4 py-2 text-xs text-emerald-400 flex items-center space-x-1.5 animate-fadeIn">
          <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
          <span>{uploadSuccess}</span>
        </div>
      )}

      {uploadError && (
        <div className="bg-red-500/10 border-b border-red-500/20 px-4 py-2 text-xs text-red-400 flex items-center space-x-1.5 animate-fadeIn">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Editor Area with Drag and Drop */}
      <div
        onDragEnter={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setDragOver(true);
        }}
        onDragOver={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setDragOver(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setDragOver(false);
        }}
        onDrop={handleDrop}
        className={`relative flex-1 flex overflow-hidden font-mono text-xs bg-slate-950 transition ${
          dragOver ? 'ring-2 ring-brand-500 ring-inset bg-brand-950/20' : ''
        }`}
      >
        {/* Line Numbers */}
        <div className="w-10 py-3 pr-2 select-none text-right text-slate-600 bg-slate-950/60 border-r border-slate-800/80 font-mono text-xs shrink-0 overflow-hidden">
          {lines.map((_, i) => (
            <div key={i} className="leading-5">
              {i + 1}
            </div>
          ))}
        </div>

        {/* Text Area */}
        <textarea
          value={code}
          onChange={(e) => {
            onChangeCode(e.target.value);
            if (uploadError) setUploadError('');
          }}
          onDragOver={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setDragOver(true);
          }}
          onDrop={handleDrop}
          placeholder="// Paste your solution code here, or drag & drop a source file (.py, .java, .cpp, .c, .txt)&#10;// No problem statement required — our LLM will infer the requirements and generate targeted tests."
          spellCheck="false"
          className="flex-1 w-full h-full p-3 bg-transparent text-slate-200 resize-none outline-none leading-5 font-mono selection:bg-brand-500 selection:text-white"
        />

        {dragOver && (
          <div className="absolute inset-0 bg-brand-950/80 backdrop-blur-sm flex items-center justify-center pointer-events-none">
            <div className="text-center text-brand-300 font-sans">
              <Upload className="w-8 h-8 mx-auto mb-2 animate-bounce" />
              <p className="text-sm font-semibold">Drop source code file to upload</p>
              <p className="text-xs text-brand-400/80 mt-1">Supports .py, .java, .cpp, .c, .txt</p>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Action Footer */}
      <div className="p-4 bg-slate-900 border-t border-slate-800 flex items-center justify-between">
        <div className="text-xs text-slate-400">
          {isGenerating ? (
            <span className="flex items-center space-x-2 text-brand-400 font-medium animate-pulse">
              <Sparkles className="w-4 h-4" />
              <span>{generationPhase || 'Generating test cases...'}</span>
            </span>
          ) : (
            <span className="text-slate-500">
              Ready to analyze & generate test suite (Min 100 cases)
            </span>
          )}
        </div>

        <button
          onClick={onGenerate}
          disabled={isGenerating || !code.trim()}
          className="inline-flex items-center space-x-2 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-medium text-xs sm:text-sm px-5 py-2.5 rounded-xl shadow-lg shadow-brand-500/25 transition disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {isGenerating ? (
            <>
              <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Generate Test Cases</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
