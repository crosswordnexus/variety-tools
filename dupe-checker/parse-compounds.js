'use strict';

const fs = require('fs');
const path = require('path');

const csvPath = path.join(__dirname, 'compound_words.csv');
const outJsonPath = path.join(__dirname, 'compounds.json');

if (!fs.existsSync(csvPath)) {
  console.error('compound_words.csv not found at', csvPath);
  process.exit(1);
}

const content = fs.readFileSync(csvPath, 'utf8');
const lines = content.split(/\r?\n/).map(l => l.trim()).filter(Boolean);

const compounds = {};

// Parse lines
for (let i = 1; i < lines.length; i++) {
  const line = lines[i];
  const parts = line.split(',');
  if (parts.length < 2) continue;

  let word = parts[0].trim().toLowerCase();
  let splitCol = parts.slice(1).join(',').trim().toLowerCase();

  let splitParts = splitCol.split('-').map(p => p.trim()).filter(Boolean);
  let rejoined = splitParts.join('');

  // 1. If split column rejoined matches col 1
  if (rejoined === word) {
    compounds[word] = splitParts;
  } else {
    // 2. Add the split column compound if valid
    if (splitParts.length >= 2 && rejoined.length >= 4) {
      compounds[rejoined] = splitParts;
    }
    // 3. Special fix for known typo 'affereffect' -> 'aftereffect'
    if (word === 'affereffect' && rejoined === 'aftereffect') {
      compounds['aftereffect'] = splitParts;
    }
  }
}

// Extra high-value puzzle compounds
const extras = {
  dreamhouse: ['dream', 'house'],
  roughhouse: ['rough', 'house'],
  doghouse: ['dog', 'house'],
  hotdog: ['hot', 'dog'],
  runaway: ['run', 'away'],
  outdoors: ['out', 'doors'],
  baseball: ['base', 'ball'],
  football: ['foot', 'ball'],
  basketball: ['basket', 'ball'],
  sunflower: ['sun', 'flower'],
  raincoat: ['rain', 'coat'],
  teaspoon: ['tea', 'spoon'],
  tablespoon: ['table', 'spoon'],
  backseat: ['back', 'seat'],
  overturn: ['over', 'turn'],
  stopwatch: ['stop', 'watch'],
  crossword: ['cross', 'word'],
  cheesecake: ['cheese', 'cake'],
  pancake: ['pan', 'cake'],
  cupcake: ['cup', 'cake'],
  blueberry: ['blue', 'berry'],
  blackberry: ['black', 'berry'],
  strawberry: ['straw', 'berry'],
  watermelon: ['water', 'melon'],
  jellyfish: ['jelly', 'fish'],
  starfish: ['star', 'fish'],
  goldfish: ['gold', 'fish'],
  seashell: ['sea', 'shell'],
  seashore: ['sea', 'shore'],
  sunlight: ['sun', 'light'],
  moonlight: ['moon', 'light'],
  daylight: ['day', 'light'],
  firefly: ['fire', 'fly'],
  dragonfly: ['dragon', 'fly'],
  butterfly: ['butter', 'fly'],
  horseshoe: ['horse', 'shoe'],
  snowball: ['snow', 'ball'],
  snowman: ['snow', 'man'],
  snowflake: ['snow', 'flake'],
  sandcastle: ['sand', 'castle'],
  treehouse: ['tree', 'house'],
  birdhouse: ['bird', 'house'],
  playhouse: ['play', 'house'],
  greenhouse: ['green', 'house'],
  courthouse: ['court', 'house'],
  warehouse: ['ware', 'house'],
  farmhouse: ['farm', 'house'],
  lighthouse: ['light', 'house'],
  slaughterhouse: ['slaughter', 'house'],
  storehouse: ['store', 'house']
};

for (const [k, v] of Object.entries(extras)) {
  compounds[k] = v;
}

fs.writeFileSync(outJsonPath, JSON.stringify(compounds, null, 2), 'utf8');
console.log(`Saved ${Object.keys(compounds).length} compound words to ${outJsonPath}`);
