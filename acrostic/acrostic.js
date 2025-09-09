// Make py global
let py = null;

// 1) Bootstrap Pyodide & swiglpk once
const initPromise = (async () => {
	py = await loadPyodide();
	await py.loadPackage("swiglpk");

	// 2) Fetch the gzipped word list
	const resp = await fetch("spreadthewordlist.dict.gz");
	const buf  = await resp.arrayBuffer();

	// 2) Decompress with pako into a UTF-8 string
	const compressed = new Uint8Array(buf);
	const dictText   = pako.ungzip(compressed, { to: "string" });

	// 3) Write the decompressed text into Pyodide's virtual FS
	py.FS.writeFile("spreadthewordlist.dict", dictText);

	// 3) Define solver in Python
	await py.runPythonAsync(`
import time, re, string
from collections import Counter
import gzip, io
import swiglpk as glp

MIN_SCORE = 50
WORDLIST = 'spreadthewordlist.dict'
LEN_DISTANCE = 2
MIN_WORD_LENGTH = 4

def is_substring(s1, s2):
    d1, d2 = Counter(s1), Counter(s2)
    return all(d2.get(k,0) >= v for k,v in d1.items())

def letter_count(word, letter):
    return word.count(letter)

def alpha_only(s):
    return re.sub(r'[^A-Za-z]+', '', s.lower())

def create_acrostic2(quote, source, excluded_words=[], included_words=[], wordlist=WORDLIST, min_score=MIN_SCORE):
    """
    Parameters
    ----------
    quote : string
        The quote we want to make an acrostic puzzle from.
    source : string
        The source of the quote (usually the author + work).
    excluded_words : list (optional)
        Words not to include in a solution.
    included_words: list (optional)
        Words to include in a solution.

    Returns
    -------
    soln_array: list
        A list of words comprising a feasible acrostic.

    This code relies heavily on the original create_acrostic function
    """

    def remove_string(s1, s2):
        # Remove the letters in s1 from s2
        s3 = s2.lower()
        for letter in alpha_only(s1):
            s3 = s3.replace(letter, '', 1)
        return s3

    # Make sure we are only including actual words
    included_words = [x for x in included_words if x]

    # Ensure the "source" is in the quote
    s1 = alpha_only(source)
    s2 = alpha_only(quote)
    try:
        assert is_substring(s1, s2)
    except AssertionError:
        raise AssertionError('Source is not contained in quote')

    if included_words:
        # Take the letters from the words we're including
        included_alpha = alpha_only(''.join(included_words))
        # Remove them from the quote
        quote2 = remove_string(included_alpha, quote)
        # Remove the first letters of included words for the source
        first_letters = ''.join(x[0] for x in included_words)
        source2 = remove_string(first_letters, source)
    else:
        source2 = alpha_only(source)
        quote2 = quote
    # Create the acrostic
    soln_array1 = create_acrostic_glpk(quote2, source2, excluded_words=excluded_words
                    , wordlist=wordlist, min_score=min_score)
    # Add in the missing words to this solution
    solution_words = soln_array1 + included_words
    soln_array = []
    for letter in alpha_only(source):
        good_words = [x for x in solution_words if x[0] == letter]
        if good_words:
            new_word = good_words[0]
            soln_array.append(new_word)
            solution_words.remove(new_word)
        else:
            return []
    return soln_array
#END create_acrostic2()

def create_acrostic_glpk(quote, source,
                         excluded_words=[],
                         wordlist=WORDLIST,
                         min_score=MIN_SCORE):
    t0 = time.time()
    source_alpha = alpha_only(source)
    quote_alpha  = alpha_only(quote)

    try:
        assert is_substring(source_alpha, quote_alpha)
    except AssertionError:
        raise AssertionError('Source is not contained in quote')

    qctr, sctr = Counter(quote_alpha), Counter(source_alpha)
    b = {L: qctr.get(L,0) for L in string.ascii_lowercase}
    b.update({f'_{L}': sctr.get(L,0) for L in string.ascii_lowercase})
    mean_len = len(quote_alpha) / len(source_alpha)
    min_len, max_len = mean_len - LEN_DISTANCE, mean_len + LEN_DISTANCE
    excl = {w.lower().strip() for w in excluded_words}
    words = []
    with open(wordlist) as f:
        for line in f:
            w, score = line.strip().split(';')
            w = w.lower().strip()
            if not (int(score) >= min_score and MIN_WORD_LENGTH <= len(w) <= max_len):
                continue
            if w[0] not in sctr or w in excl:
                continue
            if not is_substring(w[1:], quote_alpha):
                continue
            words.append(w)
    N = len(words)
    prob = glp.glp_create_prob()
    glp.glp_set_prob_name(prob, "acrostic")
    glp.glp_set_obj_dir(prob, glp.GLP_MIN)
    glp.glp_add_cols(prob, N)
    for j, w in enumerate(words, start=1):
        glp.glp_set_col_name(prob, j, w)
        glp.glp_set_col_kind(prob, j, glp.GLP_BV)
        glp.glp_set_obj_coef(prob, j, 0.0)
    letter_rows = list(qctr.keys())
    first_rows  = [f"_{L}" for L in sctr.keys()]
    all_rows    = letter_rows + first_rows
    glp.glp_add_rows(prob, len(all_rows))
    for i, row in enumerate(all_rows, start=1):
        rhs = b[row]
        glp.glp_set_row_name(prob, i, row)
        glp.glp_set_row_bnds(prob, i, glp.GLP_FX, rhs, rhs)
    entries = []
    for i, row in enumerate(letter_rows, start=1):
        for j, w in enumerate(words, start=1):
            c = letter_count(w, row)
            if c:
                entries.append((i, j, c))
    for i, row in enumerate(first_rows, start=len(letter_rows)+1):
        L = row[1:]
        for j, w in enumerate(words, start=1):
            if w.startswith(L):
                entries.append((i, j, 1))
    NZ = len(entries)
    ia = glp.intArray(NZ+1)
    ja = glp.intArray(NZ+1)
    ar = glp.doubleArray(NZ+1)
    for k, (i, j, v) in enumerate(entries, start=1):
        ia[k], ja[k], ar[k] = i, j, float(v)
    glp.glp_load_matrix(prob, NZ, ia, ja, ar)
    parm = glp.glp_iocp()
    glp.glp_init_iocp(parm)
    parm.presolve = glp.GLP_ON
    glp.glp_intopt(prob, parm)
    sol = {L: [] for L in source_alpha}
    for j, w in enumerate(words, start=1):
        if glp.glp_mip_col_val(prob, j) > 0.5:
            sol[w[0]].append(w)
    if sol[source_alpha[0]]:
        result = [sol[L].pop() for L in source_alpha]
        return result
    else:
        return []
	`);
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
		out.textContent = 'Entries:\n' + sol.join('\n');
	  } else {
		out.textContent = 'No solutions found.';
	  }
	} catch (e) {
	  out.textContent += 'Error: ' + e;
	}
});
