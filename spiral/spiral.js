/* Helper function to reverse a string */
function reverseString(str) {
    return str.split("").reverse().join("");
}

function new_word_options(forward_words, backward_words) {
  // The maximum number of words to return
  MAX_RET_WORDS = 20;
  // Find the words we've already used
  var used_words = new Set(forward_words.concat(backward_words));
  // Get the last word
  var this_word = forward_words[forward_words.length - 1];
  // To find out where we need to add a new word
  var new_len = forward_words.join('').length - backward_words.join('').length;
  var this_dict = window.spiralData['end'];
  var this_str;
  // Switch to "begin" depending on new_len
  if (new_len < 0) {
    this_word = backward_words[0];
    new_len = -1 * new_len;
    this_dict = window.spiralData['begin'];
    this_str = reverseString(this_word.substr(0, new_len));
  }
  else {
    this_str = reverseString(this_word.substr(this_word.length - new_len));
  }
  // Get our initial return words
  var ret = this_dict[this_str];
  // Sort this by score descending
  //ret.sort(function(x, y) {return y['score'] - x['score'];})
  // On second thought, sort by length descending
  ret.sort(function(x, y) {return y["words"][0].length - x["words"][0].length;});
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
  return ret2.slice(0, MAX_RET_WORDS);
}

/* add a word or pair of words to the relevant place */
function add_word(forward_words, backward_words, this_word) {
  var new_len = forward_words.join('').length - backward_words.join('').length;
  var w0 = this_word[0]; var w1 = this_word[1];
  if (new_len > 0 ) {
    // add "main" word to backwards words
    backward_words = [w0].concat(backward_words);
    if (w1) {
      forward_words.push(w1);
    }
  }
  else {
    forward_words.push(w0);
    if (w1) {
      backward_words = [w1].concat(backward_words);
    }
  }
  return [forward_words, backward_words];
}

/** Handle a click **/
$(document).on('click', '#datatables-table tbody tr', function() {
  // grab the words from the textareas
  var loop1 = document.getElementById('inwardWords').value.split('\n');
  var loop2 = document.getElementById('outwardWords').value.split('\n');
  // Grab the data
  const data = table.row(this).data();
  var this_word = data[0].split(' / ');

  var fb_words = add_word(loop1, loop2, this_word);

  // Replace the values in the text areas
  document.getElementById('inwardWords').value = fb_words[0].join('\n');
  document.getElementById('outwardWords').value = fb_words[1].join('\n');
  // Repeat the process
  processTextAreas();

  // change the headers
  changeHeaders();

  return true;
});

/* Process the words in the textareas and write results */
function processTextAreas() {
  var forward_words = document.getElementById('inwardWords').value.split('\n');
  var backward_words = document.getElementById('outwardWords').value.split('\n');

  // get our options for the next word
  var nwo = new_word_options(forward_words, backward_words);
  var tableData = [];
  nwo.forEach(function (nw) {
    var id = JSON.stringify(nw['words']);
    var thisEntry = nw['words'][0];
    var length = thisEntry.length;
    if (nw['words'][1]) {
      thisEntry += ' / ' + nw['words'][1];
      length = (length + nw['words'][1].length)/2.;
    }
    var thisLeftOver = nw['leftover'];
    tableData.push([thisEntry, thisLeftOver, length]);
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
  var loop1 = document.getElementById('inwardWords').value.split('\n');
  var loop2 = document.getElementById('outwardWords').value.split('\n');
  var inwardLength = loop1.join('').length;
  document.getElementById('inwardHeader').innerHTML = `Inward (${inwardLength})`;
  var outwardLength = loop2.join('').length;
  document.getElementById('outwardHeader').innerHTML = `Outward (${outwardLength})`;
}

/* Process the selected item from the list */
function processSelectedItem() {
  // grab the words from the textareas
  var forward_words = document.getElementById('inwardWords').value.split('\n');
  var backward_words = document.getElementById('outwardWords').value.split('\n');
  // Find out which radio button is checked
  const radioButtons = document.querySelectorAll('input[name="wordSelector"]');
  var selectedValue;
  for (const radioButton of radioButtons) {
      if (radioButton.checked) {
          selectedValue = radioButton.value;
          break;
      }
  }
  console.log(selectedValue);
  var this_word = JSON.parse(selectedValue);
  var fb_words = add_word(forward_words, backward_words, this_word);
  // Replace the values in the text areas
  document.getElementById('inwardWords').value = fb_words[0].join('\n');
  document.getElementById('outwardWords').value = fb_words[1].join('\n');
  // Repeat the process
  processTextAreas();

  // Change the inward and outward headers
  var inwardLength = fb_words[0].join('').length;
  document.getElementById('inwardHeader').innerHTML = `Inward (${inwardLength})`;
  var outwardLength = fb_words[1].join('').length;
  document.getElementById('outwardHeader').innerHTML = `Outward (${outwardLength})`;

  return true;
}
