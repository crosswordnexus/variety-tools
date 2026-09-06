// Porter Stemmer algorithm in JavaScript
// Based on Martin Porter's 1980 algorithm (http://tartarus.org/~martin/PorterStemmer/)

const step2list = {
  ational: 'ate',
  tional: 'tion',
  enci: 'ence',
  anci: 'ance',
  izer: 'ize',
  bli: 'ble',
  alli: 'al',
  entli: 'ent',
  eli: 'e',
  ousli: 'ous',
  ization: 'ize',
  ation: 'ate',
  ator: 'ate',
  alism: 'al',
  iveness: 'ive',
  fulness: 'ful',
  ousness: 'ous',
  aliti: 'al',
  iviti: 'ive',
  biliti: 'ble',
  logi: 'log'
};

const step3list = {
  icate: 'ic',
  ative: '',
  alize: 'al',
  iciti: 'ic',
  ical: 'ic',
  ful: '',
  ness: ''
};

const c = '[^aeiou]';          // consonant
const v = '[aeiouy]';          // vowel
const C = c + '[^aeiouy]*';    // consonant sequence
const V = v + '[aeiou]*';      // vowel sequence

const mgr0 = '^(' + C + ')?' + V + C;               // [C]VC... is m>0
const meq1 = '^(' + C + ')?' + V + C + '(' + V + ')?$'; // [C]VC[V] is m=1
const mgr1 = '^(' + C + ')?' + V + C + V + C;       // [C]VCVC... is m>1
const s_v = '^(' + C + ')?' + v;                    // vowel in stem

function stem(word) {
  let stem;
  let suffix;
  let firstch;
  let re;
  let re2;
  let re3;
  let re4;

  let origWord = String(word).toLowerCase();

  if (origWord.length < 3) {
    return origWord;
  }

  firstch = origWord.substr(0, 1);
  if (firstch === 'y') {
    origWord = 'Y' + origWord.substr(1);
  }

  // Step 1a
  re = /^(.+?)(ss|i)es$/;
  re2 = /^(.+?)([^s])s$/;

  if (re.test(origWord)) {
    origWord = origWord.replace(re, '$1$2');
  } else if (re2.test(origWord)) {
    origWord = origWord.replace(re2, '$1$2');
  }

  // Step 1b
  re = /^(.+?)eed$/;
  re2 = /^(.+?)(ed|ing)$/;
  if (re.test(origWord)) {
    let fp = re.exec(origWord);
    re = new RegExp(mgr0);
    if (re.test(fp[1])) {
      re = /.$/;
      origWord = origWord.replace(re, '');
    }
  } else if (re2.test(origWord)) {
    let fp = re2.exec(origWord);
    stem = fp[1];
    re2 = new RegExp(s_v);
    if (re2.test(stem)) {
      origWord = stem;
      re2 = /(at|bl|iz)$/;
      re3 = new RegExp('([^aeiouylsz])\\1$');
      re4 = new RegExp('^' + C + v + '[^aeiouwxy]$');
      if (re2.test(origWord)) {
        origWord = origWord + 'e';
      } else if (re3.test(origWord)) {
        re = /.$/;
        origWord = origWord.replace(re, '');
      } else if (re4.test(origWord)) {
        origWord = origWord + 'e';
      }
    }
  }

  // Step 1c
  re = /^(.+?)y$/;
  if (re.test(origWord)) {
    let fp = re.exec(origWord);
    stem = fp[1];
    re = new RegExp(s_v);
    if (re.test(stem)) {
      origWord = stem + 'i';
    }
  }

  // Step 2
  re = /^(.+?)(ational|tional|enci|anci|izer|bli|alli|entli|eli|ousli|ization|ation|ator|alism|iveness|fulness|ousness|aliti|iviti|biliti|logi)$/;
  if (re.test(origWord)) {
    let fp = re.exec(origWord);
    stem = fp[1];
    suffix = fp[2];
    re = new RegExp(mgr0);
    if (re.test(stem)) {
      origWord = stem + step2list[suffix];
    }
  }

  // Step 3
  re = /^(.+?)(icate|ative|alize|iciti|ical|ful|ness)$/;
  if (re.test(origWord)) {
    let fp = re.exec(origWord);
    stem = fp[1];
    suffix = fp[2];
    re = new RegExp(mgr0);
    if (re.test(stem)) {
      origWord = stem + step3list[suffix];
    }
  }

  // Step 4
  re = /^(.+?)(al|ance|ence|er|ic|able|ible|ant|ement|ment|ent|ou|ism|ate|iti|ous|ive|ize)$/;
  re2 = /^(.+?)(s|t)(ion)$/;
  if (re.test(origWord)) {
    let fp = re.exec(origWord);
    stem = fp[1];
    re = new RegExp(mgr1);
    if (re.test(stem)) {
      origWord = stem;
    }
  } else if (re2.test(origWord)) {
    let fp = re2.exec(origWord);
    stem = fp[1] + fp[2];
    re2 = new RegExp(mgr1);
    if (re2.test(stem)) {
      origWord = stem;
    }
  }

  // Step 5
  re = /^(.+?)e$/;
  if (re.test(origWord)) {
    let fp = re.exec(origWord);
    stem = fp[1];
    re = new RegExp(mgr1);
    re2 = new RegExp(meq1);
    re3 = new RegExp('^' + C + v + '[^aeiouwxy]$');
    if (re.test(stem) || (re2.test(stem) && !(re3.test(stem)))) {
      origWord = stem;
    }
  }

  re = /ll$/;
  re2 = new RegExp(mgr1);
  if (re.test(origWord) && re2.test(origWord)) {
    re = /.$/;
    origWord = origWord.replace(re, '');
  }

  // Turn initial Y back to y
  if (firstch === 'y') {
    origWord = 'y' + origWord.substr(1);
  }

  return origWord;
}

module.exports = { stem };
