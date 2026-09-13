/**
 * Dupe checking functionality using utils/dupe-checker.min.js & utils/variety.js
 */

async function checkForDupes() {
  const boxNames = ['two-tone', 'odd-squares', 'even-squares'];
  const words = [];
  boxNames.forEach(box => {
    const el = document.getElementById(box);
    if (!el) return;
    const wordsArr = el.value.split('\n').map(w => w.trim()).filter(Boolean);
    words.push(...wordsArr);
  });

  await checkAndRenderDupes(words, '#dupe-alert-container', '#checkdupes-button');
}

// Dupe button functionality
document.getElementById('checkdupes-button').addEventListener('click', checkForDupes);
