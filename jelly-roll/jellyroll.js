/**
* Filling logic for jelly roll puzzles
* (c) 2024, Crossword Nexus.
* MIT License - https://opensource.org/license/MIT
**/

// The Begin Button
const BEGIN_BUTTON = document.getElementById('begin-button');

// Helper functions to find the intersection and union of two sets
function setIntersection(set1, set2) {
  return new Set([...set1].filter(x => set2.has(x)));
}

function setUnion(set1, set2) {
  if (!set2) return set1;
  return new Set([...set1, ...set2]);
}

// take pairs of letters from a word
function pairsOfLetters(wordOrig) {
  // The "keys" of ret are the offset of the word
  // we're interested in 0, 1, 2
  let ret = ['', '', ''];
  for (var offset = 0; offset < ret.length; offset++) {
    let remainder = '';
    let word = wordOrig;
    // cut off the beginning to add
    let addition = word.substr(0, 2 - offset);
    word = word.substr(2 - offset);
    remainder += addition;
    while (word.length) {
      addition = word.substr(2, 2);
      word = word.substr(4);
      remainder += addition;
    }
    ret[offset] = remainder
  }
  return ret
}

// Helper function to slice a string like in Python
function sliceString(str, { i = 0, j = str.length, k = 1 } = {}) {
  let result = '';
  // Adjust negative indices for i and j (if provided)
  if (i < 0) i = str.length + i;
  if (j < 0) j = str.length + j;
  // Loop through the string with the given step k
  for (let index = i; index < j && index >= 0 && index < str.length; index += k) {
    result += str[index];
  }
  return result;
}

// add a word to our existing data, updating all arrays
function addWord(word, allWords, whiteWords, grayWords) {
  const allWords2 = allWords.concat([word]);
  const allString = allWords2.join('');
  const whiteString = whiteWords.join('');
  const grayString = grayWords.join('');

  // pull out any white or gray words
  // that result from adding our word
  var whiteStart = pairsOfLetters(allString)[1].slice(whiteString.length);
  var grayStart = pairsOfLetters(allString.substr(1))[0].slice(grayString.length);

  var whiteWords2 = whiteWords;
  var grayWords2 = grayWords;

  if (!BEGIN_END_DICT[whiteStart]) {
    const l1 = whiteStart.length;
    for (var i=1; i < l1; i++) {
      if (GOOD_WORDS.has(whiteStart.substr(0, l1-i))) {
        whiteWords2 = whiteWords2.concat(whiteStart.substr(0, l1-i));
        whiteStart = whiteStart.slice(-i);
        break;
      }
    }
  }
  if (!BEGIN_END_DICT[grayStart]) {
    const l1 = grayStart.length;
    for (var i=1; i<l1; i++) {
      if (GOOD_WORDS.has(grayStart.substr(0, l1-i))) {
        grayWords2 = grayWords2.concat(grayStart.substr(0, l1-i));
        grayStart = grayStart.slice(-i);
        break;
      }
    }
  }
  return [allWords2, whiteWords2, grayWords2, whiteStart, grayStart];
}

// Check if a new word will work with our current word
function doesWordWork(word, allWords, whiteWords, grayWords) {
  // add the word to new arrays
  let [allWords2, whiteWords2, grayWords2, whiteStart, grayStart] = addWord(word, allWords, whiteWords, grayWords);
  const allString = allWords2.join('');

  // We start with white if the length mod 4 is 0 or 3
  const startWhite = [0, 3].includes(allString.length % 4);
  // we start with one letter if the length is even
  const startOne = (allString.length %2 == 0);

  // Find a new "all" word that "ends" the words
  const whiteEndings = BEGIN_END_DICT[whiteStart];
  const grayEndings = BEGIN_END_DICT[grayStart];
  var nextWhite = new Set();
  var nextGray = new Set();

  // no need to go through all this if there's nothing
  if (!whiteEndings || !grayEndings) {
    return new Set();
  }

  if (!startWhite && !startOne) {
    grayEndings.forEach(x => {
      nextGray = setUnion(nextGray, BEGIN_PAIR_ARR[0][x]);
    });
    whiteEndings.forEach(x => {
      nextWhite = setUnion(nextWhite, BEGIN_PAIR_ARR[2][x]);
    });
  } else if (startWhite && !startOne) {
    grayEndings.forEach(x => {
      nextGray = setUnion(nextGray, BEGIN_PAIR_ARR[2][x]);
    });
    whiteEndings.forEach(x => {
      nextWhite = setUnion(nextWhite, BEGIN_PAIR_ARR[0][x]);
    });
  } else if (startWhite && startOne) {
    grayEndings.forEach(x => {
      nextGray = setUnion(nextGray, BEGIN_PAIR_ARR[2][x]);
    });
    whiteEndings.forEach(x => {
      nextWhite = setUnion(nextWhite, BEGIN_PAIR_ARR[1][x]);
    });
  } else if (!startWhite && startOne) {
    grayEndings.forEach(x => {
      nextGray = setUnion(nextGray, BEGIN_PAIR_ARR[1][x]);
    });
    whiteEndings.forEach(x => {
      nextWhite = setUnion(nextWhite, BEGIN_PAIR_ARR[2][x]);
    });
  }

  // The intersection of these is what we want
  const possibleNextWords = setIntersection(nextGray, nextWhite);

  // do a little check to make sure these words can be continued
  var ret = new Set();
  for (var pnw of possibleNextWords) {
    [_, _, _, whiteStart, grayStart] = addWord(pnw, allWords2, whiteWords2, grayWords2);
    if (BEGIN_KEYS.has(whiteStart) && BEGIN_KEYS.has(grayStart)) {
      ret.add(pnw);
    }
  }
  return ret;
} // END doesWordWork()

// find the next "inner" words that would arise if we added "word"
function nextInnerWords(word, allWords, whiteWords, grayWords) {
  [_, whiteWords2, grayWords2, whiteStart, grayStart] = addWord(word, allWords, whiteWords, grayWords);
  return [whiteWords2.slice(whiteWords.length).join(' '), grayWords2.slice(grayWords.length).join(' '), whiteStart, grayStart];
}

// helper function to sort the next words
function nextWordSorter(nextWord, allWords, whiteWords, grayWords) {
  [nextWhite, nextGray, whiteStart, grayStart] = nextInnerWords(nextWord, allWords, whiteWords, grayWords);
  let whiteLen = nextWhite.length;
  let grayLen = nextGray.length;
  if (whiteLen == 0) {
    whiteLen = nextWhite.length + 2;
  }
  if (grayLen == 0) {
    grayLen = nextGray.length + 2;
  }
  return whiteLen + grayLen + nextWord.length;
}

/** Handle button click events **/
function handleClick(newData=[]) {
  // change the button to "loading"
  buttonLoading(BEGIN_BUTTON);

  // Run all this asynchronously
  setTimeout(() => {
    // grab the data from the text boxes
    let allWords1 = document.getElementById('jelly-roll').value.toUpperCase().split('\n').filter(Boolean);
    let whiteWords = document.getElementById('white-squares').value.toUpperCase().split('\n').filter(Boolean);
    let grayWords = document.getElementById('gray-squares').value.toUpperCase().split('\n').filter(Boolean);

    // assume the last word is what we're adding
    let allWords = allWords1.slice(0, -1);
    let word = allWords1[allWords1.length - 1];

    // get our possibles
    let nextWords = doesWordWork(word, allWords, whiteWords, grayWords);

    // if there's nothing here, we create an alert and move on
    if (nextWords.size === 0) {
      alert("No fill found. Try a different entry.")
      // remove the new entry/entries from the text boxes
      const textBoxes = ['jelly-roll', 'white-squares', 'gray-squares'];
      for (i = 0; i < textBoxes.length; i++) {
        if (newData[i]) {
          let arr = document.getElementById(textBoxes[i]).value.toUpperCase().split('\n').filter(Boolean);
          arr.pop();
          document.getElementById(textBoxes[i]).value = arr.join('\n');
        }
      }
    } else {
      // add the word
      var whiteStart, grayStart;
      [allWords, whiteWords, grayWords, whiteStart, grayStart] = addWord(word, allWords, whiteWords, grayWords);

      // sort nextwords
      nextWords = [...nextWords].sort((a, b) =>
        nextWordSorter(b, allWords, whiteWords, grayWords) - nextWordSorter(a, allWords, whiteWords, grayWords)
      );

      //console.log(nextWords);
      // create the data set for the table
      const dataSet = [];
      for (var i=0; i<nextWords.length; i++) {
        const niw = nextInnerWords(nextWords[i], allWords, whiteWords, grayWords);
        const nextRow = [nextWords[i], niw[0], niw[1], niw[2], niw[3]];
        //console.log(niw);
        dataSet.push(nextRow);
      }
      // fill the table
      var table = $('#datatables-table').DataTable();
      table.order([]);
      table.clear().rows.add(dataSet).draw();
      // Clear the search bar
      table.search('').draw();

      // update the length
      document.getElementById('jelly-roll-length').innerHTML = `(${allWords1.join('').length})`;

    } // end if/else

    // Change the button back to "active"
    buttonActive(BEGIN_BUTTON);
  }, 0);
} // end handleClick()

/** Define what happens when we click on a row in the table **/
$('#datatables-table tbody').on('click', 'tr', function() {
    // Grab data from text boxes
    let allWords = document.getElementById('jelly-roll').value.toUpperCase().split('\n').filter(Boolean);
    let whiteWords = document.getElementById('white-squares').value.toUpperCase().split('\n').filter(Boolean);
    let grayWords = document.getElementById('gray-squares').value.toUpperCase().split('\n').filter(Boolean);

    // Grab the data from the clicked row
    const data = table.row(this).data();
    // add relevant data to relevant arrays
    if (data[0]) allWords.push(data[0]);
    if (data[1]) whiteWords.push(data[1]);
    if (data[2]) grayWords.push(data[2]);

    // re-populate text boxes
    document.getElementById('jelly-roll').value = allWords.join('\n');
    document.getElementById('white-squares').value = whiteWords.join('\n');
    document.getElementById('gray-squares').value = grayWords.join('\n');

    // Click the button
    handleClick(newData=data);
});

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

/** Export a puzzle in RG format **/
function exportToVpuz(_) {
  // Set up the output variable
  var vpuzOut = {"author": "AUTHOR_GOES_HERE", "title": "TITLE_GOES_HERE", "copyright": "COPYRIGHT_GOES_HERE"};
  const notes = `Three paths curl toward the center of this jelly roll — a white path, a gray path, and a “jelly roll” path that uses all the letters of the other two (winding back and forth as indicated by the heavy bars). Answer words proceed one after the other. Word lengths are given for the answers in the white and gray paths. It’s up to you to determine where the jelly roll answers begin and end.`;
  vpuzOut['notes'] = notes;

  // Read the text boxes
  let allArr = document.getElementById('jelly-roll').value.split('\n');

  // solution string
  const solutionString = allArr.join('').split('').sort().join('');
  vpuzOut['solution-string'] = solutionString;

  // clues
  const clues = {};
  const CLUE_HEADERS = ["White Path", "Gray Path", "Jelly Roll"];
  const ELTS = ['white-squares', 'gray-squares', 'jelly-roll'];
  for (var i=0; i < CLUE_HEADERS.length; i++) {
    let arr = document.getElementById(ELTS[i]).value.split('\n');
    clues[CLUE_HEADERS[i]] = [];
    arr.forEach(x => {
      let clue = `CLUE_FOR_${x}`;
      if (ELTS[i] != 'jelly-roll') clue += ` ${x.length}`;
      clues[CLUE_HEADERS[i]].push(clue);
    });
  }
  vpuzOut["clues"] = clues;

  // image
  const numLetters = solutionString.length / 2; // solution length must be even
  // draw on the canvas
  drawJellyRoll(numLetters);
  // trim
  const trimmedCanvas = getTrimmedCanvas();
  const base64String = trimmedCanvas.toDataURL("image/png");
  vpuzOut['puzzle-image'] = base64String;

  let fileName = allArr[0] + '.vpuz';
  let vpuzString = JSON.stringify(vpuzOut, null, 2);
  downloadStringAsFile(vpuzString, fileName, "text/plain");

}

// Export button functionality
document.getElementById('export-button').addEventListener('click', exportToVpuz);

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
