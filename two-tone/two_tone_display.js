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
