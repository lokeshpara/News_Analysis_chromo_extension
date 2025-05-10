document.addEventListener('DOMContentLoaded', function() {
  const analyzeBtn = document.getElementById('analyzeBtn');
  const promptInput = document.getElementById('promptInput');
  const loader = document.getElementById('loader');
  const summaryContainer = document.getElementById('summaryContainer');
  const headlinesContainer = document.getElementById('headlinesContainer');
  const sentimentContainer = document.getElementById('sentimentContainer');
  const summaryResult = document.getElementById('summaryResult');
  const headlinesResult = document.getElementById('headlinesResult');
  const sentimentResult = document.getElementById('sentimentResult');

  const API_URL = 'http://localhost:5000/api';

  // Show a status message on the UI for debugging
  function showStatus(message) {
    const statusDiv = document.createElement('div');
    statusDiv.style.color = 'blue';
    statusDiv.style.padding = '5px';
    statusDiv.textContent = message;
    document.querySelector('.container').prepend(statusDiv);
    setTimeout(() => statusDiv.remove(), 5000);
  }

  analyzeBtn.addEventListener('click', async function() {
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
      alert('Please enter a prompt');
      return;
    }

    // Show loader, hide previous results
    loader.style.display = 'block';
    summaryContainer.style.display = 'none';
    headlinesContainer.style.display = 'none';
    sentimentContainer.style.display = 'none';

    try {
      showStatus('Getting current tab content...');
      // Get current tab content
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Execute script to get page content
      showStatus('Extracting page content...');
      const [{result: pageContent}] = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          return {
            url: document.location.href,
            title: document.title,
            content: document.body.innerText
          };
        }
      });

      // Use the new agent-based workflow endpoint
      showStatus('Starting agent workflow...');
      
      const processResponse = await fetch(`${API_URL}/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt: prompt,
          pageContent: pageContent
        })
      });

      if (!processResponse.ok) {
        const errorData = await processResponse.json();
        throw new Error(`Processing failed: ${errorData.error || processResponse.statusText}`);
      }

      const results = await processResponse.json();
      
      // Display results
      showStatus('Analysis complete!');
      
      // Display summary if available
      if (results.summary) {
        summaryContainer.style.display = 'block';
        summaryResult.textContent = results.summary;
      }
      
      // Display headlines if available
      if (results.headlines && Array.isArray(results.headlines)) {
        headlinesContainer.style.display = 'block';
        headlinesResult.innerHTML = results.headlines.map(headline => 
          `<p>• ${headline}</p>`
        ).join('');
      }
      
      // Display sentiment if available
      if (results.sentiment) {
        sentimentContainer.style.display = 'block';
        sentimentResult.textContent = results.sentiment;
        
        // Add class based on sentiment
        const sentimentLower = results.sentiment.toLowerCase();
        if (sentimentLower.includes('positive')) {
          sentimentResult.className = 'positive';
        } else if (sentimentLower.includes('negative')) {
          sentimentResult.className = 'negative';
        } else {
          sentimentResult.className = 'neutral';
        }
      }
      
      // Remove the final_answer display - it's redundant with the sentiment analysis
      // Only use final_answer if no other results are available
      if (!results.summary && !results.headlines && !results.sentiment && results.final_answer) {
        const finalAnswerContainer = document.createElement('div');
        finalAnswerContainer.className = 'result-container';
        finalAnswerContainer.innerHTML = `
          <h2>Analysis Result</h2>
          <div>${results.final_answer}</div>
        `;
        document.querySelector('.results-section').appendChild(finalAnswerContainer);
      }

    } catch (error) {
      alert('An error occurred: ' + error.message);
      // Show error in UI
      summaryContainer.style.display = 'block';
      summaryResult.innerHTML = `<span style="color: red;">Error: ${error.message}</span>`;
    } finally {
      // Hide loader
      loader.style.display = 'none';
    }
  });
}); 