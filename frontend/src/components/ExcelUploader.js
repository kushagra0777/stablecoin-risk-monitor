import React, { useState } from 'react';

function ExcelUploader() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setResults(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/data/analyze-excel', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setResults(data);
      } else {
        setError(data.error || 'Failed to analyze file');
      }
    } catch (err) {
      setError('Error connecting to server: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (label) => {
    switch (label) {
      case 'SAFE':
        return '#28a745';
      case 'WARNING':
        return '#ffc107';
      case 'RISKY':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  const downloadCSV = () => {
    if (!results || !results.results) return;

    const headers = ['Company', 'Risk Score', 'Risk Label', 'Reserves', 'Supply', 'Price', 'Market Cap', 'Cash/Market Cap'];
    const rows = results.results.map(r => [
      r.company,
      r.risk_score,
      r.risk_label,
      r.metrics.reserves,
      r.metrics.supply,
      r.metrics.price,
      r.metrics.market_cap,
      r.metrics.cash_to_market_cap
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `risk_analysis_${new Date().toISOString()}.csv`;
    a.click();
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h2>📊 Excel Data Import & Risk Analysis</h2>
      
      <div style={{ 
        border: '2px dashed #ccc', 
        borderRadius: '8px', 
        padding: '30px', 
        textAlign: 'center',
        marginBottom: '20px',
        backgroundColor: '#f8f9fa'
      }}>
        <input 
          type="file" 
          accept=".xlsx,.xls,.csv" 
          onChange={handleFileChange}
          style={{ marginBottom: '15px' }}
        />
        
        {file && (
          <div style={{ marginBottom: '15px', color: '#495057' }}>
            Selected: <strong>{file.name}</strong> ({(file.size / 1024).toFixed(2)} KB)
          </div>
        )}

        <button 
          onClick={handleUpload}
          disabled={!file || loading}
          style={{
            padding: '12px 30px',
            fontSize: '16px',
            backgroundColor: loading ? '#6c757d' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: loading || !file ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? '⏳ Analyzing...' : '🚀 Upload & Analyze'}
        </button>
      </div>

      {error && (
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#f8d7da', 
          color: '#721c24',
          borderRadius: '5px',
          marginBottom: '20px'
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {results && results.results && (
        <div>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h3>Analysis Results ({results.total_analyzed} companies)</h3>
            <button 
              onClick={downloadCSV}
              style={{
                padding: '10px 20px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
              }}
            >
              📥 Download CSV
            </button>
          </div>

          {/* Summary Statistics */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(3, 1fr)', 
            gap: '15px',
            marginBottom: '30px'
          }}>
            {['SAFE', 'WARNING', 'RISKY'].map(label => {
              const count = results.results.filter(r => r.risk_label === label).length;
              const percentage = ((count / results.total_analyzed) * 100).toFixed(1);
              return (
                <div key={label} style={{
                  padding: '20px',
                  backgroundColor: getRiskColor(label) + '20',
                  border: `2px solid ${getRiskColor(label)}`,
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: getRiskColor(label) }}>
                    {count}
                  </div>
                  <div style={{ fontSize: '14px', color: '#495057' }}>
                    {label} ({percentage}%)
                  </div>
                </div>
              );
            })}
          </div>

          {/* Results Table */}
          <div style={{ overflowX: 'auto' }}>
            <table style={{ 
              width: '100%', 
              borderCollapse: 'collapse',
              backgroundColor: 'white',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <thead>
                <tr style={{ backgroundColor: '#f8f9fa' }}>
                  <th style={headerStyle}>Company</th>
                  <th style={headerStyle}>Risk Score</th>
                  <th style={headerStyle}>Risk Label</th>
                  <th style={headerStyle}>Reserves</th>
                  <th style={headerStyle}>Supply</th>
                  <th style={headerStyle}>Price</th>
                  <th style={headerStyle}>Market Cap</th>
                  <th style={headerStyle}>Cash/MCap %</th>
                </tr>
              </thead>
              <tbody>
                {results.results.map((result, idx) => (
                  <tr key={idx} style={{ 
                    borderBottom: '1px solid #dee2e6',
                    '&:hover': { backgroundColor: '#f8f9fa' }
                  }}>
                    <td style={cellStyle}>{result.company}</td>
                    <td style={cellStyle}>
                      <strong>{result.risk_score.toFixed(2)}</strong>
                    </td>
                    <td style={cellStyle}>
                      <span style={{
                        padding: '5px 10px',
                        borderRadius: '4px',
                        backgroundColor: getRiskColor(result.risk_label) + '20',
                        color: getRiskColor(result.risk_label),
                        fontWeight: 'bold'
                      }}>
                        {result.risk_label}
                      </span>
                    </td>
                    <td style={cellStyle}>{formatNumber(result.metrics.reserves)}</td>
                    <td style={cellStyle}>{formatNumber(result.metrics.supply)}</td>
                    <td style={cellStyle}>${result.metrics.price.toFixed(2)}</td>
                    <td style={cellStyle}>{formatNumber(result.metrics.market_cap)}</td>
                    <td style={cellStyle}>{(result.metrics.cash_to_market_cap * 100).toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Detailed Explanations */}
          <div style={{ marginTop: '30px' }}>
            <h4>📋 Detailed Analysis</h4>
            {results.results.map((result, idx) => (
              <details key={idx} style={{ marginBottom: '10px' }}>
                <summary style={{ 
                  padding: '10px', 
                  backgroundColor: '#f8f9fa',
                  cursor: 'pointer',
                  borderRadius: '5px'
                }}>
                  <strong>{result.company}</strong> - {result.risk_label}
                </summary>
                <div style={{ padding: '15px', backgroundColor: 'white', border: '1px solid #dee2e6' }}>
                  <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
                    {JSON.stringify(result.explanation, null, 2)}
                  </pre>
                </div>
              </details>
            ))}
          </div>
        </div>
      )}

      <div style={{ 
        marginTop: '30px', 
        padding: '15px', 
        backgroundColor: '#e7f3ff',
        borderRadius: '5px',
        fontSize: '14px'
      }}>
        <strong>ℹ️ Required Excel Columns:</strong>
        <ul style={{ marginTop: '10px', marginBottom: '0' }}>
          <li>Company - Company name or identifier</li>
          <li>bs_cash_cash_equivalents_and_sti - Cash and cash equivalents</li>
          <li>eqy_float - Equity float</li>
          <li>eqy_sh_out - Shares outstanding</li>
          <li>px_last - Last price</li>
        </ul>
      </div>
    </div>
  );
}

const headerStyle = {
  padding: '12px',
  textAlign: 'left',
  borderBottom: '2px solid #dee2e6',
  fontWeight: 'bold',
  fontSize: '14px'
};

const cellStyle = {
  padding: '10px',
  fontSize: '13px'
};

function formatNumber(num) {
  if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  return num.toFixed(2);
}

export default ExcelUploader;
