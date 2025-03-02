import React, { useState } from 'react';
import './App.css';

function App() {
  const [result, setResult] = useState('');

  const handleApiCall = async (apiNumber) => {
    try {
      let response;
      if (apiNumber === 1) {
        response = await fetch('http://localhost:8002/products/?skip=0&limit=100');
      } else {
        response = await fetch('http://localhost:8001/orders/');
      }
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2)); // Pretty print JSON result
    } catch (error) {
      setResult(`Error: ${error.message}`);
    }
  };

  return (
    <div className="App">
      <h1>API Buttons Example</h1>

      <div>
        <button onClick={() => handleApiCall(1)}>Call API products</button>
        <button onClick={() => handleApiCall(2)}>Call API orders</button>
      </div>

      <div>
        <textarea
          value={result}
          readOnly
          placeholder="API result will appear here..."
          rows={10}
          cols={50}
        />
      </div>
    </div>
  );
}

export default App;
