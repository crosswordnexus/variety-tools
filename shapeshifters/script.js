/**
 * Shapeshifters / Moving Staircases - Batch File Generator
 */

(function () {
  // DOM Elements
  const sizeSlider = document.getElementById('size-slider');
  const sizeInput = document.getElementById('size-input');
  const sizeDisplay = document.getElementById('size-display');
  const statShorts = document.getElementById('stat-shorts');
  const statLongs = document.getElementById('stat-longs');
  const statLetters = document.getElementById('stat-letters');
  const optComments = document.getElementById('opt-comments');
  const batchOutput = document.getElementById('batch-output');
  const copyBtn = document.getElementById('copy-btn');
  const downloadBtn = document.getElementById('download-btn');
  const gridContainer = document.getElementById('grid-container');
  const hoverCellInfo = document.getElementById('hover-cell-info');
  const viewButtons = document.querySelectorAll('.toggle-btn');
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabContents = document.querySelectorAll('.tab-content');

  // IPUZ DOM Elements
  const ipuzTitle = document.getElementById('ipuz-title');
  const ipuzAuthor = document.getElementById('ipuz-author');
  const ipuzCopyright = document.getElementById('ipuz-copyright');
  const ipuzSizeDisplay = document.getElementById('ipuz-size-display');
  const ipuzSizeSummary = document.getElementById('ipuz-size-summary');
  const cluesCountShorts = document.getElementById('clues-count-shorts');
  const cluesLenShorts = document.getElementById('clues-len-shorts');
  const cluesCountLongs = document.getElementById('clues-count-longs');
  const cluesLenLongs = document.getElementById('clues-len-longs');
  const ipuzSolutionInput = document.getElementById('ipuz-solution-input');
  const solutionStatus = document.getElementById('solution-status');
  const ipuzCluesInput = document.getElementById('ipuz-clues-input');
  const cluesStatus = document.getElementById('clues-status');
  const ipuzJsonOutput = document.getElementById('ipuz-json-output');
  const ipuzDownloadBtn = document.getElementById('ipuz-download-btn');
  const ipuzCopyBtn = document.getElementById('ipuz-copy-btn');
  const btnModeEasier = document.getElementById('btn-mode-easier');
  const btnModeHarder = document.getElementById('btn-mode-harder');
  const modeDescription = document.getElementById('mode-description');
  const downloadBtnLabel = document.getElementById('download-btn-label');

  let currentView = 'base'; // 'base' | 'shorts' | 'longs'
  let currentIpuzMode = 'easier'; // 'easier' | 'harder'

  // Tab switching
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTabId = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetContent = document.getElementById(targetTabId);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });

  // View toggling for grid
  viewButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      viewButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentView = btn.getAttribute('data-view');
      renderGrid();
    });
  });

  // Generate slot definitions (SW to NE diagonal: r + c = n)
  function generateSlots(n) {
    const shorts = [];
    const longs = [];

    // Cell mapping to check memberships
    const cellMap = {};

    // 1. Shorts: Horizontal push (LR slides left by 1)
    // Produces (n + 1) words of length n
    for (let r = 0; r <= n; r++) {
      const slot = [];
      // Upper-Left part (cols 0 .. n-1-r)
      if (r < n) {
        for (let c = 0; c <= n - 1 - r; c++) {
          const id = `r${r}c${c}`;
          slot.push(id);
          if (!cellMap[id]) cellMap[id] = { id, row: r, col: c, part: 'UL' };
          cellMap[id].shortIdx = r + 1;
        }
      }
      // Lower-Right part (cols n-r+1 .. n)
      if (r > 0) {
        for (let c = n - r + 1; c <= n; c++) {
          const id = `r${r}c${c}`;
          slot.push(id);
          if (!cellMap[id]) cellMap[id] = { id, row: r, col: c, part: 'LR' };
          cellMap[id].shortIdx = r + 1;
        }
      }
      shorts.push(slot);
    }

    // 2. Longs: Vertical push (LR slides up by 1)
    // Produces n words of length (n + 1)
    for (let r = 0; r < n; r++) {
      const slot = [];
      // UL row r: cols 0 .. n-1-r
      for (let c = 0; c <= n - 1 - r; c++) {
        const id = `r${r}c${c}`;
        slot.push(id);
        cellMap[id].longIdx = r + 1;
      }
      // LR row r+1: cols n-r .. n
      for (let c = n - r; c <= n; c++) {
        const id = `r${r + 1}c${c}`;
        slot.push(id);
        cellMap[id].longIdx = r + 1;
      }
      longs.push(slot);
    }

    return { shorts, longs, cellMap };
  }

  // Format batch output
  function formatBatchText(n, shorts, longs) {
    const includeComments = optComments.checked;
    const lines = [];

    if (includeComments) {
      lines.push(`# Shapeshifter / Moving Staircases Batch File (N = ${n})`);
      lines.push(`# Shorts: ${shorts.length} words of length ${n}`);
      lines.push(`# Longs: ${longs.length} words of length ${n + 1}`);
      lines.push(`# Total letters: ${n * (n + 1)}`);
      lines.push('');
      lines.push(`# --- Shorts (length ${n}) ---`);
    }

    shorts.forEach((slot, i) => {
      const comment = includeComments ? ` # Short ${i + 1}` : '';
      lines.push(`${slot.join(' ')}${comment}`);
    });

    if (includeComments) {
      lines.push('');
      lines.push(`# --- Longs (length ${n + 1}) ---`);
    }

    longs.forEach((slot, j) => {
      const comment = includeComments ? ` # Long ${j + 1}` : '';
      lines.push(`${slot.join(' ')}${comment}`);
    });

    lines.push('');
    return lines.join('\n');
  }

  // Render Visual Grid
  function renderGrid() {
    const n = parseInt(sizeInput.value, 10);
    const { shorts, longs, cellMap } = generateSlots(n);

    gridContainer.innerHTML = '';
    const gridEl = document.createElement('div');
    gridEl.className = 'puzzle-grid';

    if (currentView === 'base') {
      // (n + 1) rows x (n + 1) cols
      const cols = n + 1;
      const rows = n + 1;
      gridEl.style.gridTemplateColumns = `repeat(${cols}, 28px)`;
      gridEl.style.gridTemplateRows = `repeat(${rows}, 28px)`;

      for (let r = 0; r <= n; r++) {
        for (let c = 0; c <= n; c++) {
          const cell = document.createElement('div');
          cell.className = 'puzzle-cell';

          if ((r === 0 && c === n) || (r === n && c === 0)) {
            cell.classList.add('cell-void');
          } else if (r + c === n && r > 0 && r < n) {
            cell.classList.add('cell-blk');
            cell.title = `Block (r${r}c${c})`;
          } else if (r + c < n) {
            // Upper-Left
            const id = `r${r}c${c}`;
            cell.classList.add('cell-ul');
            setupCellInteractions(cell, id, cellMap[id]);
          } else {
            // Lower-Right
            const id = `r${r}c${c}`;
            cell.classList.add('cell-lr');
            setupCellInteractions(cell, id, cellMap[id]);
          }

          gridEl.appendChild(cell);
        }
      }
    } else if (currentView === 'shorts') {
      // (n + 1) rows x n cols
      gridEl.style.gridTemplateColumns = `repeat(${n}, 28px)`;
      gridEl.style.gridTemplateRows = `repeat(${n + 1}, 28px)`;

      shorts.forEach((slot) => {
        slot.forEach(cellId => {
          const info = cellMap[cellId];
          const cell = document.createElement('div');
          cell.className = 'puzzle-cell';
          cell.classList.add(info.part === 'UL' ? 'cell-ul' : 'cell-lr');
          setupCellInteractions(cell, cellId, info);
          gridEl.appendChild(cell);
        });
      });
    } else if (currentView === 'longs') {
      // n rows x (n + 1) cols
      gridEl.style.gridTemplateColumns = `repeat(${n + 1}, 28px)`;
      gridEl.style.gridTemplateRows = `repeat(${n}, 28px)`;

      longs.forEach((slot) => {
        slot.forEach(cellId => {
          const info = cellMap[cellId];
          const cell = document.createElement('div');
          cell.className = 'puzzle-cell';
          cell.classList.add(info.part === 'UL' ? 'cell-ul' : 'cell-lr');
          setupCellInteractions(cell, cellId, info);
          gridEl.appendChild(cell);
        });
      });
    }

    gridContainer.appendChild(gridEl);
  }

  function setupCellInteractions(cellEl, cellId, info) {
    cellEl.textContent = '';
    cellEl.dataset.cellId = cellId;

    cellEl.addEventListener('mouseenter', () => {
      if (info) {
        hoverCellInfo.textContent = `Cell ${cellId} [${info.part}]: Short #${info.shortIdx} (Row ${info.shortIdx}), Long #${info.longIdx} (Row ${info.longIdx})`;
      }
    });

    cellEl.addEventListener('mouseleave', () => {
      hoverCellInfo.innerHTML = '&nbsp;';
    });
  }

  // Update everything
  function updateAll() {
    const n = parseInt(sizeInput.value, 10);
    if (isNaN(n) || n < 2) return;

    sizeDisplay.textContent = n;
    const numShorts = n + 1;
    const lenShorts = n;
    const numLongs = n;
    const lenLongs = n + 1;
    const totalLetters = n * (n + 1);

    statShorts.textContent = `${numShorts} words × ${lenShorts} letters`;
    statLongs.textContent = `${numLongs} words × ${lenLongs} letters`;
    statLetters.textContent = `${totalLetters} letters`;

    const { shorts, longs } = generateSlots(n);
    batchOutput.value = formatBatchText(n, shorts, longs);

    renderGrid();

    // Update IPUZ tab summary
    if (ipuzSizeDisplay) ipuzSizeDisplay.textContent = n;
    if (ipuzSizeSummary) ipuzSizeSummary.textContent = `${numShorts} Shorts × ${numLongs} Longs`;
    if (cluesCountShorts) cluesCountShorts.textContent = numShorts;
    if (cluesLenShorts) cluesLenShorts.textContent = lenShorts;
    if (cluesCountLongs) cluesCountLongs.textContent = numLongs;
    if (cluesLenLongs) cluesLenLongs.textContent = lenLongs;

    generateIpuz();
  }

  // --- IPUZ CREATOR LOGIC ---

  // Helper functions for clue length tags
  function getLengthTag(wordObj, defaultLen) {
    const len = (wordObj && wordObj.length) ? wordObj.length : defaultLen;
    const wc = (wordObj && wordObj.wordCount) ? wordObj.wordCount : 1;
    const hasHyph = (wordObj && wordObj.hasHyphen) ? true : false;

    const parts = [len];
    if (wc > 1) {
      parts.push(`${wc} words`);
    }
    if (hasHyph) {
      parts.push('hyph.');
    }
    return `(${parts.join(', ')})`;
  }

  function appendTagToClue(clueText, tag) {
    if (!clueText || !clueText.trim()) return tag;
    let cleaned = clueText.trim();
    // Strip outer square brackets if present: "[Clue text]" -> "Clue text"
    if (cleaned.startsWith('[') && cleaned.endsWith(']')) {
      cleaned = cleaned.slice(1, -1).trim();
    }
    // Remove any existing trailing tag like (4), (7, 2 words), (12, 2 words, hyph.), (6, hyph.), etc.
    cleaned = cleaned.replace(/\s*\(\s*(?:\d+[^)]*|\d+\s*w(?:or)?ds?\.?|hyph\.?)\s*\)\s*$/i, '').trim();
    return `${cleaned} ${tag}`;
  }

  // Parse words from Ingrid output (supports multi-word phrases separated by spaces and hyphenated words)
  function parseSolutionWords(text, n) {
    if (!text || !text.trim()) return { shorts: [], longs: [], allWords: [] };
    const lines = text.split('\n');
    const words = [];
    for (const rawLine of lines) {
      let line = rawLine.trim();
      if (!line || line.startsWith('#')) continue;
      // Strip "Slot 1:", "1. ", etc. and any trailing comments/scores
      line = line.replace(/^(?:slot\s*\d+[\s\:\-]+|\d+[\.\:\-\)\s]+)/i, '').replace(/[;#].*$/, '').trim();
      if (!line) continue;

      // Detect if entry contains a hyphen connecting letters (e.g. "SEE-SAW" or "T-SHIRT")
      const hasHyphen = /[A-Za-z]\s*-\s*[A-Za-z]/.test(line);

      // Normalize hyphen spacing: "SEE - SAW" -> "SEE-SAW"
      const normalizedLine = line.replace(/([A-Za-z])\s*-\s*([A-Za-z])/g, '$1-$2');

      // Separate words by whitespace
      const tokens = normalizedLine.split(/\s+/).filter(t => /[A-Za-z]/.test(t));
      if (tokens.length > 0) {
        // Extract raw letters for grid filling (excluding spaces and hyphens)
        const letters = normalizedLine.replace(/[^A-Za-z]/g, '').toUpperCase();
        if (letters.length >= 2) {
          words.push({
            raw: tokens.join(' ').toUpperCase(),
            letters: letters,
            wordCount: tokens.length,
            hasHyphen: hasHyphen,
            length: letters.length
          });
        }
      }
    }
    const shortsCount = n + 1;
    const longsCount = n;
    const shorts = words.slice(0, shortsCount);
    const longs = words.slice(shortsCount, shortsCount + longsCount);
    return { shorts, longs, allWords: words };
  }

  // Parse clues from single textarea
  function parseClues(text, n) {
    if (!text || !text.trim()) return { shortsClues: [], longsClues: [] };
    const rawLines = text.split('\n');

    let inShorts = false;
    let inLongs = false;
    let hasHeaders = false;
    const sectionShorts = [];
    const sectionLongs = [];

    for (const rawLine of rawLines) {
      const line = rawLine.trim();
      if (!line) continue;
      if (/^#?\s*shorts/i.test(line)) {
        inShorts = true;
        inLongs = false;
        hasHeaders = true;
        continue;
      }
      if (/^#?\s*longs/i.test(line)) {
        inLongs = true;
        inShorts = false;
        hasHeaders = true;
        continue;
      }
      // Strip leading numbering like "1. ", "1: ", "1 - ", "1) "
      const cleaned = line.replace(/^\d+[\.\-\:\)\s]+\s*/, '').trim();
      if (inShorts) {
        sectionShorts.push(cleaned);
      } else if (inLongs) {
        sectionLongs.push(cleaned);
      }
    }

    if (hasHeaders) {
      return { shortsClues: sectionShorts, longsClues: sectionLongs };
    }

    // Default: split sequentially (first n+1 for shorts, next n for longs)
    const cleanLines = rawLines
      .map(l => l.trim())
      .filter(l => l && !l.startsWith('#'))
      .map(l => l.replace(/^\d+[\.\-\:\)\s]+\s*/, '').trim());

    const shortsClues = cleanLines.slice(0, n + 1);
    const longsClues = cleanLines.slice(n + 1, n + 1 + n);
    return { shortsClues, longsClues };
  }

  // Update validation and status displays for IPUZ tab
  function updateStatuses(n, solData, cluesData) {
    const totalWordsExpected = 2 * n + 1;
    if (solutionStatus) {
      if (solData.allWords.length === 0) {
        solutionStatus.className = 'status-indicator';
        solutionStatus.textContent = 'Waiting for solution input...';
      } else if (solData.allWords.length >= totalWordsExpected) {
        // Check crossing consistency
        let mismatches = 0;
        for (let r = 0; r < n; r++) {
          const longObj = solData.longs[r];
          const shortULObj = solData.shorts[r];
          const shortLRObj = solData.shorts[r + 1];
          if (longObj && shortULObj && shortLRObj) {
            const longLetters = longObj.letters;
            const ulShortLetters = shortULObj.letters;
            const lrShortLetters = shortLRObj.letters;
            // UL overlap
            const ulLong = longLetters.slice(0, n - r);
            const ulShort = ulShortLetters.slice(0, n - r);
            if (ulLong !== ulShort) mismatches++;
            // LR overlap
            const lrLong = longLetters.slice(n - r);
            const lrShort = lrShortLetters.slice(lrShortLetters.length - (r + 1));
            if (lrLong !== lrShort) mismatches++;
          }
        }
        if (mismatches === 0) {
          solutionStatus.className = 'status-indicator status-ok';
          solutionStatus.textContent = `✓ All ${totalWordsExpected} words loaded and all intersecting letters match!`;
        } else {
          solutionStatus.className = 'status-indicator status-warn';
          solutionStatus.textContent = `⚠️ Loaded ${totalWordsExpected} words, but found ${mismatches} mismatching crossing(s).`;
        }
      } else {
        solutionStatus.className = 'status-indicator status-warn';
        solutionStatus.textContent = `Loaded ${solData.allWords.length} of ${totalWordsExpected} expected words (${n + 1} Shorts, ${n} Longs).`;
      }
    }

    if (cluesStatus) {
      const totalClues = cluesData.shortsClues.length + cluesData.longsClues.length;
      if (totalClues === 0) {
        cluesStatus.className = 'status-indicator';
        cluesStatus.textContent = 'Waiting for clues...';
      } else if (cluesData.shortsClues.length === n + 1 && cluesData.longsClues.length === n) {
        cluesStatus.className = 'status-indicator status-ok';
        cluesStatus.textContent = `✓ All ${totalWordsExpected} clues loaded (${n + 1} Shorts, ${n} Longs)!`;
      } else {
        cluesStatus.className = 'status-indicator status-warn';
        cluesStatus.textContent = `Found ${cluesData.shortsClues.length} / ${n + 1} Shorts clues and ${cluesData.longsClues.length} / ${n} Longs clues.`;
      }
    }
  }

  // Generate the complete IPUZ JSON structure
  function generateIpuz() {
    const n = parseInt(sizeInput.value, 10);
    if (isNaN(n) || n < 2) return null;

    const title = (ipuzTitle ? ipuzTitle.value.trim() : '') || 'Shapeshifter';
    const author = ipuzAuthor ? ipuzAuthor.value.trim() : '';
    const copyright = ipuzCopyright ? ipuzCopyright.value.trim() : '';

    const solData = parseSolutionWords(ipuzSolutionInput ? ipuzSolutionInput.value : '', n);
    const cluesData = parseClues(ipuzCluesInput ? ipuzCluesInput.value : '', n);

    updateStatuses(n, solData, cluesData);

    const dims = n + 1;
    const puzzle = [];
    const solution = [];

    // Initialize (n+1) x (n+1) grid
    for (let r = 0; r <= n; r++) {
      const pRow = [];
      const sRow = [];
      for (let c = 0; c <= n; c++) {
        if ((r === 0 && c === n) || (r === n && c === 0)) {
          pRow.push(null);
          sRow.push(null);
        } else if (r + c === n) {
          pRow.push('#');
          sRow.push('#');
        } else {
          pRow.push(0);
          sRow.push(null);
        }
      }
      puzzle.push(pRow);
      solution.push(sRow);
    }

    // Fill solution letters from shorts
    if (solData.shorts.length > 0) {
      for (let r = 0; r <= n; r++) {
        const wordObj = solData.shorts[r];
        if (!wordObj) continue;
        const letters = wordObj.letters;
        let idx = 0;
        // Upper-Left part
        if (r < n) {
          for (let c = 0; c <= n - 1 - r; c++) {
            if (idx < letters.length) solution[r][c] = letters[idx++];
          }
        }
        // Lower-Right part
        if (r > 0) {
          for (let c = n - r + 1; c <= n; c++) {
            if (idx < letters.length) solution[r][c] = letters[idx++];
          }
        }
      }
    }

    // Prepare clue texts with length tags appended (e.g. "Clue text (6)" or "Clue text (6, 2 words)")
    const shortsClueTexts = [];
    for (let r = 0; r <= n; r++) {
      const rawClue = cluesData.shortsClues[r] || '';
      const tag = getLengthTag(solData.shorts[r], n);
      shortsClueTexts.push(rawClue ? appendTagToClue(rawClue, tag) : tag);
    }

    const longsClueTexts = [];
    for (let r = 0; r < n; r++) {
      const rawClue = cluesData.longsClues[r] || '';
      const tag = getLengthTag(solData.longs[r], n + 1);
      longsClueTexts.push(rawClue ? appendTagToClue(rawClue, tag) : tag);
    }

    if (currentIpuzMode === 'harder') {
      shortsClueTexts.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }));
      longsClueTexts.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }));
    }

    // Clues with explicit 1-based [x, y] cells
    // (Cells remain in original slot order even when clue texts are alphabetized)
    // Shorts (Horizontal): (n + 1) rows
    const shortsList = [];
    for (let r = 0; r <= n; r++) {
      const cells = [];
      if (r < n) {
        for (let c = 0; c <= n - 1 - r; c++) {
          cells.push([c + 1, r + 1]);
        }
      }
      if (r > 0) {
        for (let c = n - r + 1; c <= n; c++) {
          cells.push([c + 1, r + 1]);
        }
      }
      shortsList.push({
        number: "•",
        clue: shortsClueTexts[r] || '',
        cells: cells
      });
    }

    // Longs (Vertical): n rows
    const longsList = [];
    for (let r = 0; r < n; r++) {
      const cells = [];
      // UL row r: cols 0 .. n-1-r
      for (let c = 0; c <= n - 1 - r; c++) {
        cells.push([c + 1, r + 1]);
      }
      // LR row r+1: cols n-r .. n
      for (let c = n - r; c <= n; c++) {
        cells.push([c + 1, r + 2]);
      }
      longsList.push({
        number: "•",
        clue: longsClueTexts[r] || '',
        cells: cells
      });
    }

    const ipuzData = {
      version: 'http://ipuz.org/v2',
      kind: ['http://ipuz.org/crossword#1'],
      dimensions: {
        width: dims,
        height: dims
      },
      title: title,
      author: author,
      copyright: copyright
    };

    if (currentIpuzMode === 'harder') {
      ipuzData.fakeclues = "true";
      ipuzData.realwords = "true";
    }

    ipuzData.puzzle = puzzle;
    ipuzData.solution = solution;
    ipuzData.clues = {
      [`Shorts (${n})`]: shortsList,
      [`Longs (${n + 1})`]: longsList
    };

    if (ipuzJsonOutput) {
      ipuzJsonOutput.value = JSON.stringify(ipuzData, null, 2);
    }

    return ipuzData;
  }

  // Mode switching (Easier vs Harder)
  if (btnModeEasier) {
    btnModeEasier.addEventListener('click', () => {
      currentIpuzMode = 'easier';
      btnModeEasier.classList.add('active');
      if (btnModeHarder) btnModeHarder.classList.remove('active');
      if (modeDescription) {
        modeDescription.innerHTML = '<strong>Easier:</strong> Clues in grid order. Compatible with all IPUZ solvers.';
      }
      if (downloadBtnLabel) downloadBtnLabel.textContent = 'Download .ipuz';
      generateIpuz();
    });
  }

  if (btnModeHarder) {
    btnModeHarder.addEventListener('click', () => {
      currentIpuzMode = 'harder';
      btnModeHarder.classList.add('active');
      if (btnModeEasier) btnModeEasier.classList.remove('active');
      if (modeDescription) {
        modeDescription.innerHTML = '<strong>Harder:</strong> Alphabetized clues with <code>fakeclues</code> & <code>realwords</code> for Crossword Nexus solver.';
      }
      if (downloadBtnLabel) downloadBtnLabel.textContent = 'Download Harder .ipuz';
      generateIpuz();
    });
  }

  // IPUZ Event Listeners
  if (ipuzTitle) ipuzTitle.addEventListener('input', generateIpuz);
  if (ipuzAuthor) ipuzAuthor.addEventListener('input', generateIpuz);
  if (ipuzCopyright) ipuzCopyright.addEventListener('input', generateIpuz);
  if (ipuzSolutionInput) ipuzSolutionInput.addEventListener('input', generateIpuz);
  if (ipuzCluesInput) ipuzCluesInput.addEventListener('input', generateIpuz);

  // Copy IPUZ JSON
  if (ipuzCopyBtn) {
    ipuzCopyBtn.addEventListener('click', () => {
      const text = ipuzJsonOutput.value;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(showIpuzCopiedState);
      } else {
        ipuzJsonOutput.select();
        document.execCommand('copy');
        showIpuzCopiedState();
      }
    });
  }

  function showIpuzCopiedState() {
    const orig = ipuzCopyBtn.innerHTML;
    ipuzCopyBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
      Copied!
    `;
    ipuzCopyBtn.style.backgroundColor = '#16a34a';
    ipuzCopyBtn.style.color = '#ffffff';
    setTimeout(() => {
      ipuzCopyBtn.innerHTML = orig;
      ipuzCopyBtn.style.backgroundColor = '';
      ipuzCopyBtn.style.color = '';
    }, 1800);
  }

  // Download .ipuz file
  if (ipuzDownloadBtn) {
    ipuzDownloadBtn.addEventListener('click', () => {
      const ipuzObj = generateIpuz();
      if (!ipuzObj) return;
      const jsonText = JSON.stringify(ipuzObj, null, 2);
      const titleSlug = (ipuzObj.title || 'shapeshifter').toLowerCase().replace(/[^a-z0-9]/g, '_');
      const suffix = currentIpuzMode === 'harder' ? '_harder' : '_easier';
      const blob = new Blob([jsonText], { type: 'application/json;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${titleSlug}${suffix}.ipuz`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // Sync inputs
  sizeSlider.addEventListener('input', () => {
    sizeInput.value = sizeSlider.value;
    updateAll();
  });

  sizeInput.addEventListener('input', () => {
    let val = parseInt(sizeInput.value, 10);
    if (val < 2) val = 2;
    if (val > 15) val = 15;
    sizeSlider.value = val;
    updateAll();
  });

  optComments.addEventListener('change', updateAll);

  // Copy to clipboard
  copyBtn.addEventListener('click', () => {
    const text = batchOutput.value;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(showCopiedState);
    } else {
      batchOutput.select();
      document.execCommand('copy');
      showCopiedState();
    }
  });

  function showCopiedState() {
    const originalText = copyBtn.innerHTML;
    copyBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
      Copied!
    `;
    copyBtn.style.backgroundColor = '#16a34a';
    setTimeout(() => {
      copyBtn.innerHTML = originalText;
      copyBtn.style.backgroundColor = '';
    }, 1800);
  }

  // Download file
  downloadBtn.addEventListener('click', () => {
    const n = sizeInput.value;
    const text = batchOutput.value;
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `shapeshifter_N${n}_batch.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });

  // --- 4-SET IPUZ CREATOR LOGIC ---
  const multiTitle = document.getElementById('multi-title');
  const multiAuthor = document.getElementById('multi-author');
  const multiCopyright = document.getElementById('multi-copyright');
  const multiSubgrid1 = document.getElementById('multi-subgrid-1');
  const multiSubgrid2 = document.getElementById('multi-subgrid-2');
  const multiSubgrid3 = document.getElementById('multi-subgrid-3');
  const multiSubgrid4 = document.getElementById('multi-subgrid-4');
  const multiStatus1 = document.getElementById('multi-status-1');
  const multiStatus2 = document.getElementById('multi-status-2');
  const multiStatus3 = document.getElementById('multi-status-3');
  const multiStatus4 = document.getElementById('multi-status-4');
  const multiTotalWordsStatus = document.getElementById('multi-total-words-status');
  const multiCluesInput = document.getElementById('multi-clues-input');
  const multiCluesStatus = document.getElementById('multi-clues-status');
  const multiIpuzDownloadBtn = document.getElementById('multi-ipuz-download-btn');
  const multiIpuzCopyBtn = document.getElementById('multi-ipuz-copy-btn');
  const multiIpuzJsonOutput = document.getElementById('multi-ipuz-json-output');

  // Subgrid layout specifications
  // Order: 4x5 (N=4), 5x6 (N=5), 6x7 (N=6), 7x8 (N=7)
  const SUBGRIDS_CONFIG = [
    { id: 1, n: 4, name: '4x5', label: 'Top-Left', rOff: 0, cOff: 3, textarea: multiSubgrid1, status: multiStatus1, expectedWords: 9 },
    { id: 2, n: 5, name: '5x6', label: 'Top-Right', rOff: 0, cOff: 9, textarea: multiSubgrid2, status: multiStatus2, expectedWords: 11 },
    { id: 3, n: 6, name: '6x7', label: 'Bottom-Right', rOff: 7, cOff: 9, textarea: multiSubgrid3, status: multiStatus3, expectedWords: 13 },
    { id: 4, n: 7, name: '7x8', label: 'Bottom-Left', rOff: 7, cOff: 0, textarea: multiSubgrid4, status: multiStatus4, expectedWords: 15 }
  ];

  // Helper to detect if a line is a section header (e.g. "# 4", "Shorts:", "Length 4")
  function isHeaderLine(line) {
    if (line.startsWith('#')) return true;
    const trimmed = line.trim();
    if (/^(?:shorts|longs)\s*:?$/i.test(trimmed)) return true;
    if (/^(?:length\s*\d+|\d+[\s\-]*(?:letters?|words?)|subgrid\s*\d+)\s*:?$/i.test(trimmed)) return true;
    return false;
  }

  // Parse clues for 4-Set (48 clues total in slot order)
  function parseMultiClues(text) {
    if (!text || !text.trim()) return [];
    const rawLines = text.split('\n');
    const cleanLines = [];

    for (const rawLine of rawLines) {
      let line = rawLine.trim();
      if (!line || isHeaderLine(line)) continue;
      // Strip outer square brackets if present: "[Clue text]" -> "Clue text"
      if (line.startsWith('[') && line.endsWith(']')) {
        line = line.slice(1, -1).trim();
      }
      // Strip leading numbering: "1. ", "1: ", "1 - ", "1) ", "[1] ", "(1) "
      line = line.replace(/^(?:\[\d+\]|\(\d+\)|\d+[\.\-\:\)\s])\s*/, '').trim();
      if (line) {
        cleanLines.push(line);
      }
    }
    return cleanLines;
  }

  function generateMultiIpuz() {
    if (!multiIpuzJsonOutput) return null;

    const title = (multiTitle ? multiTitle.value.trim() : '') || 'Shapeshifters Set';
    const author = multiAuthor ? multiAuthor.value.trim() : '';
    const copyright = multiCopyright ? multiCopyright.value.trim() : '';

    // Canvas size: 16 wide, 15 high
    const canvasWidth = 16;
    const canvasHeight = 15;

    const puzzle = [];
    const solution = [];
    for (let r = 0; r < canvasHeight; r++) {
      puzzle.push(new Array(canvasWidth).fill(null));
      solution.push(new Array(canvasWidth).fill(null));
    }

    let totalWordsLoaded = 0;

    // Process each subgrid
    SUBGRIDS_CONFIG.forEach(cfg => {
      const text = cfg.textarea ? cfg.textarea.value : '';
      const solData = parseSolutionWords(text, cfg.n);
      totalWordsLoaded += solData.allWords.length;

      // Update individual status & check crossings
      if (cfg.status) {
        if (solData.allWords.length === 0) {
          cfg.status.className = 'status-indicator';
          cfg.status.textContent = 'Waiting for input...';
        } else if (solData.allWords.length === cfg.expectedWords) {
          let mismatches = 0;
          for (let r = 0; r < cfg.n; r++) {
            const longObj = solData.longs[r];
            const shortULObj = solData.shorts[r];
            const shortLRObj = solData.shorts[r + 1];
            if (longObj && shortULObj && shortLRObj) {
              const ulLong = longObj.letters.slice(0, cfg.n - r);
              const ulShort = shortULObj.letters.slice(0, cfg.n - r);
              if (ulLong !== ulShort) mismatches++;
              const lrLong = longObj.letters.slice(cfg.n - r);
              const lrShort = shortLRObj.letters.slice(shortLRObj.letters.length - (r + 1));
              if (lrLong !== lrShort) mismatches++;
            }
          }
          if (mismatches === 0) {
            cfg.status.className = 'status-indicator status-ok';
            cfg.status.textContent = `✓ ${solData.allWords.length}/${cfg.expectedWords} words loaded (crossings match)`;
          } else {
            cfg.status.className = 'status-indicator status-warn';
            cfg.status.textContent = `⚠️ Loaded ${solData.allWords.length} words, but found ${mismatches} mismatching crossing(s)`;
          }
        } else {
          cfg.status.className = 'status-indicator status-warn';
          cfg.status.textContent = `Loaded ${solData.allWords.length}/${cfg.expectedWords} words`;
        }
      }

      // Populate canvas cells for this subgrid
      const n = cfg.n;
      const R_off = cfg.rOff;
      const C_off = cfg.cOff;

      for (let r = 0; r <= n; r++) {
        for (let c = 0; c <= n; c++) {
          const R = r + R_off;
          const C = c + C_off;

          if ((r === 0 && c === n) || (r === n && c === 0)) {
            puzzle[R][C] = null;
            solution[R][C] = null;
          } else if (r + c === n) {
            puzzle[R][C] = '#';
            solution[R][C] = '#';
          } else {
            puzzle[R][C] = 0;
            solution[R][C] = null;
          }
        }
      }

      // Populate solution letters from subgrid shorts
      if (solData.shorts.length > 0) {
        for (let r = 0; r <= n; r++) {
          const wordObj = solData.shorts[r];
          if (!wordObj) continue;
          const letters = wordObj.letters;
          let idx = 0;
          if (r < n) {
            for (let c = 0; c <= n - 1 - r; c++) {
              if (idx < letters.length) solution[r + R_off][c + C_off] = letters[idx++];
            }
          }
          if (r > 0) {
            for (let c = n - r + 1; c <= n; c++) {
              if (idx < letters.length) solution[r + R_off][c + C_off] = letters[idx++];
            }
          }
        }
      }
    });

    if (multiTotalWordsStatus) {
      if (totalWordsLoaded === 48) {
        multiTotalWordsStatus.className = 'status-indicator status-ok';
        multiTotalWordsStatus.textContent = '✓ All 48 words loaded across the 4 subgrids!';
      } else if (totalWordsLoaded > 0) {
        multiTotalWordsStatus.className = 'status-indicator status-warn';
        multiTotalWordsStatus.textContent = `Total words loaded: ${totalWordsLoaded} / 48`;
      } else {
        multiTotalWordsStatus.className = 'status-indicator';
        multiTotalWordsStatus.textContent = '';
      }
    }

    // Build all 48 slots and corresponding solution word objects in exact Ingrid order:
    // 1. 4x5 Shorts (5 slots, len 4)
    // 2. 4x5 Longs (4 slots, len 5)
    // 3. 5x6 Shorts (6 slots, len 5)
    // 4. 5x6 Longs (5 slots, len 6)
    // 5. 6x7 Shorts (7 slots, len 6)
    // 6. 6x7 Longs (6 slots, len 7)
    // 7. 7x8 Shorts (8 slots, len 7)
    // 8. 7x8 Longs (7 slots, len 8)
    const allSlots = [];
    const allSolutionWords = [];

    SUBGRIDS_CONFIG.forEach(cfg => {
      const n = cfg.n;
      const R_off = cfg.rOff;
      const C_off = cfg.cOff;
      const text = cfg.textarea ? cfg.textarea.value : '';
      const solData = parseSolutionWords(text, n);

      // Shorts: n + 1 slots of length n
      for (let r = 0; r <= n; r++) {
        const cells = [];
        if (r < n) {
          for (let c = 0; c <= n - 1 - r; c++) {
            cells.push([c + C_off + 1, r + R_off + 1]);
          }
        }
        if (r > 0) {
          for (let c = n - r + 1; c <= n; c++) {
            cells.push([c + C_off + 1, r + R_off + 1]);
          }
        }
        allSlots.push({ length: n, cells: cells });
        allSolutionWords.push(solData.shorts[r] || null);
      }

      // Longs: n slots of length n + 1
      for (let r = 0; r < n; r++) {
        const cells = [];
        for (let c = 0; c <= n - 1 - r; c++) {
          cells.push([c + C_off + 1, r + R_off + 1]);
        }
        for (let c = n - r; c <= n; c++) {
          cells.push([c + C_off + 1, r + 1 + R_off + 1]);
        }
        allSlots.push({ length: n + 1, cells: cells });
        allSolutionWords.push(solData.longs[r] || null);
      }
    });

    // Parse clues
    const cluesText = multiCluesInput ? multiCluesInput.value : '';
    const rawClues = parseMultiClues(cluesText);

    if (multiCluesStatus) {
      if (rawClues.length === 0) {
        multiCluesStatus.className = 'status-indicator';
        multiCluesStatus.textContent = 'Waiting for clues...';
      } else if (rawClues.length === 48) {
        multiCluesStatus.className = 'status-indicator status-ok';
        multiCluesStatus.textContent = '✓ All 48 clues loaded!';
      } else if (rawClues.length < 48) {
        const c4Count = Math.min(Math.max(0, rawClues.length), 5);
        const c5Count = Math.min(Math.max(0, rawClues.length - 5), 10);
        const c6Count = Math.min(Math.max(0, rawClues.length - 15), 12);
        const c7Count = Math.min(Math.max(0, rawClues.length - 27), 14);
        const c8Count = Math.min(Math.max(0, rawClues.length - 41), 7);
        multiCluesStatus.className = 'status-indicator status-warn';
        multiCluesStatus.textContent = `Loaded ${rawClues.length} / 48 clues (${c4Count}/5 len 4, ${c5Count}/10 len 5, ${c6Count}/12 len 6, ${c7Count}/14 len 7, ${c8Count}/7 len 8).`;
      } else {
        multiCluesStatus.className = 'status-indicator status-warn';
        multiCluesStatus.textContent = `⚠️ Loaded ${rawClues.length} clues (expected 48; first 48 will be used).`;
      }
    }

    // Group clues by answer length (4, 5, 6, 7, 8)
    // Slot lengths in allSlots: 5 of len 4, 10 of len 5, 12 of len 6, 14 of len 7, 7 of len 8
    const buckets = { 4: [], 5: [], 6: [], 7: [], 8: [] };
    for (let i = 0; i < allSlots.length; i++) {
      const rawClue = rawClues[i] || '';
      const wordObj = allSolutionWords[i];
      const slotLen = allSlots[i].length;
      const tag = getLengthTag(wordObj, slotLen);
      const taggedClue = rawClue ? appendTagToClue(rawClue, tag) : tag;
      if (buckets[slotLen]) {
        buckets[slotLen].push(taggedClue);
      }
    }

    // Alphabetize clues within each length group
    [4, 5, 6, 7, 8].forEach(len => {
      buckets[len].sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }));
    });

    // Flatten in ascending length order: 4s, then 5s, then 6s, then 7s, then 8s
    const orderedClueTexts = [
      ...buckets[4],
      ...buckets[5],
      ...buckets[6],
      ...buckets[7],
      ...buckets[8]
    ];

    const clueEntries = [];
    for (let i = 0; i < allSlots.length; i++) {
      const slot = allSlots[i];
      clueEntries.push({
        number: "•",
        clue: orderedClueTexts[i] || `(${slot.length})`,
        cells: slot.cells
      });
    }

    const multiIpuzData = {
      version: 'http://ipuz.org/v2',
      kind: ['http://ipuz.org/crossword#1'],
      dimensions: {
        width: canvasWidth,
        height: canvasHeight
      },
      title: title,
      author: author,
      copyright: copyright,
      fakeclues: 'true',
      realwords: 'true',
      puzzle: puzzle,
      solution: solution,
      clues: {
        'Clues': clueEntries
      }
    };

    multiIpuzJsonOutput.value = JSON.stringify(multiIpuzData, null, 2);
    return multiIpuzData;
  }

  // 4-Set Event Listeners
  if (multiTitle) multiTitle.addEventListener('input', generateMultiIpuz);
  if (multiAuthor) multiAuthor.addEventListener('input', generateMultiIpuz);
  if (multiCopyright) multiCopyright.addEventListener('input', generateMultiIpuz);
  if (multiSubgrid1) multiSubgrid1.addEventListener('input', generateMultiIpuz);
  if (multiSubgrid2) multiSubgrid2.addEventListener('input', generateMultiIpuz);
  if (multiSubgrid3) multiSubgrid3.addEventListener('input', generateMultiIpuz);
  if (multiSubgrid4) multiSubgrid4.addEventListener('input', generateMultiIpuz);
  if (multiCluesInput) multiCluesInput.addEventListener('input', generateMultiIpuz);

  // 4-Set Copy
  if (multiIpuzCopyBtn) {
    multiIpuzCopyBtn.addEventListener('click', () => {
      const text = multiIpuzJsonOutput.value;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(showMultiCopiedState);
      } else {
        multiIpuzJsonOutput.select();
        document.execCommand('copy');
        showMultiCopiedState();
      }
    });
  }

  function showMultiCopiedState() {
    const orig = multiIpuzCopyBtn.innerHTML;
    multiIpuzCopyBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
      Copied!
    `;
    multiIpuzCopyBtn.style.backgroundColor = '#16a34a';
    multiIpuzCopyBtn.style.color = '#ffffff';
    setTimeout(() => {
      multiIpuzCopyBtn.innerHTML = orig;
      multiIpuzCopyBtn.style.backgroundColor = '';
      multiIpuzCopyBtn.style.color = '';
    }, 1800);
  }

  // 4-Set Download
  if (multiIpuzDownloadBtn) {
    multiIpuzDownloadBtn.addEventListener('click', () => {
      const ipuzObj = generateMultiIpuz();
      if (!ipuzObj) return;
      const jsonText = JSON.stringify(ipuzObj, null, 2);
      const titleSlug = (ipuzObj.title || 'shapeshifters_set').toLowerCase().replace(/[^a-z0-9]/g, '_');
      const blob = new Blob([jsonText], { type: 'application/json;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${titleSlug}.ipuz`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // Initial update
  updateAll();
  generateMultiIpuz();
})();
