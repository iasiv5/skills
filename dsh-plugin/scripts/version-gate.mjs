#!/usr/bin/env node
// version-gate.mjs — release gate CLI. Pure logic lives in version-gate-core.mjs
// (unit-tested); this wrapper reads the real inputs and reports.
// Checks: tag == package version; semver-by-manifest against the previous npm
// release (added skill → minor; removed/renamed → major; content-only → patch);
// first release passes only at exactly 1.0.0.
// Usage: node scripts/version-gate.mjs <tag-name>   (e.g. v1.0.0)
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { checkGate } from "./version-gate-core.mjs";

const pluginRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const REGISTRY = "https://registry.npmjs.org";
const PKG = "@iasiv5/dsh-skills";

function die(message) {
  console.error(`version-gate: ${message}`);
  process.exit(1);
}

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

function readPreviousNames(previousText) {
  const tmp = mkdtempSync(join(tmpdir(), "version-gate-"));
  try {
    execFileSync("npm", ["pack", `${PKG}@${previousText}`, "--pack-destination", tmp, `--registry=${REGISTRY}`], {
      stdio: ["ignore", "ignore", "pipe"]
    });
    const tgzName = `${PKG.replace("@", "").replace("/", "-")}-${previousText}.tgz`;
    const manifestText = execFileSync("tar", ["-xOzf", join(tmp, tgzName), "package/skills-manifest.json"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"]
    });
    return new Set(JSON.parse(manifestText).skills.map((s) => s.name));
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

const tag = (process.argv[2] ?? process.env.GITHUB_REF_NAME ?? "").replace(/^v/, "");
if (!tag) die("tag name missing (pass as argv[1] or GITHUB_REF_NAME)");

const pkgVersion = JSON.parse(readFileSync(join(pluginRoot, "package.json"), "utf8")).version;

let currentNames;
try {
  const manifest = JSON.parse(readFileSync(join(pluginRoot, "skills-manifest.json"), "utf8"));
  currentNames = new Set(manifest.skills.map((s) => s.name));
} catch {
  die("skills-manifest.json missing/unreadable — run the build first");
}

const result = checkGate({
  tag,
  pkgVersion,
  currentNames,
  publishedVersions: spawnView(),
  fetchPreviousNames: (previousText) => readPreviousNames(previousText)
});

for (const line of result.notes) console.log(`gate: ${line}`);
if (!result.ok) die(result.reason);
