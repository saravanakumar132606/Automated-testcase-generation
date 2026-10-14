const API_BASE = '/api';

export async function fetchConfig() {
  const res = await fetch(`${API_BASE}/config`);
  if (!res.ok) throw new Error('Failed to fetch config');
  return res.json();
}

export async function updateConfig(apiKey) {
  const res = await fetch(`${API_BASE}/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: apiKey }),
  });
  if (!res.ok) throw new Error('Failed to update API key');
  return res.json();
}

export async function fetchSamples() {
  const res = await fetch(`${API_BASE}/samples`);
  if (!res.ok) throw new Error('Failed to fetch samples');
  return res.json();
}

export async function uploadCodeFile(file) {
  if (!file) throw new Error('No file selected.');

  // Method 1: Direct client-side reading + server language detection
  try {
    const text = await file.text();
    const res = await fetch(`${API_BASE}/upload-content`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: file.name, content: text }),
    });
    if (res.ok) {
      return await res.json();
    }
    const errData = await res.json().catch(() => ({}));
    if (errData.detail) {
      throw new Error(errData.detail);
    }
  } catch (e) {
    if (e.message && e.message !== 'Failed to fetch' && !e.message.includes('NetworkError')) {
      throw e;
    }
    console.debug('Direct text upload fallback to multipart FormData:', e);
  }

  // Method 2: FormData multipart upload fallback
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'File upload failed' }));
    throw new Error(err.detail || 'File upload failed');
  }
  return res.json();
}

export async function analyzeCode({ code, language, apiKey }) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, language, api_key: apiKey }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Code analysis failed' }));
    throw new Error(err.detail || 'Code analysis failed');
  }
  return res.json();
}

export async function generateTestCases({ code, language, apiKey }) {
  const res = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, language, api_key: apiKey }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Generation failed' }));
    throw new Error(err.detail || 'Test case generation failed');
  }
  return res.json();
}

export async function downloadReport(reportText) {
  const res = await fetch(`${API_BASE}/download-report`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ report_text: reportText }),
  });
  if (!res.ok) throw new Error('Download failed');
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'testcases.txt';
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
