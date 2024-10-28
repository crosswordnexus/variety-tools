/**
 * (c) 2024, Crossword Nexus
 * MIT License https://mit-license.org/
 **/

/**
 * Function that defines what to do when we load a puzzle
 **/
function loadPuzzle(data) {
  // All the interesting code here
  const img = document.getElementById('puzzle-image'); // Get the image element
  const canvas = document.getElementById('canvas'); // Get the canvas element
  const ctx = canvas.getContext('2d'); // Get the 2D drawing context for the canvas

  // Default variables
  const fontSize = 20; // font size -- should we make this configurable?
  const saveTime = 10000; // how long to keep the localStorage

  /** Define what to do when the image loads **/
  img.onload = function() {
    // Set canvas dimensions to match the image dimensions
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;

    // Adjust the canvas size in the DOM to match the image
    canvas.style.width = img.width + 'px';
    canvas.style.height = img.height + 'px';

    // If there are letters, render them
    letters.forEach(letter => {
      drawLetter(letter.x, letter.y, letter.letter, push = false);
    });
  }

  /** Replace the HTML with data from the file **/
  data = readVpuz(data);

  // Read clue notes and letters
  var letters = lscache.get(data.letters_save) || [];
  var clue_notes = lscache.get(data.clue_notes_save) || [];

  // Load the image
  img.src = data['puzzle-image'];

  // Set the page title
  if (data.title) {
    document.title = data.title + ' | ' + document.title;
  }

  /** Clues **/

  // If there are no clues, hide the clue panel
  if (data['improved-clues'].length === 0) {
	  document.getElementById('clue-panels').style.display = 'none';
  }

  // Change the width of the clue-numbers depending on size
  const clueNumberLengths = data['improved-clues'].map(x => x.clues).flat().map(x => x.number.length);
  const clueNumberWidth = 0.9 * Math.max(...clueNumberLengths);

  var sheet = document.styleSheets[0];
  var rule = `.clue-number { min-width: ${clueNumberWidth}rem }`;
  sheet.insertRule(rule, sheet.cssRules.length);

  // Loop through clues and add to DOM
  var clueHTML = '', clueBoxId = 0;
  for (var i = 0; i < data['improved-clues'].length; i++) {
    // Add a clue panel
    clueHTML += `<div id="clues-${i}" class="clue-panel">\n`;
    // Add a title
    clueHTML += `  <h2 id="clues-${i}-title" class="clues-title">${data['improved-clues'][i].title}</h2>`;
    // Add a clue list ul
    clueHTML += `<ul class="clue-list" id="clue-list-${i}">`;
    // Add the list elements
    var thisHTML = '';
    data['improved-clues'][i].clues.forEach(obj => {
      thisHTML += `
          <li class="clue-item">
            <span class="clue-number">${obj.number}</span>
            <span class="clue-text">${obj.text}
            <input class="input-box note-style" id="clue-box-${clueBoxId}" type="text">
            </span>`
      if (obj.explanation) thisHTML += `<span class="clue-explanation">${obj.explanation}</span>\n`;
      thisHTML += "</li>\n";
      clueBoxId += 1;
    });
    clueHTML += thisHTML;
    // Close all the tags
    clueHTML += "</ul></div>\n";
  }
  // Add this HTML to the DOM
  document.getElementById("clue-panels").innerHTML = clueHTML;

  // Load clue notes if applicable
  for (var cnix = 0; cnix < clue_notes.length; cnix++) {
    var thisNote = clue_notes[cnix];
    if (thisNote) {
      var thisBox = document.getElementById(`clue-box-${cnix}`);
      thisBox.value = thisNote;
      thisBox.style.display = 'block';
    }
  }

  /** Now for the puzzle functionality **/
  // Create and style the overlay and circle elements
  const overlay = document.createElement('div');
  const circle = document.createElement('div');
  overlay.id = 'overlay';
  circle.id = 'circle';
  overlay.appendChild(circle);
  document.body.appendChild(overlay); // Append overlay to the body

  // Explicit dimensions for the circle
  const circleDiameter = fontSize * 1.5;
  circle.style.width = circleDiameter + 'px';
  circle.style.height = circleDiameter + 'px';

  let clickX, clickY; // Variables to store click coordinates
  //letters = lscache.get(data.letters_save) || []; // Array to store letters and their positions

  // Event listener for canvas clicks
  document.getElementById('canvas').addEventListener('click', function(event) {
    const rect = canvas.getBoundingClientRect(); // Get canvas bounding rectangle
    clickX = event.clientX - rect.left; // Calculate click's X coordinate relative to the canvas
    clickY = event.clientY - rect.top; // Calculate click's Y coordinate relative to the canvas

    // Calculate circle's position relative to the overlay
    const circleX = event.clientX - circleDiameter / 2;
    const circleY = event.clientY - circleDiameter / 2;

    // Position the circle around the clicked area
    circle.style.transform = `translate(${circleX}px, ${circleY}px)`;
    overlay.style.display = 'flex'; // Show the overlay
    overlay.style.pointerEvents = 'auto'; // Enable pointer events for the overlay

    // Add a keydown event listener to capture user input
    document.addEventListener('keydown', handleKeydown);
  });

  // Event listener to hide the overlay on click
  overlay.addEventListener('click', function() {
    overlay.style.display = 'none'; // Hide the overlay
    document.removeEventListener('keydown', handleKeydown); // Remove the keydown event listener
  });

  // Function to handle keydown events
  function handleKeydown(event) {
    if (overlay.style.display === 'flex') { // Check if the overlay is displayed
      const letter = event.key; // Get the pressed key
      if (letter === 'Backspace' || letter === 'Delete') {
        removeLetter(clickX, clickY); // Remove letter if Backspace or Delete is pressed
      } else if (letter.length === 1 && letter.match(/[a-z\.\=\+]/i)) {
        drawLetter(clickX, clickY, letter); // Draw the letter on the canvas
      }
      overlay.style.display = 'none'; // Hide the overlay
      // Remove the keydown event listener
      document.removeEventListener('keydown', handleKeydown);
    }
  }

  // Function to draw a letter centered at (x, y) on the canvas
  function drawLetter(x, y, letter, push = true) {
    ctx.font = `${fontSize}px Arial`; // Set font size and family
    ctx.fillStyle = 'black'; // Set text color

    letter = letter.toUpperCase(); // I don't see a reason to allow lowercase

    // make a "+" if the user entered "./=/+"
    if (letter.match(/[\.\=\+]/)) letter = '+';

    const textWidth = ctx.measureText(letter).width; // Measure text width
    const textHeight = parseInt(ctx.font, 10); // Approximate text height

    // Draw the text centered at (x, y)
    ctx.fillText(letter, x - textWidth / 2, y + textHeight / 2);

    // Store the letter and its position
    if (push) {
      letters.push({
        x,
        y,
        letter,
        width: textWidth,
        height: textHeight
      });
      lscache.set(data.letters_save, letters, saveTime);
    }

    // Confetti if needed
    checkIfSolved(data, letters);

  }

  // Function to remove a letter if clicked and backspace/delete is pressed
  function removeLetter(x, y) {
    // Find the letter close to the click coordinates
    const index = letters.findIndex(letter => {
      return Math.abs(letter.x - x) < letter.width / 2 && Math.abs(letter.y - y) < letter.height / 2;
    });

    if (index !== -1) {
      // Remove the letter from the array
      letters.splice(index, 1);
      lscache.set(data.letters_save, letters, saveTime);

      // Clear the canvas and redraw all remaining letters
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      letters.forEach(letter => {
        drawLetter(letter.x, letter.y, letter.letter, push = false);
      });
    }
  } // end removeLetter

  /** Dealing with clue note boxes **/
  // Select all .clue-item elements
  const items = document.querySelectorAll('.clue-item');

  // Function to save input-box text to localStorage
  function saveInputBoxText(inputBox) {
    var thisNum = parseInt(inputBox.id.split('-').at(-1))
    clue_notes[thisNum] = inputBox.value;
    lscache.set(data.clue_notes_save, clue_notes, saveTime);
  }

  // Function to check input box value and hide/show accordingly
  function checkInputBox(inputBox) {
    if (inputBox.value.trim() === '') {
      inputBox.style.display = 'none'; // Hide if input is empty
    } else {
      inputBox.style.display = 'block'; // Show if input is not empty
    }
  }

  // Loop through each item and add event listeners
  items.forEach(item => {
    // Find the input box within the clicked item
    let inputBox = item.querySelector('.input-box');

    // Add input event listener to check visibility
    item.addEventListener('input', function(event) {
      if (event.target.classList.contains('input-box')) {
        checkInputBox(event.target);
        saveInputBoxText(event.target);
      }
    });

    // Add blur event listener to hide the input box if it's empty
    item.addEventListener('focusout', function(event) {
      if (event.target.classList.contains('input-box')) {
        checkInputBox(event.target);
        saveInputBoxText(event.target);
      }
    });

    item.addEventListener('click', function() {
      // Show and focus the input box when the item is clicked
      inputBox.style.display = 'block';
      inputBox.focus();
    });

    // Add keydown event listener to the input box
    inputBox.addEventListener('keydown', function(event) {
      if (event.key === 'Enter') {
        inputBox.blur(); // Remove focus when Enter is pressed
      }
    });

  });

  // Show the modal when the info button is clicked
  document.getElementById('infoButton').addEventListener('click', function() {
    // Set the contents of the modal
    // Title
    var title = data.title;
    // Body
    var bodyHTML = '';
    if (data.author) bodyHTML += `<p id="modal-author">${data.author}</p>`;
    if (data.copyright) bodyHTML += `<p id="modal-copyright">${data.copyright}</p>`;
    if (data.notes) bodyHTML += `<p id="modal-notes">${data.notes}</p>`;
    // Show the modal
    showModal(title, bodyHTML);
  }); // end info

  // Create PDF when the print button is clicked
  document.getElementById('printButton').addEventListener('click', function() {
    const vpuzObj = data;
    // add the image to options
    options_obj = {'image': data['puzzle-image']};

    if (data['notes']) {
      options_obj['show_notepad'] = true;
    }
    // add some fake iPuz data
    vpuzObj['kind'] = ["http://ipuz.org/crossword#1"];
    vpuzObj["dimensions"] = {"height": 3, "width": 3};
    vpuzObj["puzzle"] = [ ["#", "#", "#"], ["#", "#", "#"], ["#", "#", "#"] ];

    const xw_constructor = new JSCrossword();
    const xw = xw_constructor.fromIpuz(vpuzObj);
    jscrossword_to_pdf(xw, options=options_obj);
  });

} // end loadPuzzle

/** Generic modal functionality **/
function showModal(title, body) {
  // set the values
  document.getElementById('modal-title').innerHTML = title;
  document.getElementById('modal-body').innerHTML = body;
  // show the modal
  document.getElementById('infoModal').style.display = 'flex';
}

// Hide the modal when the close button is clicked
document.getElementById('closeModal').addEventListener('click', function() {
  document.getElementById('infoModal').style.display = 'none';
});

// Hide the modal when clicking outside the modal content
document.getElementById('infoModal').addEventListener('click', function(event) {
  if (event.target === infoModal) {
    document.getElementById('infoModal').style.display = 'none';
  }
});

/** vPuz parsing **/
function readVpuz(data) {

  // Get a hash of the data
  const dataHash = hashCode(JSON.stringify(data));

  // Get the hash of the data
  data['letters_save'] = `cnvs_letters_${dataHash}`;
  data['clue_notes_save'] = `cnvs_notes_${dataHash}`;

  // If there's a "solution-string", add a sorted version
  if (data['solution-string']) {
    data['solution-string-sorted'] = sortString(data['solution-string']);
  }

  // If there's an "intro" but no notes, replace "notes" with "intro"
  if (data.intro && !data.notes) {
    data.notes = data.intro;
  }

  /** Standardize how the clues are presented **/
  const clues = [];

  // Iterate through the titles of the clues (if they exist)
  var titles = Object.keys(data['clues']) || {};

  titles.forEach(function(title) {
    var thisClues = [];
    data['clues'][title].forEach(function(clue) {
      var number = '•',
        text = '';
      explanation = null;
      // a "clue" can be an array or an object (or a string?)
      if (Array.isArray(clue)) {
        number = clue[0].toString();
        text = clue[1];
      } else if (typeof clue === 'string') {
        text = clue;
      } else { // object
        if (clue.number) {
          number = clue.number.toString();
        }
        text = clue.clue;
        explanation = clue.explanation;
      }
      var myObj = {
        'number': number,
        'text': text
      };
      if (explanation) myObj['explanation'] = explanation;
      thisClues.push(myObj);
    });
    clues.push({
      'title': title.split(':').at(-1),
      'clues': thisClues
    });
  });

  data['improved-clues'] = clues;
  return data;
}

// confetti code from https://gist.github.com/elrumo/3055a9163fd2d0d19f323db744b0a094
var confetti={maxCount:150,speed:2,frameInterval:15,alpha:1,gradient:!1,start:null,stop:null,toggle:null,pause:null,resume:null,togglePause:null,remove:null,isPaused:null,isRunning:null};!function(){confetti.start=s,confetti.stop=w,confetti.toggle=function(){e?w():s()},confetti.pause=u,confetti.resume=m,confetti.togglePause=function(){i?m():u()},confetti.isPaused=function(){return i},confetti.remove=function(){stop(),i=!1,a=[]},confetti.isRunning=function(){return e};var t=window.requestAnimationFrame||window.webkitRequestAnimationFrame||window.mozRequestAnimationFrame||window.oRequestAnimationFrame||window.msRequestAnimationFrame,n=["rgba(30,144,255,","rgba(107,142,35,","rgba(255,215,0,","rgba(255,192,203,","rgba(106,90,205,","rgba(173,216,230,","rgba(238,130,238,","rgba(152,251,152,","rgba(70,130,180,","rgba(244,164,96,","rgba(210,105,30,","rgba(220,20,60,"],e=!1,i=!1,o=Date.now(),a=[],r=0,l=null;function d(t,e,i){return t.color=n[Math.random()*n.length|0]+(confetti.alpha+")"),t.color2=n[Math.random()*n.length|0]+(confetti.alpha+")"),t.x=Math.random()*e,t.y=Math.random()*i-i,t.diameter=10*Math.random()+5,t.tilt=10*Math.random()-10,t.tiltAngleIncrement=.07*Math.random()+.05,t.tiltAngle=Math.random()*Math.PI,t}function u(){i=!0}function m(){i=!1,c()}function c(){if(!i)if(0===a.length)l.clearRect(0,0,window.innerWidth,window.innerHeight),null;else{var n=Date.now(),u=n-o;(!t||u>confetti.frameInterval)&&(l.clearRect(0,0,window.innerWidth,window.innerHeight),function(){var t,n=window.innerWidth,i=window.innerHeight;r+=.01;for(var o=0;o<a.length;o++)t=a[o],!e&&t.y<-15?t.y=i+100:(t.tiltAngle+=t.tiltAngleIncrement,t.x+=Math.sin(r)-.5,t.y+=.5*(Math.cos(r)+t.diameter+confetti.speed),t.tilt=15*Math.sin(t.tiltAngle)),(t.x>n+20||t.x<-20||t.y>i)&&(e&&a.length<=confetti.maxCount?d(t,n,i):(a.splice(o,1),o--))}(),function(t){for(var n,e,i,o,r=0;r<a.length;r++){if(n=a[r],t.beginPath(),t.lineWidth=n.diameter,e=(i=n.x+n.tilt)+n.diameter/2,o=n.y+n.tilt+n.diameter/2,confetti.gradient){var l=t.createLinearGradient(e,n.y,i,o);l.addColorStop("0",n.color),l.addColorStop("1.0",n.color2),t.strokeStyle=l}else t.strokeStyle=n.color;t.moveTo(e,n.y),t.lineTo(i,o),t.stroke()}}(l),o=n-u%confetti.frameInterval),requestAnimationFrame(c)}}function s(t,n,o){var r=window.innerWidth,u=window.innerHeight;window.requestAnimationFrame=window.requestAnimationFrame||window.webkitRequestAnimationFrame||window.mozRequestAnimationFrame||window.oRequestAnimationFrame||window.msRequestAnimationFrame||function(t){return window.setTimeout(t,confetti.frameInterval)};var m=document.getElementById("confetti-canvas");null===m?((m=document.createElement("canvas")).setAttribute("id","confetti-canvas"),m.setAttribute("style","display:block;z-index:999999;pointer-events:none;position:fixed;top:0"),document.body.prepend(m),m.width=r,m.height=u,window.addEventListener("resize",(function(){m.width=window.innerWidth,m.height=window.innerHeight}),!0),l=m.getContext("2d")):null===l&&(l=m.getContext("2d"));var s=confetti.maxCount;if(n)if(o)if(n==o)s=a.length+o;else{if(n>o){var f=n;n=o,o=f}s=a.length+(Math.random()*(o-n)+n|0)}else s=a.length+n;else o&&(s=a.length+o);for(;a.length<s;)a.push(d({},r,u));e=!0,i=!1,c(),t&&window.setTimeout(w,t)}function w(){e=!1}}();


// helper function to sort a string
function sortString(s) {
  return s.split("").sort().join("");
}

// Check if solved
function checkIfSolved(data, letters) {
  // Grab the solution string
  const solutionString = data['solution-string-sorted'];

  // Clean up letters user has typed
  const userLetters = letters.map(item => item.letter);
  const userLettersString = userLetters.join('');
  const cleanedStr = userLettersString.replace(/[^A-Za-z]/g, "");

  // We don't need to go on if the letter counts are mismatched
  if (!solutionString || solutionString.length !== cleanedStr.length) {
    return;
  }

  // Sort the letters the user has typed
  const userLettersSorted = sortString(cleanedStr);

  // If they match, make some confetti
  if (solutionString == userLettersSorted) {
    confetti.start();
    setTimeout(function() {
      confetti.stop()
    }, 3000);

    // If there are clue explanations, show them
    document.querySelectorAll('.clue-explanation').forEach(elt => {
      elt.style.display = 'block';
    });

    // If there's an "explanation", open a modal box and show it
    if (data.explanation) {
      showModal('Explanation', data.explanation);
    }
  }
} // end checkIfSolved

/**
 * Functions for loading a puzzle from the user
 **/

// Clicking the button opens the file menu
const openVpuzButton = document.getElementById('open-vpuz-button');
const openVpuzInput = document.getElementById('open-vpuz-input');
openVpuzButton.addEventListener('click', function() {
  openVpuzInput.click();
});

/** Helper function to check if the browser has drag-and-drop capability **/
function supportsDragAndDrop() {
  var div = document.createElement('div');
  return ('draggable' in div) || ('ondragstart' in div && 'ondrop' in div);
}

/**
 * Simple hash function
 * via https://stackoverflow.com/a/8831937
 **/
function hashCode(str) {
  let hash = 0;
  for (let i = 0, len = str.length; i < len; i++) {
    let chr = str.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash.toString();
}
