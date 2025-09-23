/* Helper function to reverse an array of n-grams */
function reverseArray(arr) {
    return arr.slice().reverse(); // non-destructive
}

// Example: "an|nu" -> ["an", "nu"]
function decodeKey(key) {
  return key.split("|");
}

// Collapse an array of n-grams into a key string
// Example: ["an","nu"] -> "an|nu"
function encodeKey(arr) {
  return Array.isArray(arr) ? arr.join("|") : arr;
}

// Reverse the order of n-grams and encode as key
// Example: ["an","nu"] -> "nu|an"
function reverseKey(arr) {
  return encodeKey(reverseArray(arr));
}

/* Collapse an array of n-grams into a single string */
function arrayToWord(arr) {
  return Array.isArray(arr) ? arr.join("") : arr;
}

// Global stack of past states
let historyStack = [];

// Capture current state
function saveState() {
  historyStack.push({
    inward: document.getElementById('inwardWords').value,
    outward: document.getElementById('outwardWords').value,
    cells: document.getElementById('inwardCells').value,
    tableData: $('#datatables-table').DataTable().rows().data().toArray()
  });
}

function undoLast() {
  if (historyStack.length === 0) return; // nothing to undo

  const lastState = historyStack.pop();

  // Restore textareas
  document.getElementById('inwardWords').value = lastState.inward;
  document.getElementById('outwardWords').value = lastState.outward;
  document.getElementById('inwardCells').value = lastState.cells;

  // Restore table
  const table = $('#datatables-table').DataTable();
  table.clear().rows.add(lastState.tableData).draw();

  changeHeaders();
}



function new_word_options(forward_words, backward_words) {
  // Track used words (collapsed for comparison)
  const used_words = new Set(
    forward_words.concat(backward_words).map(arrayToWord)
  );

  // Last forward word (array of chunks)
  let this_word = forward_words[forward_words.length - 1];

  // Count chunks instead of characters
  const forward_len = forward_words.reduce((a, w) => a + w.length, 0);
  const backward_len = backward_words.reduce((a, w) => a + w.length, 0);
  let new_len = forward_len - backward_len;

  // Default to using "end"
  let this_dict = window.spiralData["end"];
  let this_key;

  if (new_len < 0) {
    // Switch to "begin"
    this_word = backward_words[0];
    new_len = -new_len;
    this_dict = window.spiralData["begin"];

    // Take prefix of this_word (in chunks), reverse, and encode
    const prefixChunks = this_word.slice(0, new_len);
    this_key = reverseKey(prefixChunks);
  } else {
    // Take suffix of this_word (in chunks), reverse, and encode
    const suffixChunks = this_word.slice(this_word.length - new_len);
    this_key = reverseKey(suffixChunks);
  }

  // Look up possible continuations
  let ret = this_dict[this_key] || [];

  // Sort by collapsed length of the first word
  ret.sort((x, y) => arrayToWord(y["words"][0]).length - arrayToWord(x["words"][0]).length);

  // Filter out already-used words
  const ret2 = [];
  ret.forEach(r => {
    let good_word = true;
    r["words"].forEach(w => {
      if (w && used_words.has(arrayToWord(w))) {
        good_word = false;
      }
    });
    if (good_word) ret2.push(r);
  });

  return ret2;
}


/* Add a word (or word pair) to the spiral state */
function add_word(forward_words, backward_words, this_word) {
  // Count chunks on each side
  const forward_len = forward_words.reduce((a, w) => a + w.length, 0);
  const backward_len = backward_words.reduce((a, w) => a + w.length, 0);
  let new_len = forward_len - backward_len;

  const w0 = this_word[0]; // array of chunks
  const w1 = this_word[1]; // array of chunks or null

  if (new_len > 0) {
    // Add main word to backward side
    backward_words = [w0].concat(backward_words);
    if (w1) {
      forward_words = forward_words.concat([w1]);
    }
  } else {
    // Add main word to forward side
    forward_words = forward_words.concat([w0]);
    if (w1) {
      backward_words = [w1].concat(backward_words);
    }
  }

  return [forward_words, backward_words];
}


/** Handle a click **/
$(document).on('click', '#datatables-table tbody tr', function() {

  // Create a save state
  saveState();

  // Read textarea contents as arrays of chunks
  var forward_words = document.getElementById('inwardWords').value
    .split('\n').filter(Boolean).map(decodeKey);
  var backward_words = document.getElementById('outwardWords').value
    .split('\n').filter(Boolean).map(decodeKey);

  // Grab the displayed entry from the table
  const data = table.row(this).data();
  var entryStr = data[0]; // e.g. "wha|tap|ity / tap"

  // Split into one or two words, then decode each
  var parts = entryStr.split(" / ");
  var this_word = [decodeKey(parts[0]), parts[1] ? decodeKey(parts[1]) : null];

  // Add the word(s)
  var fb_words = add_word(forward_words, backward_words, this_word);

  // Write encoded sequences back to textareas
  document.getElementById('inwardWords').value = fb_words[0].map(encodeKey).join('\n');
  document.getElementById('outwardWords').value = fb_words[1].map(encodeKey).join('\n');

  processTextAreas();
  updateInwardCells();
  changeHeaders();
  return true;
});



function processTextAreas() {
  // Read textarea contents as arrays of chunks
  var forward_words = document.getElementById('inwardWords').value
    .split('\n').filter(Boolean).map(decodeKey);
  var backward_words = document.getElementById('outwardWords').value
    .split('\n').filter(Boolean).map(decodeKey);

  // Get candidate next words
  var nwo = new_word_options(forward_words, backward_words);
  var tableData = [];

  nwo.forEach(function (nw) {
    // Display segmentation with pipes
    let entry0 = encodeKey(nw["words"][0]);
    if (nw["words"][1]) {
      entry0 += " / " + encodeKey(nw["words"][1]);
    }

    // Collapse leftover for display
    var entry1 = encodeKey(nw["leftover"]);

    // Compute length from collapsed strings
    var len0 = arrayToWord(nw["words"][0]).length;
    var length = len0;
    if (nw["words"][1]) {
      var len1 = arrayToWord(nw["words"][1]).length;
      length = (len0 + len1) / 2.0;
    }

    // Push [segmentation string, leftover string, length]
    tableData.push([entry0, entry1, length]);
  });

  // Update DataTable
  var table = $('#datatables-table').DataTable();
  table.clear().rows.add(tableData).draw();
  table.search('').draw();

  return false;
}


/** Change the headers to track lengths **/
function changeHeaders() {
  var loop1 = document.getElementById('inwardWords').value.split('\n');
  var loop2 = document.getElementById('outwardWords').value.split('\n');
  var inwardLength = loop1.join('').length;
  document.getElementById('inwardHeader').innerHTML = `Inward (${inwardLength})`;
  var outwardLength = loop2.join('').length;
  document.getElementById('outwardHeader').innerHTML = `Outward (${outwardLength})`;
}

function updateInwardCells() {
  const inwardWords = document.getElementById('inwardWords').value
    .split('\n').filter(Boolean).map(decodeKey);

  //console.log(inwardWords);

  // Flatten all chunks and join with newlines
  const cells = inwardWords.flat().join('\n');
  document.getElementById('inwardCells').value = cells;
}
