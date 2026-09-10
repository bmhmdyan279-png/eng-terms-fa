#!/usr/bin/env node
/* Dev tool: run the browser search engine headlessly over a list of queries.
 *
 *   node tools/search_probe.js آجر بند rebar "آب‌بندی"
 *
 * It loads the exact same modules the site loads (persian-stem.js +
 * persian-search.js) against the generated index, then prints the ranking.
 * Use it to eyeball relevance before shipping a data change.
 */
"use strict";

const fs = require("fs");
const path = require("path");

const REPO = path.resolve(__dirname, "..");
const JS = path.join(REPO, "docs", "assets", "js");

const Stem = require(path.join(JS, "persian-stem.js"));
globalThis.PersianStem = Stem;

const searcher = require(path.join(JS, "persian-search.js"));
const index = JSON.parse(
  fs.readFileSync(path.join(REPO, "docs", "data", "api", "search-index.json"), "utf8")
);

searcher.state.index = index;
searcher.state.lexicon = Stem.lexiconSet(index.lexicon);
searcher.state.protected = Stem.protectedSet(index.protected || []);
searcher.state.vocabulary = searcher.buildVocabulary(index, Stem, searcher.state.lexicon, searcher.state.protected);

const queries = process.argv.slice(2);
if (!queries.length) {
  process.stderr.write("usage: node tools/search_probe.js QUERY [QUERY ...]\n");
  process.exit(2);
}

for (const query of queries) {
  const outcome = searcher.search(query);
  process.stdout.write(`\n▌ «${query}» → ${outcome ? outcome.total : 0} نتیجه\n`);
  if (!outcome) { continue; }
  outcome.results.slice(0, 8).forEach((hit, i) => {
    const entry = hit.entry;
    const roots = entry.r && entry.r.length ? `  roots=${entry.r.join(",")}` : "";
    process.stdout.write(
      `   ${String(i + 1).padStart(2)}. ${entry.fa}  [${entry.en}]  score=${hit.score.toFixed(2)}${roots}\n`
    );
  });
  if (outcome.suggestions.length) {
    process.stdout.write(`   پیشنهاد: ${outcome.suggestions.join("، ")}\n`);
  }
  if (outcome.roots.length) {
    process.stdout.write(`   ریشه‌های هم‌خانواده: ${outcome.roots.join("، ")}\n`);
  }
}
