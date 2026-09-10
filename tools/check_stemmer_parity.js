#!/usr/bin/env node
/* Prove that the browser stemmer and the build stemmer agree.
 *
 *   python scripts/build_search_index.py   # writes the golden fixture
 *   node tools/check_stemmer_parity.js     # this file
 *
 * Every case in tests/fixtures/stemming-golden.json holds the Python engine's
 * output. This script runs docs/assets/js/persian-stem.js over the same input
 * and compares normalize / fold / tokenize / content_tokens / stem / root /
 * forms field by field. Any difference is a release blocker: a user searching
 * from the browser must get what the build indexed.
 *
 * Exit code 0 = identical, 1 = divergence, 2 = missing prerequisites.
 */
"use strict";

const fs = require("fs");
const path = require("path");

const REPO = path.resolve(__dirname, "..");
const FIXTURE = path.join(REPO, "tests", "fixtures", "stemming-golden.json");
const INDEX = path.join(REPO, "docs", "data", "api", "search-index.json");

function fail(message) {
  process.stderr.write(`check_stemmer_parity: ${message}\n`);
  process.exit(2);
}

if (!fs.existsSync(FIXTURE)) {
  fail(`missing ${FIXTURE} — run: python scripts/build_search_index.py`);
}
if (!fs.existsSync(INDEX)) {
  fail(`missing ${INDEX} — run: python scripts/build_search_index.py`);
}

const fixture = JSON.parse(fs.readFileSync(FIXTURE, "utf8"));
const index = JSON.parse(fs.readFileSync(INDEX, "utf8"));

const Stem = require(path.join(REPO, "docs", "assets", "js", "persian-stem.js"));
const lexicon = Stem.lexiconSet(index.lexicon);
const protectedSet = Stem.protectedSet(index.protected || []);

if (lexicon && Object.keys(lexicon).length !== index.lexicon_size) {
  fail(
    `lexicon size mismatch: index says ${index.lexicon_size}, loaded ${Object.keys(lexicon).length}`
  );
}

const CHECKS = [
  ["normalize", (c) => Stem.normalize(c.input)],
  ["fold", (c) => Stem.fold(c.input)],
  ["tokenize", (c) => Stem.tokenize(c.input)],
  ["content_tokens", (c) => Stem.contentTokens(c.input)],
  ["stem", (c) => Stem.tokenize(c.input).map((t) => Stem.stem(t, lexicon, protectedSet))],
  ["root", (c) => Stem.tokenize(c.input).map((t) => Stem.root(t, lexicon, protectedSet))],
  ["forms", (c) => Stem.indexForms(c.input, lexicon, protectedSet)],
];

let failures = 0;
let compared = 0;

for (const testCase of fixture.cases) {
  for (const [name, compute] of CHECKS) {
    compared++;
    const expected = JSON.stringify(testCase[name]);
    const actual = JSON.stringify(compute(testCase));
    if (expected !== actual) {
      failures++;
      if (failures <= 20) {
        process.stderr.write(
          [
            `DIVERGENCE [${name}] input=${JSON.stringify(testCase.input)}`,
            `  python: ${expected}`,
            `  js    : ${actual}`,
          ].join("\n") + "\n"
        );
      }
    }
  }
}

if (failures) {
  process.stderr.write(
    `\n✗ stemmer parity FAILED: ${failures} divergence(s) in ${compared} comparisons\n`
  );
  process.exit(1);
}

process.stdout.write(
  `✓ stemmer parity: ${fixture.cases.length} cases × ${CHECKS.length} checks ` +
    `= ${compared} comparisons identical (algorithm ${fixture.algorithm})\n`
);
