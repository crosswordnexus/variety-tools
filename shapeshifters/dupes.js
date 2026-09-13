/**
 * Dupe checking functionality using utils/dupe-checker.min.js & utils/variety.js
 */

function extractWordsFromText(text) {
  if (!text || !text.trim()) return [];
  const lines = text.split('\n');
  const words = [];
  for (let line of lines) {
    line = line.trim();
    if (!line || line.startsWith('#')) continue;
    // Strip "Slot 1:", "1. ", etc. and trailing comments/scores
    line = line.replace(/^(?:slot\s*\d+[\s\:\-]+|\d+[\.\:\-\)\s]+)/i, '').replace(/[;#].*$/, '').trim();
    const parts = line.split(/[\s\-]+/).filter(w => w.length > 0 && /^[A-Za-z]+$/.test(w));
    if (parts.length > 0) {
      words.push(parts.join(' '));
    }
  }
  return words;
}

// Single IPUZ dupe check
async function checkSingleDupes() {
  const el = document.getElementById('ipuz-solution-input');
  const words = el ? extractWordsFromText(el.value) : [];
  if (words.length === 0) {
    const container = document.querySelector('#dupe-alert-container-single');
    if (container) {
      container.innerHTML = '<div class="dupe-box dupe-warning">Please enter solution words first.</div>';
      container.style.display = 'block';
    }
    return;
  }
  await checkAndRenderDupes(words, '#dupe-alert-container-single', '#checkdupes-button-single');
}

// 4-Set IPUZ dupe check
async function checkMultiDupes() {
  const boxNames = ['multi-subgrid-1', 'multi-subgrid-2', 'multi-subgrid-3', 'multi-subgrid-4'];
  const words = [];
  boxNames.forEach(box => {
    const el = document.getElementById(box);
    if (!el) return;
    words.push(...extractWordsFromText(el.value));
  });

  if (words.length === 0) {
    const container = document.querySelector('#dupe-alert-container-multi');
    if (container) {
      container.innerHTML = '<div class="dupe-box dupe-warning">Please enter solution words first.</div>';
      container.style.display = 'block';
    }
    return;
  }

  await checkAndRenderDupes(words, '#dupe-alert-container-multi', '#checkdupes-button-multi');
}

// Event listeners
const singleBtn = document.getElementById('checkdupes-button-single');
if (singleBtn) {
  singleBtn.addEventListener('click', checkSingleDupes);
}

const multiBtn = document.getElementById('checkdupes-button-multi');
if (multiBtn) {
  multiBtn.addEventListener('click', checkMultiDupes);
}
