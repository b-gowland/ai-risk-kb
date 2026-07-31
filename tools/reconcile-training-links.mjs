#!/usr/bin/env node
// reconcile-training-links.mjs
//
// Reconciles every inbound link from the KB to the training app against the
// app's actual live scenario set after the four-beat rebuild.
//
// Three dispositions, applied deterministically:
//   LIVE (id is registered in the app)   → keep the deep link, strip the stale
//                                           "N personas, ~M minutes" descriptor
//                                           (personas were retired in the rebuild)
//                                           and normalise the label.
//   PENDING (id known but not yet live)  → keep the URL (the app shows a
//                                           "not playable yet, the reference
//                                           entry stays" soft-landing for known
//                                           ids), but reword the link so it does
//                                           not promise play, and drop the stale
//                                           descriptor.
//   EVERYDAY (/#/everyday inline links)  → repoint to the app home '/', since the
//                                           /everyday route now just redirects there.
//
// The LIVE set is passed in (from the app repo) so this script never guesses.
// Run with no flag to preview (dry run); --write to apply.
//
// Usage:
//   node tools/reconcile-training-links.mjs --live=a1-hallucination,d2-privacy,... [--write]

import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const APP = 'https://app.airiskpractice.org';
const args = process.argv.slice(2);
const write = args.includes('--write');
const liveArg = args.find((a) => a.startsWith('--live='));
if (!liveArg) {
  console.error('ERROR: pass --live=<comma-separated live scenario ids> from the app repo.');
  process.exit(1);
}
const LIVE = new Set(liveArg.slice('--live='.length).split(',').map((s) => s.trim()).filter(Boolean));

const DOCS = join(process.cwd(), 'docs');
const APP_RE = APP.replace(/[.]/g, '\\.');

// [label](/#/scenario/<id>) usually wrapped in ** with a bold-close and a
// " — <descriptor>." after it. Capture optional leading **, optional trailing
// **, and the optional descriptor (which carries the stale persona text). The
// em-dash is literal U+2014.
const DEEP = new RegExp(
  String.raw`(\*\*)?\[([^\]]*?)\]\(${APP_RE}/#/scenario/([a-z0-9-]+)\)(\*\*)?` +
  String.raw`(\s+\u2014\s+[^\n]*?\.)?`,
  'g'
);
const EVERYDAY = new RegExp(
  String.raw`\[([^\]]*?)\]\((?:${APP_RE})?/#/everyday\)`,
  'g'
);

function cleanDescriptor(descriptor) {
  if (!descriptor) return '';
  const body = descriptor.replace(/^\s+\u2014\s+/, '').replace(/\.\s*$/, '');
  const title = body.split(',')[0].trim();
  return title ? ` \u2014 ${title}.` : '';
}

function walk(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else if (/\.mdx?$/.test(name)) out.push(p);
  }
  return out;
}

const summary = { live: 0, pending: 0, everyday: 0, filesChanged: 0 };
const report = [];

for (const file of walk(DOCS)) {
  let src = readFileSync(file, 'utf8');
  const before = src;
  const rel = file.replace(process.cwd() + '/', '');

  src = src.replace(DEEP, (m, boldOpen, label, id, boldClose, descriptor) => {
    const desc = cleanDescriptor(descriptor);
    if (LIVE.has(id)) {
      summary.live++;
      report.push(`  LIVE     ${id.padEnd(28)} ${rel}`);
      return `**[▶ Play this scenario](${APP}/#/scenario/${id})**${desc}`;
    }
    summary.pending++;
    report.push(`  PENDING  ${id.padEnd(28)} ${rel}`);
    // Keep the URL (soft-landing handles known ids) but don't promise play.
    return `**[▶ Interactive scenario — coming soon](${APP}/#/scenario/${id})**${desc}`;
  });

  src = src.replace(EVERYDAY, (m, label) => {
    summary.everyday++;
    report.push(`  EVERYDAY ${'(/#/everyday)'.padEnd(28)} ${rel}`);
    return `[${label}](${APP}/)`;
  });

  if (src !== before) {
    summary.filesChanged++;
    if (write) writeFileSync(file, src);
  }
}

console.log(report.sort().join('\n'));
console.log('\n─────────────────────────────────────────────');
console.log(`LIVE deep links kept + de-personad : ${summary.live}`);
console.log(`PENDING deep links → coming-soon   : ${summary.pending}`);
console.log(`/#/everyday inline → app home '/'  : ${summary.everyday}`);
console.log(`files ${write ? 'written' : 'that WOULD change'}       : ${summary.filesChanged}`);
console.log(write ? '\nAPPLIED.' : '\nDRY RUN — re-run with --write to apply.');
