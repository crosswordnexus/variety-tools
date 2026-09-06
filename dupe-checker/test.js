'use strict';

const assert = require('assert');
const { areThereDupes, findDupes, DupeChecker, stem } = require('./index.js');

async function runTests() {
  console.log('--- Running Dupe Checker Tests ---\n');

  // Test 1: Suffix matches (quick / quickly)
  console.log('Test 1: Suffix match (quick, quickly)...');
  const res1 = await findDupes(['quick', 'quickly']);
  assert.strictEqual(res1.hasDupes, true, 'Should find dupe for quick and quickly');
  assert.ok(res1.dupes.some(d => d.type === 'suffix' && d.matchedSuffix === 'ly'), 'Suffix "ly" should match');
  console.log('✓ Passed: quick / quickly detected\n');

  // Test 2: Unrelated words (eating, shoes)
  console.log('Test 2: Non-duplicates (eating, shoes)...');
  const res2 = await areThereDupes(['eating', 'shoes']);
  assert.strictEqual(res2, false, 'Should be false for non-dupes');
  console.log('✓ Passed: eating / shoes is not a dupe\n');

  // Test 3: Base + ing (eating, eat)
  console.log('Test 3: Base and ing form (eat, eating)...');
  const res3 = await areThereDupes(['eat', 'eating']);
  assert.strictEqual(res3, true, 'Should detect eat and eating');
  console.log('✓ Passed: eat / eating detected\n');

  // Test 4: Intra-word repetition (bonbon, apple)
  console.log('Test 4: Intra-word repeat within a single entry (bonbon, apple)...');
  const res4 = await areThereDupes(['bonbon', 'apple']);
  assert.strictEqual(res4, false, 'Internal repetition should not flag as duplicate between entries');
  console.log('✓ Passed: bonbon does not trigger a false positive dupe\n');

  // Test 5: Unspaced phrase splitting with wordsninja (bluedog, dog walking)
  console.log('Test 5: Unspaced phrase split by wordsninja (bluedog, dog walking)...');
  const res5 = await findDupes(['bluedog', 'dog walking']);
  assert.strictEqual(res5.hasDupes, true, 'Should detect shared stem "dog" between bluedog and dog walking');
  assert.ok(res5.dupes.some(d => d.stem === 'dog'), 'Stem "dog" should be identified');
  console.log('✓ Passed: bluedog / dog walking detected via stem "dog"\n');

  // Test 6: Compound words decomposition (roughhouse, dreamhouse)
  console.log('Test 6: Compound words (roughhouse, dreamhouse)...');
  const res6 = await findDupes(['roughhouse', 'dreamhouse']);
  assert.strictEqual(res6.hasDupes, true, 'Should detect shared root "house" between roughhouse and dreamhouse');
  assert.ok(res6.dupes.some(d => d.stem === 'hous'), 'Stem "hous" should be identified');
  console.log('✓ Passed: roughhouse / dreamhouse detected via stem "hous" (house)\n');

  // Test 7: Compound word with phrase (runaway, running shoe)
  console.log('Test 7: Compound word with phrase (runaway, running shoe)...');
  const res7 = await findDupes(['runaway', 'running shoe']);
  assert.strictEqual(res7.hasDupes, true, 'Should detect shared stem "run" between runaway and running shoe');
  assert.ok(res7.dupes.some(d => d.stem === 'run'), 'Stem "run" should be identified');
  console.log('✓ Passed: runaway / running shoe detected via stem "run"\n');

  // Test 8: Suffix with 'less' (care, careless)
  console.log('Test 8: Suffix match with -less (care, careless)...');
  const res8 = await areThereDupes(['care', 'careless']);
  assert.strictEqual(res8, true, 'Should detect care and careless');
  console.log('✓ Passed: care / careless detected\n');

  // Test 9: Stopwords support
  console.log('Test 9: Stopwords filtering (callup, standup with stopword "up")...');
  // Without stopwords, "up" will trigger a dupe
  const res9Without = await areThereDupes(['callup', 'standup']);
  assert.strictEqual(res9Without, true, 'Without stopwords, "up" is flagged as a dupe');

  // With "up" as a stopword
  const res9With = await areThereDupes(['callup', 'standup'], { stopwords: ['up'] });
  assert.strictEqual(res9With, false, 'With stopword "up", "callup" and "standup" should not flag dupe');
  console.log('✓ Passed: stopwords support works as expected\n');

  // Test 10: Custom instance
  console.log('Test 10: DupeChecker instance reuse...');
  const checker = new DupeChecker();
  await checker.init();
  const res10 = await checker.areThereDupes(['walk', 'walking']);
  assert.strictEqual(res10, true);
  console.log('✓ Passed: DupeChecker instance works\n');

  // Test 11: Irregular verb + unspaced phrase (eating, ateup with stopword "up")
  console.log('Test 11: Irregular verb phrases (eating, ateup with stopword "up")...');
  const res11 = await findDupes(['eating', 'ateup'], { stopwords: ['up'] });
  assert.strictEqual(res11.hasDupes, true, 'Should detect shared root "eat" between eating and ateup');
  assert.ok(res11.dupes.some(d => d.stem === 'eat'), 'Stem "eat" should be identified');
  console.log('✓ Passed: eating / ateup detected via shared root "eat"\n');

  // Test 12: Direct irregular verb pairs (eat / ate, went / going)
  console.log('Test 12: Direct irregular verbs (eat, ate; went, going)...');
  const res12A = await findDupes(['eat', 'ate']);
  assert.strictEqual(res12A.hasDupes, true, 'Should detect eat and ate');
  const res12B = await findDupes(['went', 'going']);
  assert.strictEqual(res12B.hasDupes, true, 'Should detect went and going');
  console.log('✓ Passed: direct irregular verbs detected\n');

  // Test 13: Irregular plural with compound (mice, mousetrap)
  console.log('Test 13: Irregular plural with compound (mice, mousetrap)...');
  const res13 = await findDupes(['mice', 'mousetrap']);
  assert.strictEqual(res13.hasDupes, true, 'Should detect shared root "mouse" between mice and mousetrap');
  console.log('✓ Passed: mice / mousetrap detected via shared root "mouse"\n');

  console.log('All tests passed successfully!');
}

runTests().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
