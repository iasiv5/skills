// version-gate-core.mjs — pure gate logic, no side effects (imports nothing).
// The CLI wrapper (version-gate.mjs) reads real inputs and calls checkGate;
// tests inject fixture inputs. Keep this file free of process/fs/network.
export function parseSemver(text) {
  const match = /^(\d+)\.(\d+)\.(\d+)$/.exec(String(text).trim());
  if (!match) throw new Error(`not a plain semver: ${text}`);
  return { major: Number(match[1]), minor: Number(match[2]), patch: Number(match[3]), text: String(text).trim() };
}

export function newer(a, b) {
  if (a.major !== b.major) return a.major > b.major;
  if (a.minor !== b.minor) return a.minor > b.minor;
  return a.patch > b.patch;
}

/** Highest published version ≤ the releasing version (prerelease-ish entries filtered). */
export function previousReleaseOf(versions, version) {
  const plain = versions
    .filter((v) => /^\d+\.\d+\.\d+$/.test(v))
    .map(parseSemver)
    .filter((v) => !newer(v, version))
    .sort((a, b) => (newer(a, b) ? 1 : newer(b, a) ? -1 : 0));
  return plain.pop();
}

export function diffNames(currentNames, previousNames) {
  const added = [...currentNames].filter((n) => !previousNames.has(n));
  const removed = [...previousNames].filter((n) => !currentNames.has(n));
  return { added, removed };
}

/**
 * The gate. Returns { ok: true, notes } or { ok: false, reason, notes }.
 * - publishedVersions may be null: null = first release on npm.
 * - currentNames: Set of skill names in the about-to-release manifest.
 * - fetchPreviousNames(previousText): called when diffing; returns a Set of the
 *   previous release's skill names (tests inject fixtures, the CLI reads the tarball).
 */
export function checkGate({ tag, pkgVersion, currentNames, publishedVersions, fetchPreviousNames }) {
  const notes = [];
  const fail = (reason) => ({ ok: false, reason, notes });
  const note = (line) => notes.push(line);

  const version = parseSemver(pkgVersion);
  if (String(tag).replace(/^v/, "") !== version.text) {
    return fail(`git tag (${String(tag).replace(/^v/, "")}) != package.json version (${version.text})`);
  }
  note(`tag == package version == ${version.text}`);

  if (!currentNames || currentNames.size === 0) {
    return fail("skills-manifest.json missing/empty — run the build first");
  }

  if (publishedVersions === null || publishedVersions.length === 0) {
    if (version.text !== "1.0.0") {
      return fail(`first release must be 1.0.0 (got ${version.text})`);
    }
    note("first release on npm — no previous manifest to diff; 1.0.0 asserted");
    return { ok: true, notes };
  }

  const previous = previousReleaseOf(publishedVersions, version);
  if (!previous) {
    return fail(`no previous version <= ${version.text} found on npm (${publishedVersions.join(", ")})`);
  }
  note(`previous release ${previous.text}; diffing manifests`);

  if (typeof fetchPreviousNames !== "function") {
    return fail("fetchPreviousNames callback required for diffing releases");
  }
  const previousNames = fetchPreviousNames(previous.text);
  if (!(previousNames instanceof Set)) {
    return fail("fetchPreviousNames must return a Set of skill names");
  }

  const { added, removed } = diffNames(currentNames, previousNames);
  note(`manifest diff — added: ${added.length} [${added.join(", ")}]; removed: ${removed.length} [${removed.join(", ")}]`);

  if (removed.length > 0) {
    if (!(version.major > previous.major)) {
      return fail(`skill(s) removed/renamed → major bump required (prev ${previous.text} → got ${version.text})`);
    }
  } else if (added.length > 0) {
    if (!(version.major > previous.major || (version.major === previous.major && version.minor > previous.minor))) {
      return fail(`skill(s) added → minor bump required (prev ${previous.text} → got ${version.text})`);
    }
  } else if (!newer(version, previous)) {
    return fail(`version must be strictly greater than the published ${previous.text}`);
  }
  note(`semver satisfies manifest diff (prev ${previous.text} → ${version.text})`);
  return { ok: true, notes };
}
