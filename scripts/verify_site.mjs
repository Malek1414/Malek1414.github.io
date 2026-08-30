// Site invariants: every inline <script> parses; every referenced local asset exists.
import fs from 'node:fs';
const html = fs.readFileSync('index.html', 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (!scripts.length) { console.error('FAIL: no inline scripts found'); process.exit(1); }
for (const s of scripts) new Function(s); // parse only; throws SyntaxError on bad JS
const refs = new Set(
  [...html.matchAll(/['"](assets\/[^'"]+|output\/[^'"]+)['"]/g)].map(m => m[1])
);
let missing = 0;
for (const a of refs) if (!fs.existsSync(a)) { console.error('MISSING: ' + a); missing++; }
if (missing) process.exit(1);
console.log(`OK: JS parses, ${refs.size} referenced assets exist`);
