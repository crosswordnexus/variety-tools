/**
 * Dupe checking functionality using utils/dupe-checker.min.js
 */

async function checkForDupes() {
  const btn = document.getElementById('checkdupes-button');
  const dupeAlert = document.getElementById('dupe-alert-container');
  if (!dupeAlert) return;

  if (typeof window.findDupes !== 'function') {
    console.warn('dupe-checker.min.js is not loaded or findDupes is unavailable');
    return;
  }

  // Grab the words from the text boxes
  const boxNames = ['two-tone', 'odd-squares', 'even-squares'];
  const words = [];
  boxNames.forEach(box => {
    const el = document.getElementById(box);
    if (!el) return;
    const wordsArr = el.value.split('\n').map(w => w.trim()).filter(Boolean);
    words.push(...wordsArr);
  });

  if (words.length === 0) {
    dupeAlert.style.display = 'none';
    return;
  }

  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Checking...';
  }

  try {
    const res = await window.findDupes(words);
    if (res.hasDupes) {
      const detailsHtml = res.dupes.map(d => {
        return `<li><strong>${d.stem}</strong>: <em>${d.words.join(', ')}</em></li>`;
      }).join('');

      dupeAlert.innerHTML = `
        <div class="dupe-box dupe-warning">
          <div class="dupe-box-title">⚠️ ${res.dupes.length} Dupe${res.dupes.length === 1 ? '' : 's'} Detected</div>
          <ul class="dupe-box-list">${detailsHtml}</ul>
        </div>
      `;
      dupeAlert.style.display = 'block';
    } else {
      dupeAlert.innerHTML = `
        <div class="dupe-box dupe-clean">
          ✓ No dupes detected
        </div>
      `;
      dupeAlert.style.display = 'block';
    }
  } catch (err) {
    console.error('Error running dupe check:', err);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Check for dupes';
    }
  }
}

// Dupe button functionality
document.getElementById('checkdupes-button').addEventListener('click', checkForDupes);
