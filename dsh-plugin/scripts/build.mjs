#!/usr/bin/env node
// build.mjs — stage skills/, generate skills-manifest.json, run gates, report size.
// Modes: default = stage + manifest + gates + pack report; --check = gates +
// staged-sync verification only (no writes).
import { createHash } from "node:crypto";
import { cp, readdir, readFile, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join, relative, resolve } from "node:path";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const pluginRoot = resolve(scriptDir, "..");
const repoRoot = resolve(pluginRoot, "..");
const stagedSkillsDir = join(pluginRoot, "skills");
const manifestPath = join(pluginRoot, "skills-manifest.json");
const checkMode = process.argv.includes("--check");

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/u;
const LEGACY_INVOCATION_KEYS = ["disableModelInvocation", "modelInvocable", "userInvocable"];
const BOOL_TRUE = new Set([true, 1, "1", "true", "yes", "on"]);
const BOOL_FALSE = new Set([false, 0, "0", "false", "no", "off"]);
const REF_PREFIX_RE = /^(?:scripts|assets|references|docs)\//;

// License-driven packaging exclusions (owner decisions D4/D5, 2026-11-01):
//   remotion-best-practices — upstream ships no content license
//     (remotion-dev/skills). Its remotion-license subskill (synced at upstream
//     4.0.541) documents the Remotion *software* license (remotion.pro), not a
//     license for the skills content, so the exclusion stands.
// docx / pdf / xlsx were excluded under the same policy until upstream
// (anthropics/skills) relicensed them to Apache-2.0 (LICENSE.txt replaced,
// 2026-11 sync; owner re-decision 2026-11-08): redistribution is now allowed,
// so they are packaged again.
// Audit record: ~/.dsh-research/dsh-skills-plan-review/license-audit-2026-11.md
const PACKAGING_EXCLUDE = new Set(["remotion-best-practices"]);

const errors = [];
function fail(message) {
  errors.push(message);
}

// --- discovery ---------------------------------------------------------------

async function discoverSkillDirs() {
  const entries = await readdir(repoRoot, { withFileTypes: true });
  const dirs = [];
  const excluded = [];
  for (const entry of entries) {
    if (entry.name.startsWith(".")) continue;
    if (!entry.isDirectory()) continue;
    if (!existsSync(join(repoRoot, entry.name, "SKILL.md"))) continue;
    if (PACKAGING_EXCLUDE.has(entry.name)) {
      excluded.push(entry.name);
      continue;
    }
    dirs.push(entry.name);
  }
  if (excluded.length > 0) console.log(`excluded from package (license policy): ${excluded.sort().join(", ")}`);
  return dirs.sort();
}

// --- gate 1: frontmatter validity + invocation policy ------------------------

function frontmatterBoolean(dirName, key, value) {
  if (value === undefined) return undefined;
  if (BOOL_TRUE.has(value)) return true;
  if (BOOL_FALSE.has(value)) return false;
  fail(`${dirName}: frontmatter field "${key}" must be a boolean (got ${JSON.stringify(value)})`);
  return undefined;
}

function parseFrontmatter(dirName, dirPath) {
  const skillMdPath = join(dirPath, "SKILL.md");
  const raw = readFile(skillMdPath, { encoding: "utf8" });
  return raw.then((text) => {
    const match = FRONTMATTER_RE.exec(text);
    if (match === null) {
      fail(`${dirName}: SKILL.md has no YAML frontmatter`);
      return { body: text, meta: null, invocation: { modelInvocable: true, userInvocable: true } };
    }
    let meta;
    try {
      meta = parseYaml(match[1]);
    } catch (error) {
      fail(`${dirName}: frontmatter YAML parse error: ${error.message}`);
      return { body: text.slice(match[0].length), meta: null, invocation: { modelInvocable: true, userInvocable: true } };
    }
    if (!meta || typeof meta !== "object") {
      fail(`${dirName}: frontmatter is not a mapping`);
      return { body: text.slice(match[0].length), meta: null, invocation: { modelInvocable: true, userInvocable: true } };
    }
    if (typeof meta.name !== "string" || meta.name.length === 0) fail(`${dirName}: frontmatter "name" missing/empty`);
    if (typeof meta.description !== "string" || meta.description.length === 0) fail(`${dirName}: frontmatter "description" missing/empty`);
    if (meta.whenToUse !== undefined && typeof meta.whenToUse !== "string") fail(`${dirName}: frontmatter "whenToUse" must be a string`);
    for (const legacy of LEGACY_INVOCATION_KEYS) {
      if (Object.hasOwn(meta, legacy)) fail(`${dirName}: legacy invocation key "${legacy}" is unsupported; use "disable-model-invocation" / "user-invocable"`);
    }
    const disableModel = frontmatterBoolean(dirName, "disable-model-invocation", meta["disable-model-invocation"]);
    const userInvocable = frontmatterBoolean(dirName, "user-invocable", meta["user-invocable"]);
    const invocation = {
      modelInvocable: disableModel !== true,
      userInvocable: userInvocable !== false
    };
    return { body: text.slice(match[0].length), meta, invocation };
  });
}

// --- gate 2: unique frontmatter names ----------------------------------------

function checkUniqueNames(records) {
  const seen = new Map();
  for (const record of records) {
    if (record.meta?.name === undefined) continue;
    const owner = seen.get(record.meta.name);
    if (owner !== undefined) fail(`duplicate skill name "${record.meta.name}" in "${owner}" and "${record.dir}"`);
    else seen.set(record.meta.name, record.dir);
  }
}

// --- gate 3: reference integrity (against the staged set = skill dirs) -------
// Severity semantics (as-is packaging, errata C):
//   FAIL  — target exists in the repo but outside the staged skill dirs
//           (packaging divergence: worked in the old full-repo layout, breaks in the package);
//           or reference escapes the repository via ../ while its target exists in the repo.
//   WARN  — target missing from source entirely (pre-existing upstream dangling ref,
//           carried as-is) or unresolvable/placeholder-looking references.

function collectReferences(dirName, body) {
  const refs = new Set();
  const linkRe = /\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;
  const backtickRe = /`((?:scripts|assets|references|docs)\/[A-Za-z0-9][A-Za-z0-9._/-]*)`/g;
  for (const match of body.matchAll(linkRe)) refs.add(match[1]);
  for (const match of body.matchAll(backtickRe)) refs.add(match[1]);
  return [...refs].filter((ref) => {
    if (/^(https?:|mailto:|data:|file:)/i.test(ref)) return false;
    if (ref.startsWith("#")) return false;
    if (ref.includes("<") || ref.includes(">")) return false; // documentation placeholders like </abs/path.html>
    if (ref.startsWith("/")) return false; // absolute paths are host-specific examples
    if (ref.includes("*")) return false; // globs are patterns, not files
    return !ref.startsWith("{{");
  });
}

function checkReferences(dirName, dirPath, body, stagedDirs) {
  let warnings = 0;
  for (const ref of collectReferences(dirName, body)) {
    let clean = ref.split("#")[0].split("?")[0];
    if (clean.length === 0) continue;
    clean = clean.replace(/^\.\//, "").replace(/[,.;:]+$/, "");
    if (clean.length === 0) continue;
    const target = resolve(dirPath, clean);
    const rel = relative(repoRoot, target);
    const escapesRepo = rel.startsWith("..");
    if (escapesRepo) {
      if (existsSync(target)) {
        fail(`${dirName}: reference "${ref}" escapes the repository but its target exists at ${rel} — packaging would break it`);
      } else {
        warnings += 1;
        console.warn(`warn: ${dirName}: reference "${ref}" unresolvable (escapes repo; carried as-is)`);
      }
      continue;
    }
    const insideStaged = stagedDirs.some((d) => rel === d || rel.startsWith(`${d}/`));
    if (!insideStaged) {
      if (existsSync(target)) {
        fail(`${dirName}: reference "${ref}" exists in the repo but outside the packaged skill directories (target: ${rel}) — packaging would break it`);
      } else {
        warnings += 1;
        console.warn(`warn: ${dirName}: reference "${ref}" points outside the packaged dirs and is missing there too (carried as-is)`);
      }
      continue;
    }
    if (!existsSync(target)) {
      warnings += 1;
      console.warn(`warn: ${dirName}: reference "${ref}" target missing (pre-existing dangling ref, carried as-is): ${rel}`);
    }
  }
  return warnings;
}

// --- staging + manifest ------------------------------------------------------

async function stageSkillDir(dirName) {
  const source = join(repoRoot, dirName);
  const target = join(stagedSkillsDir, dirName);
  await rm(target, { recursive: true, force: true });
  await cp(source, target, { recursive: true });
}

function computeManifest(records) {
  const skills = records
    .slice()
    .sort((a, b) => a.dir.localeCompare(b.dir))
    .map((record) => ({
      dir: record.dir,
      name: record.meta.name,
      description: record.meta.description,
      ...(record.meta.whenToUse !== undefined ? { whenToUse: record.meta.whenToUse } : {}),
      invocation: record.invocation
    }));
  return { skills };
}

async function hashTree(root) {
  const map = new Map();
  async function walk(current, prefix) {
    for (const entry of await readdir(current, { withFileTypes: true })) {
      const child = join(current, entry.name);
      const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
      if (entry.isDirectory()) await walk(child, rel);
      else if (entry.isFile()) map.set(rel, createHash("sha256").update(await readFile(child)).digest("hex"));
    }
  }
  if (existsSync(root)) await walk(root, "");
  return map;
}

async function verifyStagedSync(records) {
  if (!existsSync(stagedSkillsDir)) {
    fail("--check: staged skills/ does not exist — run a full build first");
    return;
  }
  const sourceMaps = new Map();
  for (const record of records) sourceMaps.set(record.dir, await hashTree(join(repoRoot, record.dir)));
  const stagedDirs = (await readdir(stagedSkillsDir)).sort();
  const expectedDirs = records.map((r) => r.dir).sort();
  if (stagedDirs.join(",") !== expectedDirs.join(",")) {
    fail(`--check: staged dir set out of sync (staged: ${stagedDirs.join(", ") || "<empty>"}; expected: ${expectedDirs.join(", ")})`);
    return;
  }
  for (const record of records) {
    const stagedMap = await hashTree(join(stagedSkillsDir, record.dir));
    const sourceMap = sourceMaps.get(record.dir);
    for (const [file, hash] of sourceMap) {
      if (stagedMap.get(file) !== hash) fail(`--check: ${record.dir}/${file} differs between source and staged copy`);
    }
    for (const file of stagedMap.keys()) {
      if (!sourceMap.has(file)) fail(`--check: ${record.dir}/${file} exists only in staged copy`);
    }
  }
  if (!existsSync(manifestPath)) {
    fail("--check: skills-manifest.json missing");
    return;
  }
  const expected = computeManifest(records);
  const actual = await readFile(manifestPath, { encoding: "utf8" });
  if (actual.trim() !== JSON.stringify(expected, null, 2) + "\n") {
    fail("--check: skills-manifest.json out of sync with source frontmatter");
  }
}

// --- gate 4: pack report ------------------------------------------------------

function packReport() {
  const result = spawnSync("npm", ["pack", "--dry-run"], { cwd: pluginRoot, encoding: "utf8" });
  if (result.status !== 0) {
    fail(`npm pack --dry-run failed (exit ${result.status})`);
    if (result.stderr) process.stderr.write(result.stderr.split("\n").filter((l) => !l.startsWith("npm notice")).join("\n"));
    return;
  }
  const notices = (result.stderr ?? "").split("\n").filter((line) => line.startsWith("npm notice"));
  // Hard exclusion assertions (fail-closed): dev trees and test scaffolding must
  // never enter the tarball, regardless of the files whitelist.
  for (const line of notices) {
    if (/npm notice (node_modules\/|test\/|scripts\/|\.github\/)/.test(line)) {
      fail(`pack listing contains forbidden path: ${line.trim()}`);
    }
  }
  const interesting = notices.filter((line) => /Tarball Details|package size|total files|filename/i.test(line));
  console.log(interesting.join("\n"));
}

// --- main --------------------------------------------------------------------

const dirs = await discoverSkillDirs();
if (dirs.length === 0) {
  console.error(`build: 0 skill directories discovered under ${repoRoot} — nothing to do`);
  process.exit(1);
}

const records = [];
for (const dir of dirs) {
  const parsed = await parseFrontmatter(dir, join(repoRoot, dir));
  records.push({ dir, ...parsed });
}

checkUniqueNames(records);
let warningCount = 0;
for (const record of records) warningCount += checkReferences(record.dir, join(repoRoot, record.dir), record.body, dirs);

if (checkMode) {
  await verifyStagedSync(records);
} else {
  await rm(stagedSkillsDir, { recursive: true, force: true });
  for (const dir of dirs) await stageSkillDir(dir);
  const manifest = computeManifest(records);
  const { writeFile } = await import("node:fs/promises");
  await writeFile(manifestPath, JSON.stringify(manifest, null, 2) + "\n", { encoding: "utf8" });
  console.log(`${manifest.skills.length} skills staged`);
  packReport();
}

if (errors.length > 0) {
  console.error(`build: ${errors.length} gate failure(s):`);
  for (const error of errors) console.error(`  - ${error}`);
  process.exit(1);
}
if (checkMode) console.log("check passed: gates green, staged copy in sync");
if (warningCount > 0) console.log(`reference-integrity warnings (non-blocking, carried as-is): ${warningCount}`);
