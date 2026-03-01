let originalData = null;
let patches = [];

document.getElementById('file-input').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            originalData = JSON.parse(e.target.result);
            processPuzzle();
        } catch (err) {
            alert("Error parsing .ipuz file: " + err.message);
        }
    };
    reader.readAsText(file);
});

function processPuzzle() {
    const dimensions = originalData.dimensions;
    const puzzle = originalData.puzzle;
    const solution = originalData.solution;

    // Ported from Python: Identify patches
    patches = getPatches(puzzle, dimensions);

    // Generate UI for Rows
    const rowsContainer = document.getElementById('rows-container');
    rowsContainer.innerHTML = '<h3>Rows</h3>';
    for (let r = 0; r < dimensions.height; r++) {
        const rowSolution = solution[r].join("");
        const label = r < 26 ? String.fromCharCode(65 + r) : (r + 1).toString();
        addRowInput(rowsContainer, `Row ${label}`, rowSolution, `row-${r}`);
    }

    // Generate UI for Patches
    const patchesContainer = document.getElementById('patches-container');
    patchesContainer.innerHTML = '<h3>Patches</h3>';
    patches.forEach((patch, i) => {
        const patchSolution = patch.map(([r, c]) => solution[r][c]).join("");
        addRowInput(patchesContainer, `Patch ${i + 1}`, patchSolution, `patch-${i}`);
    });

    document.getElementById('editor').classList.remove('hidden');
    document.getElementById('download-btn').style.display = 'block';
}

function addRowInput(container, label, answer, id) {
    const div = document.createElement('div');
    div.className = 'clue-row';
    div.innerHTML = `
        <label for="${id}">${label}</label>
        <input type="text" id="${id}" placeholder="Enter clue here..." value="${answer}">
        <span class="answer">(${answer})</span>
    `;
    container.appendChild(div);
}

function areConnected(r1, c1, r2, c2, puzzle) {
    if (r1 === r2) { // Same row, check horizontal connection (Right bar)
        const cMin = Math.min(c1, c2);
        const cell = puzzle[r1][cMin];
        const style = (cell && typeof cell === 'object') ? (cell.style || {}) : {};
        const barred = style.barred || '';
        return !barred.includes('R');
    }
    if (c1 === c2) { // Same column, check vertical connection (Bottom bar)
        const rMin = Math.min(r1, r2);
        const cell = puzzle[rMin][c1];
        const style = (cell && typeof cell === 'object') ? (cell.style || {}) : {};
        const barred = style.barred || '';
        return !barred.includes('B');
    }
    return false;
}

function getPatches(puzzle, dimensions) {
    const height = dimensions.height;
    const width = dimensions.width;
    const visited = new Set();
    const foundPatches = [];

    for (let r = 0; r < height; r++) {
        for (let c = 0; c < width; c++) {
            const key = `${r},${c}`;
            if (!visited.has(key)) {
                const newPatch = [];
                const queue = [[r, c]];
                visited.add(key);

                while (queue.length > 0) {
                    const [currR, currC] = queue.shift();
                    newPatch.push([currR, currC]);

                    const neighbors = [[0, 1], [0, -1], [1, 0], [-1, 0]];
                    for (const [dr, dc] of neighbors) {
                        const nr = currR + dr;
                        const nc = currC + dc;
                        const nKey = `${nr},${nc}`;
                        if (nr >= 0 && nr < height && nc >= 0 && nc < width) {
                            if (!visited.has(nKey) && areConnected(currR, currC, nr, nc, puzzle)) {
                                visited.add(nKey);
                                queue.push([nr, nc]);
                            }
                        }
                    }
                }
                // Sort cells: row-major order
                newPatch.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
                foundPatches.push(newPatch);
            }
        }
    }
    // Sort patches by their first cell
    foundPatches.sort((a, b) => a[0][0] - b[0][0] || a[0][1] - b[0][1]);
    return foundPatches;
}

document.getElementById('download-btn').addEventListener('click', function() {
    const isHard = document.querySelector('input[name="difficulty"]:checked').value === 'hard';
    const dimensions = originalData.dimensions;
    const height = dimensions.height;
    const width = dimensions.width;
    const solution = originalData.solution;

    // 1. Generate Rows Clues
    const rowsClues = [];
    for (let r = 0; r < height; r++) {
        const clueText = document.getElementById(`row-${r}`).value;
        const label = r < 26 ? String.fromCharCode(65 + r) : (r + 1).toString();
        const cells = [];
        for (let c = 0; c < width; c++) {
            cells.push([c + 1, r + 1]);
        }
        rowsClues.push({
            clue: clueText,
            number: label,
            cells: cells
        });
    }

    // 2. Identify Patches and Generate Patches Clues
    const patchesCluesData = [];
    const newPuzzle = [];
    for (let r = 0; r < height; r++) {
        const newRow = [];
        for (let c = 0; c < width; c++) {
            const rawCell = originalData.puzzle[r][c];
            let cellData = typeof rawCell === 'object' ? { ...rawCell } : { cell: rawCell };
            
            if (c === 0) {
                cellData.cell = r < 26 ? String.fromCharCode(65 + r) : (r + 1).toString();
            } else {
                cellData.cell = "_";
            }
            newRow.push(cellData);
        }
        newRow.forEach(cell => { if (cell.style && cell.style.mark) delete cell.style.mark; });
        newPuzzle.push(newRow);
    }

    patches.forEach((patchCells, i) => {
        const patchNum = (i + 1).toString();
        const clueText = document.getElementById(`patch-${i}`).value;
        const patchSolution = patchCells.map(([r, c]) => solution[r][c]).join("");
        const cells = patchCells.map(([r, c]) => [c + 1, r + 1]);

        patchesCluesData.push({
            clue: clueText,
            number: isHard ? "•" : patchNum,
            cells: cells,
            answer: patchSolution // for sorting in hard mode
        });

        if (!isHard) {
            const [firstR, firstC] = patchCells[0];
            if (!newPuzzle[firstR][firstC].style) newPuzzle[firstR][firstC].style = {};
            if (!newPuzzle[firstR][firstC].style.mark) newPuzzle[firstR][firstC].style.mark = {};
            newPuzzle[firstR][firstC].style.mark.TR = patchNum;
        }
    });

    if (isHard) {
        // Sort clues by answer alphabetically
        const sortedClues = patchesCluesData.slice().sort((a, b) => a.answer.localeCompare(b.answer));
        // Re-assign clue text back to the spatial clue objects
        for (let i = 0; i < patchesCluesData.length; i++) {
            patchesCluesData[i].clue = sortedClues[i].clue;
        }
    }

    const patchesClues = patchesCluesData.map(({ answer, ...rest }) => rest);

    let notes = "Each row in a Patchwork puzzle has two answers, to be entered in the grid in order. " +
                "Answers will also be entered in the irregularly shaped patchwork pieces marked by " +
                "heavy lines in the grid, always left to right, row by row within each piece.";
    if (isHard) {
        notes += "\n\nClues for the patches are given, but it is up to you to determine which " +
                 "clue goes with which patch. Clues for the patches are given in alphabetical " +
                 "order by answer.";
    }

    const outputData = {
        version: originalData.version || "http://ipuz.org/v1",
        kind: originalData.kind || ["http://ipuz.org/crossword#1"],
        title: originalData.title || "",
        copyright: originalData.copyright || "",
        author: originalData.author || "",
        notes: notes,
        intro: notes,
        dimensions: dimensions,
        block: originalData.block || "#",
        empty: "_",
        puzzle: newPuzzle,
        solution: solution,
        clues: {
            "Rows": rowsClues,
            "Patches": patchesClues
        }
    };

    if (isHard) {
        outputData.fakecluegroups = ["Patches"];
    }

    downloadJSON(outputData, (originalData.title || "patchwork") + "_converted.ipuz");
});

function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
