/**
 * Shared utility functions for Variety Tools
 */

/**
 * Checks a list of words for duplicates using window.findDupes (from dupe-checker.min.js)
 * and renders a styled alert box into targetContainer.
 *
 * @param {string[]} words - Array of words or phrases to check.
 * @param {HTMLElement|string} targetContainer - DOM element or selector for the dupe alert box.
 * @param {HTMLElement|string} [button] - Optional button element or selector to toggle loading state.
 * @returns {Promise<object|null>} findDupes result object, or null.
 */
async function checkAndRenderDupes(words, targetContainer, button) {
  const container = typeof targetContainer === 'string'
    ? document.querySelector(targetContainer)
    : targetContainer;
  if (!container) return null;

  const btn = typeof button === 'string'
    ? document.querySelector(button)
    : button;

  if (typeof window.findDupes !== 'function') {
    console.warn('dupe-checker.min.js is not loaded or findDupes is unavailable');
    return null;
  }

  const cleanWords = (words || [])
    .map(w => (typeof w === 'string' ? w.trim() : ''))
    .filter(Boolean);

  if (cleanWords.length === 0) {
    container.style.display = 'none';
    container.innerHTML = '';
    return null;
  }

  const originalBtnText = btn ? btn.textContent : '';
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Checking...';
  }

  try {
    const res = await window.findDupes(cleanWords);
    if (res && res.hasDupes) {
      const detailsHtml = res.dupes.map(d => {
        return `<li><strong>${d.stem}</strong>: <em>${d.words.join(', ')}</em></li>`;
      }).join('');

      container.innerHTML = `
        <div class="dupe-box dupe-warning">
          <div class="dupe-box-title">⚠️ ${res.dupes.length} Dupe${res.dupes.length === 1 ? '' : 's'} Detected</div>
          <ul class="dupe-box-list">${detailsHtml}</ul>
        </div>
      `;
      container.style.display = 'block';
    } else {
      container.innerHTML = `
        <div class="dupe-box dupe-clean">
          ✓ No dupes detected
        </div>
      `;
      container.style.display = 'block';
    }
    return res;
  } catch (err) {
    console.error('Error running dupe check:', err);
    return null;
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = originalBtnText || 'Check for Dupes';
    }
  }
}

// Expose globally
window.checkAndRenderDupes = checkAndRenderDupes;
