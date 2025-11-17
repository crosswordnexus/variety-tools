/**
* Display elements for two-tone puzzles
* (c) 2024, Crossword Nexus.
* MIT License - https://opensource.org/license/MIT
**/

/**  Change button's functionality and color and text **/

// Change to a "loading" button
function buttonLoading(button) {
  button.textContent = 'Loading ...';
  button.style['background-color'] = 'gray';
  button.style.cursor = 'default';
  button.removeEventListener('click', handleClick);
}

function buttonActive(button) {
  button.style['background-color'] = '#007bff';
  button.innerHTML = 'Begin';
  button.style.cursor = 'pointer';
  button.addEventListener('click', handleClick);
}

/** Undo functionality **/
// Stack of [twoTone, odd, even] entries added via table-click
let UNDO_STACK = [];

const UNDO_BUTTON = document.getElementById('undo-button');

UNDO_BUTTON.addEventListener('click', function() {
    if (UNDO_STACK.length === 0) return;

    // Pop last action
    const last = UNDO_STACK.pop();

    let allWords = document.getElementById('two-tone').value.toUpperCase().split('\n').filter(Boolean);
    let oddWords = document.getElementById('odd-squares').value.toUpperCase().split('\n').filter(Boolean);
    let evenWords = document.getElementById('even-squares').value.toUpperCase().split('\n').filter(Boolean);

    // Remove only the entries actually added
    if (last.twoTone && allWords[allWords.length - 1] === last.twoTone)
        allWords.pop();
    if (last.odd && oddWords[oddWords.length - 1] === last.odd)
        oddWords.pop();
    if (last.even && evenWords[evenWords.length - 1] === last.even)
        evenWords.pop();

    // Restore the fields
    document.getElementById('two-tone').value = allWords.join('\n');
    document.getElementById('odd-squares').value = oddWords.join('\n');
    document.getElementById('even-squares').value = evenWords.join('\n');

    // Refresh suggestions after undo
    handleClick([]);

    // Disable Undo if no more history
    if (UNDO_STACK.length === 0)
        UNDO_BUTTON.disabled = true;
});

const STORAGE_KEY = "twoToneState_v1";

function saveState() {
    const state = {
        twoTone: document.getElementById('two-tone').value,
        odd: document.getElementById('odd-squares').value,
        even: document.getElementById('even-squares').value,
        undo: UNDO_STACK
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function loadState() {
    const data = localStorage.getItem(STORAGE_KEY);
    if (!data) return null;
    try {
        return JSON.parse(data);
    } catch {
        return null;
    }
}

function clearState() {
    localStorage.removeItem(STORAGE_KEY);
}
