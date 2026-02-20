import React from "react";
import Dashboard from "./components/Dashboard";
import ExcelUploader from "./components/ExcelUploader";

function App() {
  return (
    <div style={{ fontFamily: 'Arial, sans-serif' }}>
      <header style={{ 
        backgroundColor: '#007bff', 
        color: 'white', 
        padding: '20px',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: 0 }}>🛡️ Stablecoin Risk Monitor</h1>
        <p style={{ margin: '5px 0 0 0', opacity: 0.9 }}>
          AI-Powered Risk Analysis for Financial Assets
        </p>
      </header>
      
      <div style={{ padding: '0 20px' }}>
        <ExcelUploader />
        
        <hr style={{ margin: '40px 0', border: '1px solid #dee2e6' }} />
        
        <Dashboard />
      </div>
      
      <footer style={{ 
        textAlign: 'center', 
        padding: '20px',
        marginTop: '40px',
        borderTop: '1px solid #dee2e6',
        color: '#6c757d',
        fontSize: '14px'
      }}>
        <p>Stablecoin Risk Monitor © 2026 | Powered by AI & Blockchain</p>
      </footer>
    </div>
  );
}

export default App;
