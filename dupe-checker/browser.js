'use strict';

const { DupeChecker, areThereDupes, findDupes, stem, DEFAULT_SUFFIXES } = require('./index.js');

const globalChecker = new DupeChecker();

if (typeof window !== 'undefined') {
  window.DupeChecker = DupeChecker;
  window.globalDupeChecker = globalChecker;
  window.areThereDupes = (arr, opts) => globalChecker.areThereDupes(arr, opts);
  window.findDupes = (arr, opts) => globalChecker.findDupes(arr, opts);
  window.stem = stem;
  window.DEFAULT_SUFFIXES = DEFAULT_SUFFIXES;
}

module.exports = {
  DupeChecker,
  areThereDupes,
  findDupes,
  stem,
  DEFAULT_SUFFIXES
};
