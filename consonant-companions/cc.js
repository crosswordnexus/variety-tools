/* Function to strip non-consonants from a string */
function word_to_consonants(s) {
  return s.toUpperCase().replace(/[^BCDFGHJKLMNPQRSTVWXZ]/g, '');
}

/* Helper function to find if there's a common substring of a given length */
function hasCommonSubstringOfLength(s1, s2, targetLength) {
    let n1 = s1.length;
    let n2 = s2.length;

    // If either string is shorter than the target, it's impossible
    if (n1 < targetLength || n2 < targetLength) return false;

    let dp = Array(n1 + 1).fill(0).map(() => Array(n2 + 1).fill(0));

    for (let i = 1; i <= n1; i++) {
        for (let j = 1; j <= n2; j++) {
            if (s1[i - 1] === s2[j - 1]) {
                dp[i][j] = 1 + dp[i - 1][j - 1];

                // Short-circuit: return true immediately if target is reached
                if (dp[i][j] >= targetLength) {
                    return true;
                }
            }
        }
    }
    return false;
}

/*
* Find options for new words
* Note that this returns consonant-only versions of the words
*/
function new_word_options(left_words1, right_words1) {

  // left_words1 and right_words1 have vowels
  // strip those first
  left_words = left_words1.map(word_to_consonants);
  right_words = right_words1.map(word_to_consonants);

  // Find the words we've already used
  var used_words = new Set(left_words.concat(right_words));

  // Get the last word
  var this_word = left_words[left_words.length - 1];

  // To find out where we need to add a new word
  var new_len = left_words.join('').length - right_words.join('').length;

  var this_dict = window.ccData['begin'];
  var this_str;
  // If the "right words" are longer, we add a new word on the left
  if (new_len < 0) {
    this_word = right_words[right_words.length - 1];
    new_len = -1 * new_len;
  }

  this_str = this_word.substr(this_word.length - new_len);

  // Get our initial return words
  var ret = this_dict[this_str];
  // Sort this by score descending
  ret.sort(function(x, y) {return y['score'] - x['score'];});

  var ret2 = [];
  // Remove anything that's already been used
  ret.forEach(function (r) {
    var good_word = true
    r['words'].forEach(function(w) {
      if (used_words.has(w)) {
        good_word = false;
      }
    });
    if (good_word) {
      ret2.push(r);
    }
  });
  return ret2;
}

/* add a word or pair of words to the relevant place */
function add_word(left_words1, right_words1, this_word) {

  left_words = left_words1.map(word_to_consonants);
  right_words = right_words1.map(word_to_consonants);

  var new_len = left_words.join('').length - right_words.join('').length;
  var w0 = this_word[0]; var w1 = this_word[1];

  // If "left words" is longer than right, add word to the right
  if (new_len > 0 ) {
    right_words1.push(w0);
    if (w1) {
      left_words1.push(w1);
    }
  }
  else { // otherwise add the "main" word to the left
    left_words1.push(w0);
    if (w1) {
      right_words1.push(w1);
    }
  }
  return [left_words1, right_words1];
}

/** Handle a click **/
$(document).on('click', '#datatables-table tbody tr', function() {

  // Create a save state
  saveState();

  // grab the words from the textareas
  var loop1 = document.getElementById('leftWords').value.split('\n');
  var loop2 = document.getElementById('rightWords').value.split('\n');
  // Grab the data
  const data = table.row(this).data();
  var this_word = data[0].split(' / ');

  var fb_words = add_word(loop1, loop2, this_word);

  // Replace the values in the text areas
  document.getElementById('leftWords').value = fb_words[0].join('\n');
  document.getElementById('rightWords').value = fb_words[1].join('\n');
  // Repeat the process
  processTextAreas();

  // change the headers
  changeHeaders();

  return true;
});

/* Process the words in the textareas and write results */
function processTextAreas() {
  var left_words = document.getElementById('leftWords').value.split('\n');
  var right_words = document.getElementById('rightWords').value.split('\n');

  // get our options for the next word

  var nwo = new_word_options(left_words, right_words);
  // nwo consists of consonant-only versions of the words
  // so we have to map them for display
  var tableData = [];
  nwo.forEach(function (nw) {
    var id = JSON.stringify(nw['words']);
    // leftover string
    let thisLeftOver = nw['leftover'];
    // word 1 (all consonants)
    var thisEntryConsonants = nw['words'][0];
    let thisEntryWords = window.ctwData[thisEntryConsonants];
    for (const thisWord of thisEntryWords) {
      let thisEntry = thisWord;
      var length = thisWord.length;
      if (nw['words'][1]) {
        thisEntryConsonant2 = nw['words'][1];
        let thisEntryWords2 = window.ctwData[thisEntryConsonant2];
        for (const thisWord2 of thisEntryWords2) {
          thisEntry = thisWord + ' / ' + thisWord2;
          length = (length + thisWord2.length)/2.;
          // only do this if there's no common substring of length 4+
          if (!hasCommonSubstringOfLength(thisWord, thisWord2, 4)) {
            tableData.push([thisEntry, thisLeftOver, length.toFixed(1)]);
          }
        }
      } else { // no nw['words'][1]
        tableData.push([thisEntry, thisLeftOver, length.toFixed(1)]);
      }
    }
  });
  // Fill the table
  var table = $('#datatables-table').DataTable();
  table.clear().rows.add(tableData).draw();
  // Clear the search bar
  table.search('').draw();

  // change the headers
  //changeHeaders();

  return false;
}

/** Change the headers to track lengths **/
function changeHeaders() {
  var loop1 = document.getElementById('leftWords').value.split('\n');
  var loop2 = document.getElementById('rightWords').value.split('\n');
  var leftLength = loop1.join('').length;
  document.getElementById('leftHeader').innerHTML = `Left (${leftLength})`;
  var rightLength = loop2.join('').length;
  document.getElementById('rightHeader').innerHTML = `Right (${rightLength})`;
}

/** For the "undo" button **/

// Global stack of past states
let historyStack = [];

// Capture current state
function saveState() {
  historyStack.push({
    left: document.getElementById('leftWords').value,
    right: document.getElementById('rightWords').value,
    tableData: $('#datatables-table').DataTable().rows().data().toArray()
  });

}

function undoLast() {
  if (historyStack.length === 0) return; // nothing to undo

  const lastState = historyStack.pop();

  // Restore textareas
  document.getElementById('leftWords').value = lastState.left;
  document.getElementById('rightWords').value = lastState.right;

  // Restore table
  const table = $('#datatables-table').DataTable();
  table.clear().rows.add(lastState.tableData).draw();

  changeHeaders();
}
