function handleMessage(request, sender, sendResponse) {
    if (request.action === "getURL") {
      browser.tabs.query({ active: true, currentWindow: true })
        .then(tabs => {
          sendResponse({ url: tabs[0]?.url || null });
        })
        .catch(error => {
          sendResponse({ error: "URL retrieval failed" });
        });
      return true;
    }
  }
  
  browser.runtime.onMessage.removeListener(handleMessage);
  browser.runtime.onMessage.addListener(handleMessage);
  