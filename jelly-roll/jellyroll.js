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
function addWord(word, allWords, evenWords, oddWords) {
  const allWords2 = allWords.concat([word]);
  const allString = allWords2.join('');
  const evenString = evenWords.join('');
  const oddString = oddWords.join('');

  // pull out any odd or even words that result from adding our word
  var oddStart = sliceString(allString, {k:2}).slice(oddString.length);
  var evenStart = sliceString(allString, {i:1, k:2}).slice(evenString.length);

  var evenWords2 = evenWords;
  var oddWords2 = oddWords;

  if (!BEGIN_END_DICT[evenStart]) {
    const l1 = evenStart.length;
    for (var i=1; i < l1; i++) {
      if (GOOD_WORDS.has(evenStart.substr(0, l1-i))) {
        evenWords2 = evenWords2.concat(evenStart.substr(0, l1-i));
        evenStart = evenStart.slice(-i);
        break;
      }
    }
  }
  if (!BEGIN_END_DICT[oddStart]) {
    const l1 = oddStart.length;
    for (var i=1; i<l1; i++) {
      if (GOOD_WORDS.has(oddStart.substr(0, l1-i))) {
        oddWords2 = oddWords2.concat(oddStart.substr(0, l1-i));
        oddStart = oddStart.slice(-i);
        break;
      }
    }
  }
  return [allWords2, evenWords2, oddWords2, evenStart, oddStart];
}

// Check if a new word will work with our current word
function doesWordWork(word, allWords, evenWords, oddWords) {
  // add the word to new arrays
  let [allWords2, evenWords2, oddWords2, evenStart, oddStart] = addWord(word, allWords, evenWords, oddWords);
  const allString = allWords2.join('');

  // `startEven` is True if the next letter in "all" words continues `evenStart`
  const startEven = (allString.length % 2 == 1);

  // Find a new "all" word that "ends" the odd and even
  const evenEndings = BEGIN_END_DICT[evenStart];
  const oddEndings = BEGIN_END_DICT[oddStart];
  var nextEven = new Set();
  var nextOdd = new Set();

  if (!evenEndings || !oddEndings) {
    return new Set();
  }

  if (!startEven) {
    evenEndings.forEach(x => {
      nextEven = setUnion(nextEven, BEGIN_EVEN_DICT[x]);
    });
    oddEndings.forEach(x => {
      nextOdd = setUnion(nextOdd, BEGIN_ODD_DICT[x]);
    });
  } else {
    evenEndings.forEach(x => {
      nextEven = setUnion(nextEven, BEGIN_ODD_DICT[x]);
    });
    oddEndings.forEach(x => {
      nextOdd = setUnion(nextOdd, BEGIN_EVEN_DICT[x]);
    });
  }

  // The intersection of these is what we want
  const possibleNextWords = setIntersection(nextEven, nextOdd);

  // do a little check to make sure these words can be continued
  var ret = new Set();
  for (var pnw of possibleNextWords) {
    [_, _, _, evenStart, oddStart] = addWord(pnw, allWords2, evenWords2, oddWords2);
    if (BEGIN_KEYS.has(evenStart) && BEGIN_KEYS.has(oddStart)) {
      ret.add(pnw);
    }
  }
  return ret;
} // END doesWordWork()

// find the next "inner" words that would arise if we added "word"
function nextInnerWords(word, allWords, evenWords, oddWords) {
  [_, evenWords2, oddWords2, evenStart, oddStart] = addWord(word, allWords, evenWords, oddWords);
  return [evenWords2.slice(evenWords.length).join(' '), oddWords2.slice(oddWords.length).join(' '), evenStart, oddStart];
}

// helper function to sort the next words
function nextWordSorter(nextWord, allWords, evenWords, oddWords) {
  [nextEven, nextOdd, evenStart, oddStart] = nextInnerWords(nextWord, allWords, evenWords, oddWords);
  let evenLen = nextEven.length;
  let oddLen = nextOdd.length;
  if (evenLen == 0) {
    evenLen = evenStart.length + 2;
  }
  if (oddLen == 0) {
    oddLen = oddStart.length + 2;
  }
  return evenLen + oddLen;
}

/** Handle button click events **/
function handleClick(newData=[]) {
  // change the button to "loading"
  buttonLoading(BEGIN_BUTTON);

  // Run all this asynchronously
  setTimeout(() => {
    // grab the data from the text boxes
    let allWords1 = document.getElementById('two-tone').value.toUpperCase().split('\n').filter(Boolean);
    let oddWords = document.getElementById('odd-squares').value.toUpperCase().split('\n').filter(Boolean);
    let evenWords = document.getElementById('even-squares').value.toUpperCase().split('\n').filter(Boolean);

    // assume the last word is what we're adding
    let allWords = allWords1.slice(0, -1);
    let word = allWords1[allWords1.length - 1];

    // get our possibles
    let nextWords = doesWordWork(word, allWords, evenWords, oddWords);

    // if there's nothing here, we create an alert and move on
    if (nextWords.size === 0) {
      alert("No fill found. Try a different entry.")
      // remove the new entry/entries from the text boxes
      const textBoxes = ['two-tone', 'odd-squares', 'even-squares'];
      for (i = 0; i < textBoxes.length; i++) {
        if (newData[i]) {
          let arr = document.getElementById(textBoxes[i]).value.toUpperCase().split('\n').filter(Boolean);
          arr.pop();
          document.getElementById(textBoxes[i]).value = arr.join('\n');
        }
      }
    } else {
      // add the word
      var evenStart, oddStart;
      [allWords, evenWords, oddWords, evenStart, oddStart] = addWord(word, allWords, evenWords, oddWords);

      // sort nextwords
      nextWords = [...nextWords].sort((a, b) =>
        nextWordSorter(b, allWords, evenWords, oddWords) - nextWordSorter(a, allWords, evenWords, oddWords)
      );

      //console.log(nextWords);
      // create the data set for the table
      const dataSet = [];
      for (var i=0; i<nextWords.length; i++) {
        const niw = nextInnerWords(nextWords[i], allWords, evenWords, oddWords);
        const nextRow = [nextWords[i], niw[1], niw[0], niw[3], niw[2]];
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
      document.getElementById('two-tone-length').innerHTML = `(${allWords1.join('').length})`;

    } // end if/else

    // Change the button back to "active"
    buttonActive(BEGIN_BUTTON);
  }, 0);
} // end handleClick()

/** Define what happens when we click on a row in the table **/
$('#datatables-table tbody').on('click', 'tr', function() {
    // Grab data from text boxes
    let allWords = document.getElementById('two-tone').value.toUpperCase().split('\n').filter(Boolean);
    let oddWords = document.getElementById('odd-squares').value.toUpperCase().split('\n').filter(Boolean);
    let evenWords = document.getElementById('even-squares').value.toUpperCase().split('\n').filter(Boolean);

    // Grab the data from the clicked row
    const data = table.row(this).data();
    // add relevant data to relevant arrays
    if (data[0]) allWords.push(data[0]);
    if (data[1]) oddWords.push(data[1]);
    if (data[2]) evenWords.push(data[2]);

    // re-populate text boxes
    document.getElementById('two-tone').value = allWords.join('\n');
    document.getElementById('odd-squares').value = oddWords.join('\n');
    document.getElementById('even-squares').value = evenWords.join('\n');

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
