#!/usr/bin/env node
// build-llms.mjs — writes build/llms.txt after `docusaurus build`.
//
// A plain map of the library for AI tools, generated from entry front matter
// so it can't drift from the docs. Cheap bet with weak evidence (5 Oct): no
// major engine has confirmed using llms.txt, but it costs nothing.

import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const SITE = 'https://library.airiskpractice.org';
const DOCS = join(process.cwd(), 'docs');
const BUILD = join(process.cwd(), 'build');

if (!existsSync(BUILD)) {
  console.error('build/ not found — run `docusaurus build` first.');
  process.exit(1);
}

const field = (front, key) => {
  const m = front.match(new RegExp(`^${key}:\\s*"?(.*?)"?\\s*$`, 'm'));
  return m ? m[1] : '';
};

const entries = [];
for (const folder of readdirSync(DOCS).filter((d) => d.startsWith('domain-')).sort()) {
  for (const file of readdirSync(join(DOCS, folder)).filter((f) => /\.mdx?$/.test(f)).sort()) {
    const src = readFileSync(join(DOCS, folder, file), 'utf8');
    const front = (src.match(/^---\n([\s\S]*?)\n---/) || [])[1];
    if (!front) continue;
    const id = field(front, 'id');
    const title = field(front, 'title');
    const description = field(front, 'description');
    if (!id || !title) continue;
    entries.push(`- [${title}](${SITE}/docs/${folder}/${id}): ${description}`);
  }
}

if (entries.length === 0) {
  console.error('build-llms: no entries found in docs/domain-*. Refusing to write an empty llms.txt.');
  process.exit(1);
}

const txt = `# AI Risk Practice Library

> A free, open reference of AI risks, each with plain-language explanation, controls with owners and done criteria, and mappings to the EU AI Act, NIST AI RMF, ISO 42001 and OWASP. Content CC BY 4.0. Practice scenarios that pair with these entries are at https://app.airiskpractice.org/scenarios/

## Entries

${entries.join('\n')}

## Also

- [How to use the library](${SITE}/docs/how-to-use)
- [About](${SITE}/docs/about)
- [Practice scenarios](https://app.airiskpractice.org/scenarios/)
`;

writeFileSync(join(BUILD, 'llms.txt'), txt);
console.log(`llms.txt written (${entries.length} entries).`);
