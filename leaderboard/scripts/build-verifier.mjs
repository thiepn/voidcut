import fs from 'node:fs';
import path from 'node:path';
import { parse } from 'acorn';
import acornGlobals from 'acorn-globals';

const input = path.resolve(process.argv[2] || '../index.html');
const output = path.resolve('src/generated-verifier.js');
const html = fs.readFileSync(input, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
if (!scripts.length) throw new Error('No inline script found in VOIDCUT index.html');
const source = scripts.sort((a, b) => b.length - a.length)[0];
const program = parse(source, { ecmaVersion: 'latest', sourceType: 'script' });
const iife = program.body.find(node =>
  node.type === 'ExpressionStatement' &&
  node.expression?.type === 'CallExpression' &&
  ['ArrowFunctionExpression', 'FunctionExpression'].includes(node.expression?.callee?.type) &&
  node.expression.callee.body?.type === 'BlockStatement'
);
if (!iife) throw new Error('VOIDCUT runtime IIFE not found');
const body = iife.expression.callee.body.body;

const nodes = [];
const declByName = new Map();
function namesFromPattern(pattern, out = []) {
  if (!pattern) return out;
  if (pattern.type === 'Identifier') out.push(pattern.name);
  else if (pattern.type === 'ObjectPattern') for (const p of pattern.properties) namesFromPattern(p.value || p.argument, out);
  else if (pattern.type === 'ArrayPattern') for (const p of pattern.elements) namesFromPattern(p, out);
  else if (pattern.type === 'RestElement') namesFromPattern(pattern.argument, out);
  else if (pattern.type === 'AssignmentPattern') namesFromPattern(pattern.left, out);
  return out;
}
for (const node of body) {
  let names = [];
  if (node.type === 'FunctionDeclaration' || node.type === 'ClassDeclaration') {
    if (node.id?.name) names = [node.id.name];
  } else if (node.type === 'VariableDeclaration') {
    for (const d of node.declarations) names.push(...namesFromPattern(d.id));
  } else continue;
  const entry = { node, names, source: source.slice(node.start, node.end) };
  nodes.push(entry);
  for (const name of names) declByName.set(name, entry);
}

const roots = ['analyzeReplayData'];
for (const root of roots) if (!declByName.has(root)) throw new Error(`Verifier root missing: ${root}`);
const selected = new Set();
const queue = [...roots];
while (queue.length) {
  const name = queue.pop();
  const entry = declByName.get(name);
  if (!entry || selected.has(entry)) continue;
  selected.add(entry);
  const ast = parse(entry.source, { ecmaVersion: 'latest', sourceType: 'script' });
  for (const ref of acornGlobals(ast)) {
    if (declByName.has(ref.name)) queue.push(ref.name);
  }
}

const ordered = [...selected].sort((a, b) => a.node.start - b.node.start);
const generated = `// GENERATED FILE. DO NOT EDIT.\n// Extracted from VOIDCUT index.html so server verification uses the exact game simulation.\n\n${ordered.map(x => x.source).join('\n\n')}\n\nconst VC_GRADE_ORDER={D:0,C:1,B:2,A:3,S:4,'S+':5};\nexport function verifyReplay(replay){\n  if(!replay||replay.version!==9||(replay.arenaGeneration||2)!==2||(replay.directorGeneration||6)!==6)return null;\n  const analysis=analyzeReplayData(replay);\n  if(!analysis?.verified)return null;\n  let bestGrade=null;\n  for(const cut of analysis.cuts||[]){\n    const g=cut?.grade;\n    if(g&&(!bestGrade||(VC_GRADE_ORDER[g]??-1)>(VC_GRADE_ORDER[bestGrade]??-1)))bestGrade=g;\n  }\n  return Object.freeze({score:replay.score,chamber:replay.chamber,deathTime:replay.deathTime,hash:replay.hash,cuts:(analysis.cuts||[]).length,bestGrade});\n}\n`;
const forbidden = [/\bdocument\b/, /\bwindow\b/, /\blocalStorage\b/, /\bnavigator\b/, /\bcanvas\b/, /\bgetContext\b/];
for (const re of forbidden) if (re.test(generated)) throw new Error(`Generated verifier unexpectedly depends on browser API: ${re}`);
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, generated);
console.log(`Generated verifier with ${ordered.length} top-level declarations (${generated.length.toLocaleString()} bytes).`);
