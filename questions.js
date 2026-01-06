// Loaded before game.js to provide quiz data by loading from ai-engr.json
// This script loads the questions data asynchronously
(async function() {
  try {
    const response = await fetch('./data/ai-engr.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    window._Question = await response.json();
    console.log('Questions loaded successfully from ai-engr.json');
  } catch (error) {
    console.error('Failed to load questions from ai-engr.json:', error);
    // Fallback: Initialize with empty object
    window._Question = {};
  }
})();
