/* Persian morphology for the browser — mirror of scripts/persian_text.py.
 *
 * The ALGORITHM lives here; the DATA (affix tables, verb paradigms, broken
 * plurals, stopwords, exceptions, character map) is generated from Python into
 * docs/assets/js/persian-stem-data.js, so the two implementations cannot drift
 * on content. tools/check_stemmer_parity.js proves the algorithm agrees too:
 * it runs this file over tests/fixtures/stemming-golden.json in CI.
 *
 * Design rule (same as the data policy): when morphology is ambiguous, do
 * nothing. A missed stem only costs ranking; a wrong stem costs trust.
 *
 * Note on case folding: Python uses str.casefold(), JS uses toLowerCase().
 * tests/test_persian_text.py asserts that for every string in the dataset and
 * every string in the parity corpus the two are identical, so the difference
 * can never surface.
 */
(function (root, factory) {
  "use strict";
  var api = factory();
  if (typeof module !== "undefined" && module.exports) { module.exports = api; }
  if (root) { root.PersianStem = api; }
})(
  typeof window !== "undefined"
    ? window
    : typeof globalThis !== "undefined"
      ? globalThis
      : this,
  function () {
    "use strict";

    /* ---- data (generated) ------------------------------------------------ */
    var DATA =
      typeof PERSIAN_STEM_DATA !== "undefined"
        ? PERSIAN_STEM_DATA
        : typeof require === "function"
          ? require("./persian-stem-data.js")
          : null;
    if (!DATA) {
      throw new Error("persian-stem.js: persian-stem-data.js must be loaded first");
    }

    var ZWNJ = DATA.zwnj;
    var MIN_STEM_LENGTH = DATA.minStemLength;
    var MIN_PART_LENGTH = DATA.minPartLength;
    var MIN_ROOT_LENGTH = DATA.minRootLength;
    var SAFE_SUFFIXES = DATA.safeSuffixes;
    var GUARDED_SUFFIXES = DATA.guardedSuffixes;
    var PREFIXES = DATA.prefixes;
    var STOPWORDS = arrayToSet(DATA.stopwords);
    var STEM_EXCEPTIONS = arrayToSet(DATA.stemExceptions);
    var BROKEN_PLURALS = DATA.brokenPlurals;
    var VERB_STEMS = DATA.verbStems;
    var VERB_ENDINGS = DATA.verbEndings;
    var NO_SPLIT = arrayToSet(DATA.noSplit);
    var CONFUSABLES = arrayToSet(
      DATA.confusables.map(function (pair) { return pair[0] + "|" + pair[1]; })
    );

    /* derived tables (generated the same way Python generates them) */
    var STEM_TO_VERB = {};
    var CONJUGATIONS = {};
    Object.keys(VERB_STEMS).forEach(function (infinitive) {
      var past = VERB_STEMS[infinitive][0];
      var present = VERB_STEMS[infinitive][1];
      [past, present].forEach(function (stemForm) {
        if (!hasOwn(STEM_TO_VERB, stemForm)) { STEM_TO_VERB[stemForm] = infinitive; }
        VERB_ENDINGS.forEach(function (ending) {
          var form = stemForm + ending;
          if (!hasOwn(CONJUGATIONS, form)) {
            CONJUGATIONS[form] = [infinitive, past, present];
          }
        });
      });
    });

    /* character translation table */
    var CHAR_MAP = DATA.charMap;

    /* \w in Python's re covers Unicode letters/digits/underscore. JS \w is
     * ASCII-only, so Unicode property escapes are required. Harakat are not
     * word characters in either engine and are removed by normalize() anyway. */
    /* The hyphen stays inside a token so "self-consolidating" and "ACI 318-19"
     * survive as units; tokenize() then also emits their parts. (The trailing
     * "-" is literal inside a character class.) */
    var WORD_SPLIT_RE = /[^\p{L}\p{N}_\u200c-]+/gu;
    var DIGIT_RE = /^[0-9\u06f0-\u06f9\u0660-\u0669]+$/;

    /* ---- helpers --------------------------------------------------------- */
    function hasOwn(obj, key) {
      return Object.prototype.hasOwnProperty.call(obj, key);
    }

    function arrayToSet(list) {
      var set = {};
      (list || []).forEach(function (item) { set[item] = true; });
      return set;
    }

    function collapseSpace(text) {
      return text.replace(/\s+/g, " ").trim();
    }

    /* ---- normalization --------------------------------------------------- */
    function normalize(text) {
      if (!text) { return ""; }
      var out = String(text);
      if (typeof out.normalize === "function") { out = out.normalize("NFKC"); }
      var mapped = "";
      for (var i = 0; i < out.length; i++) {
        var ch = out.charAt(i);
        mapped += hasOwn(CHAR_MAP, ch) ? CHAR_MAP[ch] : ch;
      }
      return collapseSpace(mapped);
    }

    function fold(text) {
      return normalize(text).split(ZWNJ).join("").toLowerCase().trim();
    }

    function normalizeLatin(text) {
      if (!text) { return ""; }
      var out = String(text);
      if (typeof out.normalize === "function") { out = out.normalize("NFKC"); }
      return collapseSpace(out).toLowerCase();
    }

    /* ---- tokenization ---------------------------------------------------- */
    function tokenize(text) {
      var normalized = normalize(text);
      if (!normalized) { return []; }
      var tokens = [];
      var seen = {};

      function push(token) {
        token = token.trim();
        /* keeping "-" as a word character means a stray dash becomes a token */
        if (token && /[\p{L}\p{N}]/u.test(token) && !hasOwn(seen, token)) {
          seen[token] = true;
          tokens.push(token);
        }
      }

      normalized.split(WORD_SPLIT_RE).forEach(function (chunk) {
        if (!chunk) { return; }
        push(chunk);
        if (chunk.indexOf(ZWNJ) !== -1) {
          chunk.split(ZWNJ).forEach(push);
          push(chunk.split(ZWNJ).join(""));
        }
        if (chunk.indexOf("-") !== -1) {
          chunk.split("-").forEach(push);
        }
      });
      return tokens;
    }

    function contentTokens(text) {
      return tokenize(text).filter(function (token) {
        var bare = token.split(ZWNJ).join("");
        if (hasOwn(STOPWORDS, bare)) { return false; }
        if (DIGIT_RE.test(bare)) { return false; }
        return true;
      });
    }

    /* ---- lexicon guard --------------------------------------------------- */
    function isKnown(token, lexicon) {
      return !!lexicon && hasOwn(lexicon, fold(token));
    }

    function isProtected(token, protectedSet) {
      return !!protectedSet && hasOwn(protectedSet, fold(token));
    }

    function lexiconSet(list) {
      var set = {};
      (list || []).forEach(function (word) { set[word] = true; });
      return set;
    }

    /* ---- stemming -------------------------------------------------------- */
    function stripSuffix(token, lexicon) {
      var i, affix, rest;
      for (i = 0; i < SAFE_SUFFIXES.length; i++) {
        affix = SAFE_SUFFIXES[i];
        if (endsWith(token, affix) && token.length - affix.length >= MIN_STEM_LENGTH) {
          return token.slice(0, token.length - affix.length);
        }
      }
      for (i = 0; i < GUARDED_SUFFIXES.length; i++) {
        affix = GUARDED_SUFFIXES[i];
        if (endsWith(token, affix) && token.length - affix.length >= MIN_STEM_LENGTH) {
          rest = token.slice(0, token.length - affix.length);
          if (isKnown(rest, lexicon)) { return rest; }
        }
      }
      return token;
    }

    function stripPrefix(token, lexicon) {
      for (var i = 0; i < PREFIXES.length; i++) {
        var affix = PREFIXES[i];
        if (startsWith(token, affix) && token.length - affix.length >= MIN_STEM_LENGTH) {
          var rest = token.slice(affix.length);
          if (isKnown(rest, lexicon)) { return rest; }
        }
      }
      return token;
    }

    function endsWith(text, suffix) {
      return text.length >= suffix.length &&
        text.slice(text.length - suffix.length) === suffix;
    }

    function startsWith(text, prefix) {
      return text.slice(0, prefix.length) === prefix;
    }

    function stem(token, lexicon, protectedSet) {
      var normalized = normalize(token).trim();
      if (!normalized) { return normalized; }
      var bare = normalized.split(ZWNJ).join("");
      if (hasOwn(STEM_EXCEPTIONS, bare) || hasOwn(STEM_EXCEPTIONS, fold(bare))) {
        return bare;
      }
      /* a dictionary headword is a lexicalized unit: never reduce it */
      if (isProtected(bare, protectedSet)) { return bare; }
      if (hasOwn(BROKEN_PLURALS, bare)) { return BROKEN_PLURALS[bare]; }
      if (hasOwn(BROKEN_PLURALS, fold(bare))) { return BROKEN_PLURALS[fold(bare)]; }

      var current = bare;
      for (var round = 0; round < 2; round++) {
        var reduced = stripSuffix(current, lexicon);
        if (reduced === current) { break; }
        current = reduced;
        /* may land on a headword, but never continue past it (see persian_text.py) */
        if (isProtected(current, protectedSet)) { break; }
      }
      return current;
    }

    function root(token, lexicon, protectedSet) {
      var current = stem(token, lexicon, protectedSet);
      var folded = fold(current);
      if (hasOwn(BROKEN_PLURALS, folded)) { current = BROKEN_PLURALS[folded]; }

      if (!isProtected(current, protectedSet)) { current = stripPrefix(current, lexicon); }
      folded = fold(current);
      if (hasOwn(BROKEN_PLURALS, folded)) { return BROKEN_PLURALS[folded]; }

      if (hasOwn(STEM_TO_VERB, folded) && !hasOwn(STEM_EXCEPTIONS, folded)) {
        return current;
      }
      if (hasOwn(CONJUGATIONS, folded) && !hasOwn(STEM_EXCEPTIONS, folded)) {
        var past = CONJUGATIONS[folded][1];
        return past.length >= MIN_ROOT_LENGTH ? past : current;
      }
      return stem(current, lexicon, protectedSet);
    }

    function splitCompound(token, lexicon, protectedSet) {
      var bare = token.split(ZWNJ).join("");
      if (hasOwn(NO_SPLIT, bare) || hasOwn(STOPWORDS, fold(bare))) { return []; }
      if (bare.length < 2 * MIN_PART_LENGTH) { return []; }
      for (var cut = bare.length - MIN_PART_LENGTH; cut >= MIN_PART_LENGTH; cut--) {
        var head = bare.slice(0, cut);
        var tail = bare.slice(cut);
        if (head.length < MIN_PART_LENGTH || tail.length < MIN_PART_LENGTH) { continue; }
        var headKnown = isKnown(head, lexicon) || isKnown(stem(head, lexicon, protectedSet), lexicon);
        var tailKnown = isKnown(tail, lexicon) || isKnown(stem(tail, lexicon, protectedSet), lexicon);
        if (headKnown && tailKnown) { return [head, tail]; }
      }
      return [];
    }

    function indexForms(text, lexicon, protectedSet) {
      if (!text) { return []; }
      var forms = [];
      var seen = {};

      function push(value) {
        value = fold(value);
        if (value && !hasOwn(seen, value)) {
          seen[value] = true;
          forms.push(value);
        }
      }

      function pushFamily(value) {
        var key = fold(value);
        if (hasOwn(CONJUGATIONS, key)) {
          push(CONJUGATIONS[key][0]);
          push(CONJUGATIONS[key][1]);
          push(CONJUGATIONS[key][2]);
        }
        if (hasOwn(STEM_TO_VERB, key)) { push(STEM_TO_VERB[key]); }
      }

      push(text);
      /* space-free variant — see MAX_COLLAPSED_LENGTH in persian_text.py */
      var collapsed = fold(text).split(" ").join("");
      if (collapsed !== fold(text) && collapsed.length <= DATA.maxCollapsedLength) {
        push(collapsed);
      }
      tokenize(text).forEach(function (token) {
        push(token);
        push(stem(token, lexicon, protectedSet));
        var tokenRoot = root(token, lexicon, protectedSet);
        push(tokenRoot);

        var parts = splitCompound(token, lexicon, protectedSet).slice();
        if (token.indexOf(ZWNJ) !== -1) {
          token.split(ZWNJ).forEach(function (part) {
            if (part) { parts.push(part); }
          });
        }
        parts.forEach(function (part) {
          push(part);
          var partRoot = root(part, lexicon, protectedSet);
          push(partRoot);
          pushFamily(part);
          pushFamily(partRoot);
        });
        pushFamily(token);
        pushFamily(tokenRoot);
      });
      return forms;
    }

    /* ---- fuzzy matching -------------------------------------------------- */
    function editDistance(a, b, maxDistance) {
      if (a === b) { return 0; }
      if (Math.abs(a.length - b.length) > maxDistance) { return maxDistance + 1; }
      var previous = [];
      for (var j = 0; j <= b.length; j++) { previous.push(j); }
      for (var i = 1; i <= a.length; i++) {
        var current = [i];
        var best = i;
        for (var k = 1; k <= b.length; k++) {
          var cost = a.charAt(i - 1) === b.charAt(k - 1) ? 0 : 1;
          var value = Math.min(
            previous[k] + 1,
            current[k - 1] + 1,
            previous[k - 1] + cost
          );
          current.push(value);
          if (value < best) { best = value; }
        }
        if (best > maxDistance) { return maxDistance + 1; }
        previous = current;
      }
      return previous[b.length];
    }

    function suggest(token, vocabulary, maxDistance, limit) {
      maxDistance = maxDistance === undefined ? 1 : maxDistance;
      limit = limit === undefined ? 5 : limit;
      var target = fold(token);
      if (!target) { return []; }
      var scored = [];
      (vocabulary || []).forEach(function (word) {
        var candidate = fold(word);
        if (!candidate || candidate === target) { return; }
        if (startsWith(candidate, target) && candidate.length - target.length <= 3) {
          scored.push([0, candidate]);
          return;
        }
        if (startsWith(target, candidate) && target.length - candidate.length <= 3) {
          scored.push([1, candidate]);
          return;
        }
        if (candidate.length === target.length) {
          var diffIndex = -1;
          var diffs = 0;
          for (var i = 0; i < candidate.length; i++) {
            if (candidate.charAt(i) !== target.charAt(i)) {
              diffs++;
              diffIndex = i;
            }
          }
          if (diffs === 1) {
            var pair = candidate.charAt(diffIndex) + "|" + target.charAt(diffIndex);
            scored.push([hasOwn(CONFUSABLES, pair) ? 2 : 3, candidate]);
            return;
          }
        }
        var distance = editDistance(candidate, target, maxDistance);
        if (distance <= maxDistance) { scored.push([4 + distance, candidate]); }
      });
      scored.sort(function (a, b) {
        return a[0] - b[0] || (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0);
      });
      var out = [];
      var seen = {};
      for (var n = 0; n < scored.length && out.length < limit; n++) {
        var value = scored[n][1];
        if (!hasOwn(seen, value)) {
          seen[value] = true;
          out.push(value);
        }
      }
      return out;
    }

    return {
      version: DATA.algorithm,
      data: DATA,
      normalize: normalize,
      fold: fold,
      normalizeLatin: normalizeLatin,
      tokenize: tokenize,
      contentTokens: contentTokens,
      lexiconSet: lexiconSet,
      protectedSet: arrayToSet,
      stem: stem,
      root: root,
      splitCompound: splitCompound,
      indexForms: indexForms,
      editDistance: editDistance,
      suggest: suggest,
      stemToVerb: STEM_TO_VERB,
      conjugations: CONJUGATIONS
    };
  }
);
