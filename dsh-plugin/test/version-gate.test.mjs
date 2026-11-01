import assert from "node:assert/strict";
import { test } from "node:test";
import { checkGate, previousReleaseOf } from "../scripts/version-gate-core.mjs";

const prev = new Set(["a"]);

function base(overrides = {}) {
  return {
    currentNames: new Set(["a"]),
    pkgVersion: "1.0.0",
    tag: "v1.0.0",
    publishedVersions: null,
    fetchPreviousNames: () => prev,
    ...overrides
  };
}

test("first release passes only at 1.0.0", () => {
  const r = checkGate(base());
  assert.equal(r.ok, true);
  const bad = checkGate(base({ pkgVersion: "1.0.1", tag: "v1.0.1" }));
  assert.equal(bad.ok, false);
  assert.match(bad.reason, /first release must be 1\.0\.0/);
});

test("tag != package version fails", () => {
  const r = checkGate(base({ tag: "v0.9.0" }));
  assert.equal(r.ok, false);
  assert.match(r.reason, /!= package\.json version/);
});

test("empty manifest fails", () => {
  const r = checkGate(base({ currentNames: new Set() }));
  assert.equal(r.ok, false);
  assert.match(r.reason, /missing\/empty/);
});

test("added skills require a minor bump", () => {
  const cur = new Set(["a", "b"]);
  const ok = checkGate(base({ tag: "v1.1.0", pkgVersion: "1.1.0", currentNames: cur, publishedVersions: ["1.0.0"] }));
  assert.equal(ok.ok, true);
  const bad = checkGate(base({ tag: "v1.0.1", pkgVersion: "1.0.1", currentNames: cur, publishedVersions: ["1.0.0"] }));
  assert.equal(bad.ok, false);
  assert.match(bad.reason, /minor bump required/);
});

test("removed skills require a major bump", () => {
  const cur = new Set(["a"]);
  const fixture = () => new Set(["a", "b"]);
  const ok = checkGate(base({ tag: "v2.0.0", pkgVersion: "2.0.0", currentNames: cur, publishedVersions: ["1.0.0"], fetchPreviousNames: fixture }));
  assert.equal(ok.ok, true);
  const bad = checkGate(base({ tag: "v1.1.0", pkgVersion: "1.1.0", currentNames: cur, publishedVersions: ["1.0.0"], fetchPreviousNames: fixture }));
  assert.equal(bad.ok, false);
  assert.match(bad.reason, /major bump required/);
});

test("content-only change requires strictly greater version", () => {
  const ok = checkGate(base({ tag: "v1.0.1", pkgVersion: "1.0.1", publishedVersions: ["1.0.0"] }));
  assert.equal(ok.ok, true);
  const bad = checkGate(base({ tag: "v1.0.0", pkgVersion: "1.0.0", publishedVersions: ["1.0.0"] }));
  assert.equal(bad.ok, false);
  assert.match(bad.reason, /strictly greater/);
});

test("missing fetchPreviousNames fails loudly on diffing releases", () => {
  const b = base({ tag: "v1.0.1", pkgVersion: "1.0.1", publishedVersions: ["1.0.0"] });
  delete b.fetchPreviousNames;
  const r = checkGate(b);
  assert.equal(r.ok, false);
  assert.match(r.reason, /fetchPreviousNames/);
});

test("previousReleaseOf picks highest ≤ version and filters prerelease-ish entries", () => {
  const version = { major: 1, minor: 0, patch: 1, text: "1.0.1" };
  const prev = previousReleaseOf(["0.0.0-stage", "0.0.1", "1.0.0"], version);
  assert.equal(prev.text, "1.0.0");
  assert.equal(previousReleaseOf(["0.0.0-stage"], version), undefined);
});

test("gate tolerates the 0.0.0-stage placeholder entry", () => {
  const r = checkGate(base({
    tag: "v1.0.1",
    pkgVersion: "1.0.1",
    publishedVersions: ["0.0.0-stage", "0.0.1"]
  }));
  assert.equal(r.ok, true);
});
