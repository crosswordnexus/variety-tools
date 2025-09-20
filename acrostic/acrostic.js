// Make py global
let py = null;

// 1) Bootstrap Pyodide & swiglpk once
const initPromise = (async () => {
	// Load pyodide and the swiglpk package
  py = await loadPyodide();
  await py.loadPackage("swiglpk");

  // Fetch the gzipped word list
  const resp = await fetch("spreadthewordlist.dict.gz");
  const buf = await resp.arrayBuffer();

	// Decompress word list with pako into a UTF-8 string
  const compressed = new Uint8Array(buf);
  const dictText = pako.ungzip(compressed, {
    to: "string"
  });

  // Write the decompressed text into Pyodide's virtual FS
  py.FS.writeFile("spreadthewordlist.dict", dictText);

	// Load in acrostic_glp
	const resp_glp = await fetch("acrostic_glp.py");
	const text_glp = await resp_glp.text();
	py.FS.writeFile("acrostic_glp.py", text_glp);

	// Import
	await py.runPythonAsync("from acrostic_glp import create_acrostic2");

  // Once everything is loaded, hide spinner and show controls
  document.getElementById('spinner').style.display = 'none';
  document.getElementById('loading-text').style.display = 'none';
  document.getElementById('controls').style.display = 'block';
  return py;
})();

// Wire up the UI
document.getElementById('solve-btn').addEventListener('click', async (e) => {
  e.preventDefault();
  const quote = document.getElementById('quote-input').value;
  const source = document.getElementById('source-input').value;

  const exclStr = document.getElementById('excluded-input').value;
  const excluded = exclStr.trim().split(',').filter(Boolean);

  const inclStr = document.getElementById('included-input').value;
  const included = inclStr.trim().split(',').filter(Boolean);

  const out = document.getElementById('output');
  out.textContent = 'Solving...\n';

  const py = await initPromise;
  py.globals.set('quote', quote);
  py.globals.set('source', source);
  py.globals.set('excluded', excluded);
  py.globals.set('included', included);

  // Redirect stdout and stderr to output element
  //py.setStdout({batched: (msg) => { out.textContent += msg; }});
  //py.setStderr({batched: (msg) => { out.textContent += msg; }});

  try {
		const res = await py.runPythonAsync(`create_acrostic2(quote, source, excluded, included)`);
    const sol = res.toJs();
    if (sol.length) {
      out.textContent = sol.join('\n');
    } else {
      out.textContent = 'No solutions found.';
    }
  } catch (e) {
    out.textContent += 'Error: ' + e;
  }
});
