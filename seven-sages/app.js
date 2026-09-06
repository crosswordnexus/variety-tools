import { SevenSages, initWords, getWordScore, drawGrid } from './seven_sages.js';

const gridImage = new Image();
let solverReady = false;
let table = null;

async function init() {
  try {
    // Initialize DataTable
    table = $('#datatables-table').DataTable({
      paging: true,
      pageLength: 10,
      searching: true,
      ordering: true,
      order: []
    });

    // Start fetching the wordlist
    const wordListPromise = fetch('./spreadthewordlist.dict').then(res => res.text());

    // Load the image
    const imagePromise = new Promise((resolve, reject) => {
      gridImage.onload = () => resolve();
      gridImage.onerror = (e) => reject(e);
      gridImage.src = 'seven_sages.jpg';
    });

    // Also ensure DejaVuSans is fully loaded before drawing on canvas
    const fontPromise = document.fonts.ready;

    const [wordListText] = await Promise.all([wordListPromise, imagePromise, fontPromise]);

    initWords(wordListText);
    solverReady = true;

    // Load from localStorage
    let savedQuote = null;
    let savedEntries = null;
    try {
      savedQuote = localStorage.getItem('seven-sages-quote');
      savedEntries = localStorage.getItem('seven-sages-entries');
    } catch (e) {
      console.warn("localStorage not available:", e);
    }
    if (savedQuote !== null) {
      document.getElementById("quote").value = savedQuote;
    }
    if (savedEntries !== null) {
      document.getElementById("inputs").value = savedEntries;
    }

    loadVPuzMetadata();

    // hide loading and show main UI
    document.getElementById("loading").style.display = "none";
    document.getElementById("mainUI").style.display = "block";

    if (savedQuote || savedEntries) {
      findNextEntry();
    }
  } catch (e) {
    console.error(e);
    document.getElementById("loading").textContent = "Failed to load assets: " + e.message;
  }
}

async function findNextEntry(event) {
  if (event) event.preventDefault();

  if (!solverReady) {
    alert("Solver not yet initialized...");
    return;
  }

  document.getElementById("results-loading").innerHTML = '<span id="spinner"></span>Finding options...';
  document.getElementById("results-table-div").style.display = "none";

  // Let UI render the 'Finding options...' message
  await new Promise(resolve => setTimeout(resolve, 50));

  try {
    const quote = document.getElementById("quote").value.trim();
    const entriesVal = document.getElementById('inputs').value;
    const entries = entriesVal
      .split('\n')
      .map(line => line.trim())
      .filter(line => line !== '');

    try {
      localStorage.setItem('seven-sages-quote', quote);
      localStorage.setItem('seven-sages-entries', entriesVal);
    } catch (e) {
      console.warn("localStorage not available:", e);
    }

    const ss = new SevenSages(quote);
    for (let i = 0; i < entries.length; i++) {
      ss.set_word(entries[i], i);
    }

    const nextOptions = ss.find_next_entry_options();
    const dataUri = drawGrid(ss, gridImage, true);

    // Populate DataTable
    const tableData = nextOptions.map(item => [item.word, item.score]);
    table.clear().rows.add(tableData).draw();
    table.search('').draw();

    document.getElementById("myImg").src = dataUri;
  } catch (e) {
    console.error(e);
    alert("Error: " + e.message);
  } finally {
    document.getElementById("results-loading").textContent = '';
    document.getElementById("results-table-div").style.display = "block";
  }
}

// Row selection handler
$(document).on('click', '#datatables-table tbody tr', function() {
  const rowData = table.row(this).data();
  if (!rowData || !rowData[0]) return;
  const clickedWord = rowData[0];

  const textarea = document.getElementById('inputs');
  let val = textarea.value.trim();
  if (val) {
    val += '\n' + clickedWord;
  } else {
    val = clickedWord;
  }
  textarea.value = val;

  findNextEntry();
});

// Undo button handler
document.getElementById('undo').addEventListener('click', () => {
  const textarea = document.getElementById('inputs');
  const lines = textarea.value.split('\n').map(l => l.trim()).filter(l => l !== '');
  if (lines.length > 0) {
    lines.pop();
    textarea.value = lines.join('\n');
    findNextEntry();
  }
});

// Clear All button handler
document.getElementById('clear-all').addEventListener('click', () => {
  if (!confirm("Are you sure you want to clear all data? This will erase the quote, entries, and all saved progress.")) {
    return;
  }

  // Clear input fields
  document.getElementById('quote').value = '';
  document.getElementById('inputs').value = '';

  // Clear results and table
  document.getElementById('results-loading').textContent = '';
  if (table) {
    table.clear().draw();
    table.search('').draw();
  }

  // Reset grid image to base template
  if (gridImage && gridImage.src) {
    document.getElementById('myImg').src = gridImage.src;
  } else {
    document.getElementById('myImg').removeAttribute('src');
  }

  // Reset VPuz metadata
  document.getElementById('vpuz-title').value = '';
  document.getElementById('vpuz-author').value = '';
  document.getElementById('vpuz-copyright').value = '© ';
  document.getElementById('vpuz-notes').value = "Each answer in this puzzle is seven letters long and encircles the correspondingly numbered space, reading either clockwise (+) or counterclockwise (-) as indicated. The starting point of each answer is for you to determine. When the grid is correctly filled in, the letters in the outermost ring (reading clockwise from answer 1) will spell out a quote.";
  const vpuzContainer = document.getElementById('vpuz-clues-container');
  if (vpuzContainer) {
    vpuzContainer.innerHTML = '';
  }
  updateVPuzTab();

  // Clear localStorage
  try {
    const keysToRemove = [
      'seven-sages-quote',
      'seven-sages-entries',
      'seven-sages-vpuz-title',
      'seven-sages-vpuz-author',
      'seven-sages-vpuz-copyright',
      'seven-sages-vpuz-notes',
      'seven-sages-vpuz-clues'
    ];
    keysToRemove.forEach(k => localStorage.removeItem(k));
  } catch (e) {
    console.warn("localStorage not available:", e);
  }
});

document.querySelector("form").addEventListener("submit", findNextEntry);

// Tab switching logic
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('button-primary'));
    btn.classList.add('button-primary');

    const targetTab = btn.getAttribute('data-tab');
    document.querySelectorAll('.tab-content').forEach(content => {
      content.style.display = 'none';
    });
    document.getElementById(targetTab).style.display = 'block';

    if (targetTab === 'tab-vpuz') {
      updateVPuzTab();
    }
  });
});

function updateVPuzTab() {
  const quote = document.getElementById("quote").value.trim();
  const entriesVal = document.getElementById('inputs').value;
  const entries = entriesVal
    .split('\n')
    .map(line => line.trim())
    .filter(line => line !== '');

  const container = document.getElementById('vpuz-clues-container');
  const warning = document.getElementById('vpuz-warning');
  const downloadBtn = document.getElementById('vpuz-download');

  if (entries.length !== 36) {
    warning.style.display = 'block';
    warning.textContent = `Warning: You currently have ${entries.length} entries. You need exactly 36 entries to generate the vPuz file.`;
    container.style.display = 'none';
    downloadBtn.disabled = true;
    return;
  }

  warning.style.display = 'none';
  container.style.display = 'block';
  downloadBtn.disabled = false;

  let ss;
  try {
    ss = new SevenSages(quote);
    for (let i = 0; i < entries.length; i++) {
      ss.set_word(entries[i], i);
    }
  } catch (e) {
    warning.style.display = 'block';
    warning.textContent = `Error in grid configuration: ${e.message}`;
    container.style.display = 'none';
    downloadBtn.disabled = true;
    return;
  }

  let savedClues = [];
  try {
    const saved = localStorage.getItem('seven-sages-vpuz-clues');
    if (saved) savedClues = JSON.parse(saved);
  } catch (e) {
    console.warn(e);
  }

  let html = '<div class="row">';

  // Left column: Clues 1-18
  html += '<div class="six columns">';
  for (let i = 0; i < 18; i++) {
    const num = i + 1;
    const word = entries[i].toUpperCase();
    const dirSymbol = ss.directions[i] === '+' ? '(+)' : '(-)';
    const labelText = `${num} ${dirSymbol} (Word: ${word})`;
    const savedVal = savedClues[i] || '';
    html += `
      <div style="margin-bottom: 10px;">
        <label style="font-weight: normal; margin-bottom: 2px;">
          <strong>${labelText}</strong>
        </label>
        <input type="text" class="u-full-width vpuz-clue-input" data-index="${i}" value="${savedVal.replace(/"/g, '&quot;')}" placeholder="Enter clue here..." />
      </div>
    `;
  }
  html += '</div>';

  // Right column: Clues 19-36
  html += '<div class="six columns">';
  for (let i = 18; i < 36; i++) {
    const num = i + 1;
    const word = entries[i].toUpperCase();
    const dirSymbol = ss.directions[i] === '+' ? '(+)' : '(-)';
    const labelText = `${num} ${dirSymbol} (Word: ${word})`;
    const savedVal = savedClues[i] || '';
    html += `
      <div style="margin-bottom: 10px;">
        <label style="font-weight: normal; margin-bottom: 2px;">
          <strong>${labelText}</strong>
        </label>
        <input type="text" class="u-full-width vpuz-clue-input" data-index="${i}" value="${savedVal.replace(/"/g, '&quot;')}" placeholder="Enter clue here..." />
      </div>
    `;
  }
  html += '</div>';
  html += '</div>';
  container.innerHTML = html;

  const clueInputs = container.querySelectorAll('.vpuz-clue-input');
  clueInputs.forEach(input => {
    input.addEventListener('input', () => {
      const idx = parseInt(input.getAttribute('data-index'));
      savedClues[idx] = input.value;
      try {
        localStorage.setItem('seven-sages-vpuz-clues', JSON.stringify(savedClues));
      } catch (e) {
        console.warn(e);
      }
    });
  });
}

function loadVPuzMetadata() {
  try {
    const title = localStorage.getItem('seven-sages-vpuz-title');
    if (title !== null) document.getElementById('vpuz-title').value = title;

    const author = localStorage.getItem('seven-sages-vpuz-author');
    if (author !== null) document.getElementById('vpuz-author').value = author;

    const copyright = localStorage.getItem('seven-sages-vpuz-copyright');
    if (copyright !== null) document.getElementById('vpuz-copyright').value = copyright;

    const notes = localStorage.getItem('seven-sages-vpuz-notes');
    if (notes !== null) {
      document.getElementById('vpuz-notes').value = notes;
    } else {
      document.getElementById('vpuz-notes').value = "Each answer in this puzzle is seven letters long and encircles the correspondingly numbered space, reading either clockwise (+) or counterclockwise (-) as indicated. The starting point of each answer is for you to determine. When the grid is correctly filled in, the letters in the outermost ring (reading clockwise from answer 1) will spell out a quote.";
    }
  } catch (e) {
    console.warn(e);
  }
}

['vpuz-title', 'vpuz-author', 'vpuz-copyright', 'vpuz-notes'].forEach(id => {
  document.getElementById(id).addEventListener('input', (e) => {
    try {
      localStorage.setItem(`seven-sages-${id}`, e.target.value);
    } catch (err) {
      console.warn(err);
    }
  });
});

function downloadVPuzFile() {
  const quote = document.getElementById("quote").value.trim();
  const entries = document
    .getElementById('inputs')
    .value
    .split('\n')
    .map(line => line.trim())
    .filter(line => line !== '');

  if (entries.length !== 36) {
    alert("Error: Must have exactly 36 entries.");
    return;
  }

  let ss;
  try {
    ss = new SevenSages(quote);
    for (let i = 0; i < entries.length; i++) {
      ss.set_word(entries[i], i);
    }
  } catch (e) {
    alert(`Error in grid configuration: ${e.message}`);
    return;
  }

  let chars = [];
  for (let r = 0; r < ss.rows.length; r++) {
    for (let c = 0; c < ss.rows[r].length; c++) {
      const char = ss.rows[r][c].toUpperCase();
      if (char && char !== '.') {
        chars.push(char);
      }
    }
  }
  chars.sort();
  const solutionString = chars.join('');

  const title = document.getElementById('vpuz-title').value.trim() || 'Stained Glass';
  const author = document.getElementById('vpuz-author').value.trim() || 'Alex Boisvert';
  const copyright = document.getElementById('vpuz-copyright').value.trim() || '© 2026 Crossword Nexus';
  const notes = document.getElementById('vpuz-notes').value.trim();

  const clueInputs = document.querySelectorAll('.vpuz-clue-input');
  const cluesArr = [];
  for (let i = 0; i < 36; i++) {
    const num = i + 1;
    const dirSymbol = ss.directions[i] === '+' ? '(+)' : '(-)';
    let clueText = '';
    const matchingInput = Array.from(clueInputs).find(input => parseInt(input.getAttribute('data-index')) === i);
    if (matchingInput) {
      clueText = matchingInput.value.trim();
    }
    cluesArr.push([`${num} ${dirSymbol}`, clueText]);
  }

  const base64Image = drawGrid(ss, gridImage, false);

  const vpuzObj = {
    author: author,
    title: title,
    copyright: copyright,
    "solution-string": solutionString,
    notes: notes,
    clues: {
      "Clues": cluesArr
    },
    "puzzle-image": base64Image
  };

  const jsonString = JSON.stringify(vpuzObj, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${title.toLowerCase().replace(/[^a-z0-9]+/g, '_')}.vpuz`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

document.getElementById('vpuz-download').addEventListener('click', downloadVPuzFile);

init();
