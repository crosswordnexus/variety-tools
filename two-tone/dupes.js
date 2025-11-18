
/** Functions to help check for dupes **/

// turn a phrase into an array of root forms using `compromise`
function lemmatize(phrase) {
  var doc = nlp(phrase);
  //compute all roots
  doc.compute('root');
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
  const boxNames = ['two-tone', 'odd-squares', 'even-squares'];
  const words = {};
  boxNames.forEach(box => {
    let wordsArr = document.getElementById(box).value.split('\n');
    wordsArr.forEach(w => {
      if (!w) return;
      // infer spaces and lemmatize
      let w3 = lemmatize(inferSpaces(w.toLowerCase()))
      w3.forEach(w4 => {
        if (!words[w4]) words[w4] = [];
        words[w4].push(w);
      });
    });
  });

  //console.log(words);

  // Prepare text for an alert
  var alertText = '';
  Object.keys(words).forEach(k => {
    if (words[k].size > 1 && k.length >= 3) {
      let dupeDisplay = [...words[k]].join(', ');
      alertText += `${k} => ${dupeDisplay}\n`;
    }
  });
  if (!alertText) alertText = "No dupes found.";
  alert(alertText);
}

// Dupe button functionality
document.getElementById('checkdupes-button').addEventListener('click', checkForDupes);
