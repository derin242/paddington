if (!window.analysisListenerAttached) {
  document.getElementById("runBtn").addEventListener("click", () => {
    const button = document.getElementById("runBtn");
    button.disabled = true;
    
    document.getElementById("result").textContent = "Analyzing...";

    browser.runtime.sendMessage({ action: "getURL" })
      .then(response => {
        if (!response?.url) throw new Error("No URL received");
        return fetch('http://localhost:5000/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: response.url })
        });
      })
      .then(res => res.json())
      .then(data => {
        document.getElementById("result").textContent = data.result || data.error;
      })
      .catch(err => {
        document.getElementById("result").textContent = err.message;
      })
      .finally(() => {
        button.disabled = false;
      });
  });
  
  window.analysisListenerAttached = true;
}
