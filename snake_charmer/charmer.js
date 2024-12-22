function new_word_options(loop1, loop2) {
  // The maximum number of words to return
  MAX_RET_WORDS = 20;
  // Find the words we've already used
  var used_words = new Set(loop1.concat(loop2));
  // Get the last word
  var this_word = loop1[loop1.length - 1];
  // To find out where we need to add a new word
  var new_len = loop1.join('').length - loop2.join('').length;
  var this_dict = window.spiralData['begin'];

  //console.log(loop2);

  // Switch stuff depending on new_len
  if (new_len < 0) {
    this_word = loop2[loop2.length - 1];
    new_len = -1 * new_len;
  }
  //console.log(this_word);
  var this_str = this_word.substr(this_word.length - new_len);
  //console.log(this_str);

  // Get our initial return words
  var ret = this_dict[this_str];

  // Sort this by score descending
  ret.sort(function(x, y) {return y['score'] - x['score'];})
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

/* add a word or pair of words to the relevant places */
function add_word(loop1, loop2, this_word) {
  var new_len = loop1.join('').length - loop2.join('').length;
  var w0 = this_word[0]; var w1 = this_word[1];
  if (new_len > 0 ) {
    // add words
    loop2.push(w0);
    if (w1) {
      loop1.push(w1);
    }
  }
  else {
    loop1.push(w0);
    if (w1) {
      loop2.push(w1);
    }
  }
  return [loop1, loop2];
}

/* Process the words in the textareas and write results */
function processTextAreas() {
  var loop1 = document.getElementById('inwardWords').value.split('\n');
  var loop2 = document.getElementById('outwardWords').value.split('\n');

  // get our options for the next word
  var nwo = new_word_options(loop1, loop2);
  var tableData = [];
  nwo.forEach(function (nw) {
    var id = JSON.stringify(nw['words']);
    var thisEntry = nw['words'][0];
    if (nw['words'][1]) {
      thisEntry += ' / ' + nw['words'][1];
    }
    var thisLeftOver = nw['leftover'];
    tableData.push([thisEntry, thisLeftOver, nw['words'][0].length]);
  });

  // Fill the table
  var table = $('#datatables-table').DataTable();
  table.clear().rows.add(tableData).draw();
  // Clear the search bar
  table.search('').draw();

  // change the headers
  changeHeaders();

  return false;
}

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

// Change the inward and outward headers
function changeHeaders() {
  var loop1 = document.getElementById('inwardWords').value.split('\n');
  var loop2 = document.getElementById('outwardWords').value.split('\n');
  var inwardLength = loop1.join('').length;
  document.getElementById('inwardHeader').innerHTML = `Loop 1 (${inwardLength})`;
  var outwardLength = loop2.join('').length;
  document.getElementById('outwardHeader').innerHTML = `Loop 2 (${outwardLength})`;
}
