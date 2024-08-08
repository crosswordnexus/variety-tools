/**
* Display elements for rows garden puzzles
* (c) 2024, Crossword Nexus and Joon Pahk.
* MIT License - https://opensource.org/license/MIT
**/

// Colors for the puzzle
const COLORS = ['light', 'medium', 'dark'];
// Dimensions of the puzzle
const ROWS = 12;
const COLUMNS = 21;

// function to determine the color, given the row and column
function cellColor(r, c) {
  var color1 = COLORS[Math.floor((r-1)/2) % 3];
  var color2 = COLORS[(1 + Math.floor(r/2)) % 3];
  if (r == 0 || r == ROWS - 1) color1 = 'empty';
  var color = color2;
  if (c % 6 <= 2) color = color1;
  return color;
}

// Function to make a rows garden puzzle from given text
function makeRowsGardenPuzzle(text='') {
  var letters = [];
  var ctr = 0;
  text = text.replace(/[^a-zA-Z]/g, '').toUpperCase();
  for (var i=0; i < ROWS; i++) {
    // temporary array for this row
    var thisRow = [];
    for (var j=0; j < COLUMNS; j++) {
      // Determine the color
      var color = cellColor(i, j);
      // Get the letter from the text
      var letter = '';
      if (color !== 'empty') {
        letter = text.at(ctr) || '';
        ctr += 1;
      } else {letter = '_';}
      thisRow.push({'letter': letter || '', 'style': color});
    }
    letters.push(thisRow);
  }
  return {'rows': ROWS, 'cols': COLUMNS, 'letters': letters};
}

function createCrossword(data) {
    const crossword = document.getElementById('crossword');

    crossword.innerHTML = '';

    // Dynamically set grid template rows and columns
    crossword.style.gridTemplateColumns = `repeat(${data.cols}, 25px)`;
    crossword.style.gridTemplateRows = `repeat(${data.rows}, 25px)`;

    for (let r = 0; r < data.rows; r++) {
        for (let c = 0; c < data.cols; c++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            if (data.letters[r][c]) {
                cell.textContent = data.letters[r][c]['letter'] || '';
                cell.classList.add(data.letters[r][c]['style'] || 'light');
            } else {
                cell.classList.add('empty');
            }
            crossword.appendChild(cell);
        }
    }
}

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

// Start off with an empty grid
const rg = makeRowsGardenPuzzle();
console.log(rg);
createCrossword(rg);
