let currentXw = null;
const GRAY = '999999';

document.getElementById('process-button').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) return alert("Please upload a file.");

    const buf = await file.arrayBuffer();
    const data = new Uint8Array(buf);
    
    try {
        currentXw = JSCrossword.fromData(data);
        const quote = document.getElementById('quote-input').value;

        if (quote) {
            applyQuoteLogic(currentXw, quote);
        } else {
            applyDefaultLogic(currentXw);
        }
        
        document.getElementById('display-area').textContent = `Processed puzzle: "${currentXw.metadata.title}"`;
        document.getElementById('export-button').disabled = false;
        
    } catch (err) {
        console.error(err);
        alert("Failed to process puzzle.");
    }
});

document.getElementById('export-button').addEventListener('click', () => {
    if (!currentXw) return;
    const ipuz = currentXw.toIpuzString();
    const blob = new Blob([ipuz], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'going_too_far.ipuz';
    a.click();
});

function applyQuoteLogic(xw, quote) {
    const quoteAlpha = quote.replace(/[^A-Za-z]/g, '').toUpperCase();
    let quoteIx = 0;
    
    xw.cells.forEach(cell => {
        if (cell.type === 'block' && quoteIx < quoteAlpha.length) {
            cell.type = 'normal';
            cell.solution = quoteAlpha[quoteIx];
            cell['background-color'] = GRAY;
            quoteIx++;
        }
    });
}

function applyDefaultLogic(xw) {
    const blackSquareLocations = new Set();
    const GRAY = '999999';
    
    // Step 1 & 2: remove bars, turn circles to gray
    xw.cells.forEach(cell => {
        cell['right-bar'] = false;
        cell['bottom-bar'] = false;
        cell['top-bar'] = false;
        cell['left-bar'] = false;
        
        if (cell['background-shape'] === 'circle') {
            cell['background-shape'] = null;
            cell['background-color'] = GRAY;
            blackSquareLocations.add(`${cell.x},${cell.y}`);
        }
    });
    
    // 3. Remove circled letters (those now gray squares) from their words
    xw.words.forEach(word => {
        word.cells = word.cells.filter(([x, y]) => !blackSquareLocations.has(`${x},${y}`));
    });

    // 4. Re-number
    let number = 1;
    for (let y = 0; y < xw.metadata.height; y++) {
        for (let x = 0; x < xw.metadata.width; x++) {
            const thisCell = xw.cells.find(c => c.x === x && c.y === y);
            if (!thisCell) continue;

            if (thisCell['background-color'] === GRAY) {
                thisCell.number = null;
                continue;
            }

            const isGrayLeft = (x === 0) || (xw.cells.find(c => c.x === x - 1 && c.y === y)?.['background-color'] === GRAY);
            const isGrayUp = (y === 0) || (xw.cells.find(c => c.x === x && c.y === y - 1)?.['background-color'] === GRAY);

            const startsAcross = isGrayLeft;
            const startsDown = isGrayUp;

            if (startsAcross || startsDown) {
                thisCell.number = number.toString();
                
                // Update clues
                xw.clues.forEach(clueSet => {
                    clueSet.clue.forEach(clue => {
                        const word = xw.words.find(w => w.id === clue.word);
                        if (word && word.cells.some(([cx, cy]) => cx === x && cy === y)) {
                            clue.number = number.toString();
                        }
                    });
                });
                number++;
            } else {
                thisCell.number = null;
            }
        }
    }
    
    // 5. Re-sort clues (Basic re-sort)
    xw.clues.forEach(clueSet => {
        clueSet.clue.sort((a, b) => parseInt(a.number) - parseInt(b.number));
    });
}
