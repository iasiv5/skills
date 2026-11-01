#!/usr/bin/env node
// version-gate.mjs — release gate: tag == package version, plus semver-by-manifest
// against the previous npm release (added skill → minor; removed/renamed → major;
// content-only changes → patch). First release: no previous version on npm →
// pass, but only when the version is exactly 1.0.0 (plan Q6/Q9).
// Usage: node scripts/version-gate.mjs <tag-name>   (e.g. v1.0.0)
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const pluginRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const REGISTRY = "https://registry.npmjs.org";
const PKG = "@iasiv5/dsh-skills";

function die(message) {
  console.error(`version-gate: ${message}`);
  process.exit(1);
}

function parseSemver(text) {
  const match = /^(\d+)\.(\d+)\.(\d+)$/.exec(text.trim());
  if (!match) die(`not a plain semver: ${text}`);
  return { major: Number(match[1]), minor: Number(match[2]), patch: Number(match[3]), text: text.trim() };
}

function newer(a, b) {
  if (a.major !== b.major) return a.major > b.major;
  if (a.minor !== b.minor) return a.minor > b.minor;
  return a.patch > b.patch;
}

const tag = (process.argv[2] ?? process.env.GITHUB_REF_NAME ?? "").replace(/^v/, "");
if (!tag) die("tag name missing (pass as argv[1] or GITHUB_REF_NAME)");
const version = parseSemver(JSON.parse(readFileSync(join(pluginRoot, "package.json"), "utf8")).version);
if (tag !== version.text) die(`git tag (${tag}) != package.json version (${version.text})`);
console.log(`gate: tag == package version == ${version.text}`);

const currentManifest = JSON.parse(readFileSync(join(pluginRoot, "skills-manifest.json"), "utf8"));
if (!Array.isArray(currentManifest.skills) || currentManifest.skills.length === 0) {
  die("skills-manifest.json missing/empty — run the build first");
}
const currentNames = new Set(currentManifest.skills.map((s) => s.name));

const publishedVersions = spawnView();
function spawnView() {
  try {
    const out = execFileSync("npm", ["view", PKG, "versions", "--json", `--registry=${REGISTRY}`], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"]
    });
    return JSON.parse(out);
  } catch (error) {
    const stderr = String(error.stderr ?? "");
    if (/E404|code E404|404 Not Found/.test(stderr)) return null; // first release
    die(`npm view failed unexpectedly: ${stderr.split("\n")[0] || error.message}`);
  }
}

if (publishedVersions === null || publishedVersions.length === 0) {
  if (version.text !== "1.0.0") {
    die(`first release must be 1.0.0 (got ${version.text})`);
  }
  console.log("gate: first release on npm — no previous manifest to diff; 1.0.0 asserted");
  process.exit(0);
}

const previousText = publishedVersions
  .filter((v) => /^\d+\.\d+\.\d+$/.test(v))
  .map(parseSemver)
  .filter((v) => !newer(v, version))
  .sort((a, b) => (newer(a, b) ? 1 : newer(b, a) ? -1 : 0))
  .pop();
if (!previousText) die(`no previous version <= ${version.text} found on npm (${publishedVersions.join(", ")})`);
console.log(`gate: previous release ${previousText.text}; diffing manifests`);

const tmp = mkdtempSync(join(tmpdir(), "version-gate-"));
let previousNames;
try {
  const tgz = join(tmp, "prev.tgz");
  execFileSync("npm", ["pack", `${PKG}@${previousText.text}`, "--pack-destination", tmp, `--registry=${REGISTRY}`], {
    stdio: ["ignore", "ignore", "pipe"]
  });
  const tgzName = `${PKG.replace("@", "").replace("/", "-")}-${previousText.text}.tgz`;
  const manifestText = execFileSync("tar", ["-xOzf", join(tmp, tgzName), "package/skills-manifest.json"], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  });
  previousNames = new Set(JSON.parse(manifestText).skills.map((s) => s.name));
} finally {
  rmSync(tmp, { recursive: true, force: true });
}

const added = [...currentNames].filter((n) => !previousNames.has(n));
const removed = [...previousNames].filter((n) => !currentNames.has(n));
console.log(`gate: manifest diff — added: ${added.length} [${added.join(", ")}]; removed: ${removed.length} [${removed.join(", ")}]`);

if (removed.length > 0) {
  if (!(version.major > previousText.major)) {
    die(`skill(s) removed/renamed → major bump required (prev ${previousText.text} → got ${version.text})`);
  }
} else if (added.length > 0) {
  if (!(version.major > previousText.major || (version.major === previousText.major && version.minor > previousText.minor))) {
    die(`skill(s) added → minor bump required (prev ${previousText.text} → got ${version.text})`);
  }
} else if (!newer(version, previousText)) {
  die(`version must be strictly greater than the published ${previousText.text}`);
}
console.log(`gate: semver satisfies manifest diff (prev ${previousText.text} → ${version.text})`);
