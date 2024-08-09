/**
* Filling logic for rows garden puzzles
* Note that for now this is always top-down
* (c) 2024, Crossword Nexus and Joon Pahk.
* MIT License - https://opensource.org/license/MIT
**/

// uppercase letters for reference
const UPPERCASE_LETTERS = new Set('ABCDEFGHIJKLMNOPQRSTUVWXYZ');

// The Begin Button
const BEGIN_BUTTON = document.getElementById('begin-button');

// lscache key for bloom mapper
const LC_BM_KEY = 'rg-bloom-mapper';
// Timeout time for cache is 3 days
const LC_TIMEOUT_TIME = 60 * 24 * 3;

// Return all twelve "rotations" of a (6-letter) word in a bloom
function bloomPatterns(_input) {
  let patterns = new Set()
  // reverse the string
  let _input2 = _input.split('').reverse().join('');

  // loop through all options
  for (var i=0; i<6; i++) {
    let pat1 = _input.substr(i) + _input.substr(0, i);
    let pat2 = _input2.substr(i) + _input2.substr(0, i);
    patterns.add(pat1);
    patterns.add(pat2);
  }
  return patterns;
}

// Given a pattern, find possible bloom entries
function bloomMatches(_input) {
  // Set up our output variable
  let output = new Set();

  // find words in WORDS[6] that match this
  bloomPatterns(_input.toLowerCase()).forEach(pat => {
    var re = createMatcher(pat);
    WORDS[6].forEach(w => {
      if (re(w)) output.add(w);
    });
  });
  return output;
}

// Function to match simple regexes without the overhead of regex
function createMatcher(pattern) {
  // pattern must be all dots and letters
  pattern = pattern.toLowerCase();
  return function(word) {
    word = word.toLowerCase();
    if (word.length !== pattern.length) return false;
    for (let i = 0; i < pattern.length; i++) {
      if (pattern[i] !== '.' && pattern[i] !== word[i]) return false;
    }
    return true;
  };
}

// Helper function to check if a string is all lowercase or periods
function isLowercaseOrPeriod(str) {
    const allowedChars = new Set('abcdefghijklmnopqrstuvwxyz.');
    return str.split('').every(char => allowedChars.has(char));
}

// Helper function to reverse a string
function reverseString(s) {
  return s.split('').reverse().join('');
}

// Helper function to find the intersection of two sets
function setIntersection(set1, set2) {
  return new Set([...set1].filter(x => set2.has(x)));
}

// Function to get a matching entry in a row
function rowMatches(_input, startLocation=0) {
  // Get the length of the input
  const myLen = _input.length;

  // Set up the blooms
  var s = _input;

  // if startLocation != 0 we are looking at the second word in a row
  const ix = (21 - startLocation) % 3;
  s = s.substr(ix);

  // bloomBuds is an array of dictionaries
  // each dictionary has a 3-letter pattern and a "start" integer
  const bloomBuds = [];
  let ctr = 0;
  while (s) {
    var s1 = s.substr(0, 3);
    s = s.substr(3);
    if (isLowercaseOrPeriod(s1)) {
      d = {'bud': s1, 'start': ctr + ix};
      bloomBuds.push(d);
    }
    ctr += 3;
  } // end while s

  // if `input` has an uppercase letter we have to check if it matches
  // we set up a regex-like function
  var myRe;
  if (_input != _input.toLowerCase()) {
    let pat = '';
    _input.split('').forEach( letter => {
      if (UPPERCASE_LETTERS.has(letter)) pat += letter.toLowerCase();
      else pat += '.';
    });
    myRe = createMatcher(pat);
  } else {
    myRe = function(x) {return true;}
  }

  // Determine which words are "good"
  let goodWords = {};
  WORDS[myLen].forEach(w => {
    if (!myRe(w)) return;
    if (!bloomBuds) {
      if (myRe(w)) goodWords[w] = [];
    } else {
      var thisMatches;
      bloomBuds.forEach(d => {
        var fullPat = reverseString(d['bud']) + w.substr(d['start'], 3);
        // if there's no '.' we can use bloomPatterns
        if (!fullPat.includes('.')) {
          thisMatches = setIntersection(bloomPatterns(fullPat), WORDS[6]);
        } else {
          thisMatches = bloomMatches(fullPat);
        }
        if (thisMatches.size) {
          // add a random element of this set to goodWords
          goodWords[w] = (goodWords[w] || []).concat([thisMatches.values().next().value]);
        }
      });
    } // end if/else
  }); // end for WORDS

  // Set up the output value
  var output = {};
  Object.keys(goodWords).forEach(x => {
    var k = goodWords[x];
    if (k.length == bloomBuds.length) {
      output[x] = k;
    }
  }); // end goodWords loop
  return output;
} // end rowMatches()

// function to fill an entire row given the row above
function fillRow(rowAbove, rowNumber) {

  if (rowNumber >= ROWS) {
    return;
  }
  // set up the return object
  var output = {};

  // Modify `rowAbove` based on the rowNumber
  var rowAbove2 = '';
  for (var i=0; i < rowAbove.length; i++) {
    var letter = rowAbove.at(i);
    if (cellColor(rowNumber, i) == cellColor(rowNumber - 1, i)) {
      rowAbove2 += letter;
    } else if (UPPERCASE_LETTERS.has(letter)) {
      rowAbove2 += letter;
    } else {
      rowAbove2 += '_';
    }
  } // end for rowAbove
  rowAbove = rowAbove2;

  var minLen = 6, maxLen = 15;
  // We need to change some stuff if we're in the last row
  if (rowNumber == ROWS - 1) {
    minLen = 9;
    maxLen = 9;
    rowAbove = rowAbove.replaceAll('_', '');
  }

  // loop through possible lengths to find all possible options
  for (myLen = minLen; myLen <= maxLen; myLen++) {
    // Step 1: find options for the first entry
    var pat1 = rowAbove.substr(0, myLen);
    var rm1 = rowMatches(pat1);

    // At the last row, we can just return rm1
    if (rowNumber == ROWS - 1) {
      Object.keys(rm1).forEach(k => {
        output[JSON.stringify([k, ''])] = rm1[k];
      });
      return output;
    }

    // Step 2: find options for the second entry
    var rm2 = rowMatches(rowAbove.substr(myLen), myLen);

    // Make sure we have matches
    if (!rm1 || !rm2) continue;

    // Step 3: make sure these line up
    // iterate through rm1 and rm2
    Object.keys(rm1).forEach(k1 => {
      Object.keys(rm2).forEach(k2 => {
        // we need to make sure that the end of k1
        // and the start of k2 will form a valid bloom
        var startCol = myLen;
        var numEndLetters = myLen % 3;
        // we only need to do this if it's not a multiple of 3
        if (numEndLetters > 0) {
          var pat;
          var k1EndReversed = reverseString(k1).substr(0, numEndLetters);
          var k2Start = k2.substr(0, 3 - numEndLetters);
          // get the pattern to match based on matching cell colors
          if (cellColor(rowNumber - 1, startCol) == cellColor(rowNumber, startCol)) {
            pat = k2Start + k1EndReversed + rowAbove.substr(myLen - numEndLetters, 3);
            pat = pat.replace('_', '.');
          } else {
            pat = k2Start + k1EndReversed + '...';
          }
          if (!bloomPatterns(pat)) {
            return;
          }
        } // end if numEndLetters
        var k = JSON.stringify([k1, k2]);
        var v = rm1[k1].concat(rm2[k2]);
        // We do a final check if this is the penultimate row
        if (rowNumber == ROWS - 2) {
          var kk = k1 + k2;
          var thisMatch = kk.substr(3, 3) + kk.substr(9, 3) + kk.substr(15, 3);
          if (Object.keys(rowMatches(thisMatch)).length) output[k] = v;
        } else { // otherwise we always add
          output[k] = v;
        }
      }); // end for rm2
    }); // end for rm1
  } // end for myLen

  return output;

}

// helper function to find the first unfilled row
function findFirstUnfilledRow(rgData) {
  for (var r=0; r < ROWS; r++) {
    if (rgData.letters[r].map(x => x.letter).join('').length < COLUMNS) {
      break;
    }
  }
  return r;
}

/** Given an rgData object, find the options for the next row **/
function nextRowOptions(rgData) {
  // First, find the row we need to populate
  const rowNumber = findFirstUnfilledRow(rgData);
  // We can't do this if rowNumber == 0
  if (rowNumber == 0) {
    console.log('Need data in row 0');
    return;
  }

  if (rowNumber >= ROWS) {
    return null;
  }

  // Get the letters currently in this row and in the row above
  var rowAbove1 = rgData.letters[rowNumber-1].map(x => x.letter).join('').toLowerCase();
  var thisRow = rgData.letters[rowNumber].map(x => x.letter).join('').toUpperCase().replaceAll('_', '');
  // Construct the string to pass into the `fillRow` function
  var rowAbove = '';
  for (var i=0; i<COLUMNS; i++) rowAbove += (thisRow.at(i) || rowAbove1.at(i));

  var newData = fillRow(rowAbove, rowNumber);

  return newData;
}

/** Handle button click events **/
function handleClick(bloomEntries=null) {
  // change the button to "loading"
  buttonLoading(BEGIN_BUTTON);

  // Run all this asynchronously
  setTimeout(() => {
    // grab the data from the text box
    const rowWords = document.getElementById('rows-text').value;

    // create the puzzle data
    const rgData = makeRowsGardenPuzzle(text=rowWords);

    // visualize the rows garden puzzle
    createCrossword(rgData);

    // create options for the next row
    var dataObj = nextRowOptions(rgData);

    // Convert to array
    if (dataObj) {
      var tableData = [];
      Object.keys(dataObj).forEach(k => {
        var thisRow = JSON.parse(k).concat(dataObj[k].join(' '));
        tableData.push(thisRow);
      });

      // Fill the table
      var table = $('#datatables-table').DataTable();
      table.clear().rows.add(tableData).draw();
      // Clear the search bar
      table.search('').draw();
    }

    /** Populate the text boxes **/
    // Clear text boxes
    COLORS.forEach(color => {
      document.getElementById(`${color}-text`).value = '';
    });

    // Make the rows text box uppercase
    document.getElementById('rows-text').value = document.getElementById('rows-text').value.toUpperCase();

    // Find the last filled row
    const lastFilledRow = findFirstUnfilledRow(rgData) - 1;

    // retrieve bloom mapper from lscache
    var bloomMapper = lscache.get(LC_BM_KEY) || {};

    // If we have a bloomEntries array, process it
    if (Array.isArray(bloomEntries)) {
      const [color, blooms] = lastBlooms(rgData, lastFilledRow);
      for (var i=0; i<blooms.length; i++) {
        bloomMapper[blooms[i]] = bloomEntries[i].toUpperCase();
      }
      // Save bloomMapper
      lscache.set(LC_BM_KEY, bloomMapper, LC_TIMEOUT_TIME);
    }

    // Object to hold bloom values for each text box
    const textBoxData = COLORS.reduce((acc, key) => {
      acc[key] = [];
      return acc;
    }, {});

    // Loop through and process blooms
    for (var r = 1; r <= lastFilledRow; r++) {
      const [color, blooms] = lastBlooms(rgData, r);
      // Populate textBoxData
      blooms.forEach(b => {
        textBoxData[color].push(bloomMapper[b] || b);
      });
    } // end for r

    // Populate the text boxes
    COLORS.forEach(color => {
      document.getElementById(`${color}-text`).value = textBoxData[color].join('\n');
    });

    // Change the button back to "active"
    buttonActive(BEGIN_BUTTON);
  }, 0);
}

/** Define what happens when we click on a row in the table **/
$('#datatables-table tbody').on('click', 'tr', function() {
    // Grab the data
    var data = table.row(this).data();
    // get the next row to add
    var nextRow = data.slice(0, 2).join('/');
    // if there's only one word, no need for the slash
    if (!data[1]) nextRow = data[0];
    // Add this to the text box
    document.getElementById('rows-text').value += '\n' + nextRow;
    // Click the button
    handleClick(data[2].split(' '));
});

// Function to get the blooms (in dictionary order) from a row
function lastBlooms(rgData, rowNumber) {
  // Set up the output array
  var output = [];
  // Get the color of the blooms
  const color = COLORS[(ROWS - 1 - rowNumber) % 3];
  // Get the column where the blooms start
  const startCol = 3 * (rowNumber % 2);

  var col = startCol;
  while (col < COLUMNS) {
    var thisText = '';
    for (var r = rowNumber - 1; r <= rowNumber; r++) {
      for (var c = col; c < col + 3; c++) {
        thisText += rgData.letters[r][c].letter.toUpperCase() || '';
      }
    }
    output.push(thisText);
    col += 6;
  }
  return [color, output];
}

/** Export a puzzle in RG format **/
function exportToRG(_) {
  // Set up the output variable
  var rgOut = {"author": "AUTHOR_GOES_HERE", "title": "TITLE_GOES_HERE", "copyright": "COPYRIGHT_GOES_HERE"};
  // Read the text boxes
  let rowsArr = document.getElementById('rows-text').value.split('\n');
  var bloomsArrs = {};
  COLORS.forEach(color => {
    bloomsArrs[color] = document.getElementById(`${color}-text`).value.split('\n');
  });
  // Populate rows
  const rows = [];
  for (var i=0; i<rowsArr.length; i++) {
    let thisRow = rowsArr[i];
    if (!thisRow) continue;
    let rowArr = thisRow.split('/');
    const thisRowArr = [];
    rowArr.forEach(entry => {
      thisRowArr.push({"clue": `CLUE_FOR_${entry}`, "answer": entry});
    });
    rows.push(thisRowArr);
  }
  rgOut['rows'] = rows;

  // Populate blooms
  COLORS.forEach(color => {
    rgOut[color] = [];
    bloomsArrs[color].forEach(entry => {
      rgOut[color].push({"clue": `CLUE_FOR_${entry}`, "answer": entry});
    });
  });

  let fileName = rowsArr[0] + '.rg';
  let yamlString = jsyaml.dump(rgOut);
  downloadStringAsFile(yamlString, fileName, "text/plain");

  //console.log(yamlString);
}

// Export button functionality
document.getElementById('export-button').addEventListener('click', exportToRG);

// Helper function for creating downloads
function downloadStringAsFile(content, fileName, mimeType) {
    // Create a blob with the content
    const blob = new Blob([content], { type: mimeType });

    // Create a temporary anchor element
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = fileName;

    // Append the anchor to the body (required for some browsers)
    document.body.appendChild(a);

    // Trigger the download by simulating a click
    a.click();

    // Remove the anchor element from the document
    document.body.removeChild(a);

    // Revoke the object URL to free up memory
    URL.revokeObjectURL(a.href);
}


/** Functions to help check for dupes **/

// turn a phrase into an array of root forms using `compromise`
function lemmatize(phrase) {
  var doc = nlp(phrase);
  //compute all roots
  doc.compute('root')
  // retrieve them from .json() response
  var p2 = doc.json()[0].terms.map(t=>t.root || t.normal);
  return p2;
}

// infer spaces in a string like "INFERSPACESINASTRINGLIKE"
// ported from https://stackoverflow.com/a/11642687
function inferSpaces(s, maxword = 15) {
  // Find the best match for the i first characters, assuming cost has
  // been built for the i-1 first characters.
  // Returns a pair [match_cost, match_length].
  function bestMatch(i) {
    const candidates = [...Array(Math.min(maxword, i)).keys()].map(k => {
      const c = cost[i - k - 1] || 0;
      const word = s.slice(i - k - 1, i);
      return [c + (WORDNINJA[word] || 9e999), k + 1];
    });
    return candidates.reduce((min, curr) => (curr[0] < min[0] ? curr : min));
  }

  // Build the cost array.
  const cost = [0];
  for (let i = 1; i <= s.length; i++) {
    const [c, k] = bestMatch(i);
    cost.push(c);
  }

  // Backtrack to recover the minimal-cost string.
  const out = [];
  let i = s.length;
  while (i > 0) {
    const [c, k] = bestMatch(i);
    if (c !== cost[i]) throw new Error("Cost mismatch during backtracking");
    out.push(s.slice(i - k, i));
    i -= k;
  }

  return out.reverse().join(" ");
}

function checkForDupes(_) {
  // Grab the words from the text boxes
  const boxNames = ['rows'].concat(COLORS);
  const words = {};
  boxNames.forEach(box => {
    let wordsArr = document.getElementById(`${box}-text`).value.split('\n');
    wordsArr.forEach(w => {
      if (!w) return;
      let w1 = w.split('/');
      w1.forEach(w2 => {
        // infer spaces and lemmatize
        let w3 = lemmatize(inferSpaces(w2.toLowerCase()))
        w3.forEach(w4 => {
          if (!words[w4]) words[w4] = new Set();
          words[w4].add(w2);
        });
      });
    });
  });

  // Prepare text for an alert
  var alertText = '';
  Object.keys(words).forEach(k => {
    if (words[k].size > 1 && k.length > 3) {
      let dupeDisplay = [...words[k]].join(', ');
      alertText += `${k} => ${dupeDisplay}\n`;
    }
  });
  if (!alertText) alertText = "No dupes found.";
  alert(alertText);
}

// Dupe button functionality
document.getElementById('checkdupes-button').addEventListener('click', checkForDupes);
