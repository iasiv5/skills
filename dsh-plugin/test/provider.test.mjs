import assert from "node:assert/strict";
import { test } from "node:test";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { apply, inject, name } from "../lib/index.js";

const fixturesDir = join(dirname(fileURLToPath(import.meta.url)), "fixtures");

function fakeCtx() {
  const captured = { providers: [] };
  return {
    ctx: {
      skills: {
        registerProvider(factory) {
          captured.providers.push(factory());
        }
      }
    },
    captured
  };
}

test("plugin identity exports", () => {
  assert.equal(name, "iasi-skills");
  assert.deepEqual(inject, ["skills"]);
});

test("apply registers exactly one provider named after the package", () => {
  const { ctx, captured } = fakeCtx();
  apply(ctx, { manifestDir: fixturesDir });
  assert.equal(captured.providers.length, 1);
  assert.equal(captured.providers[0].name, "@iasiv5/dsh-skills");
});

test("list() returns manifest candidates with invocation passed through verbatim", async () => {
  const { ctx, captured } = fakeCtx();
  apply(ctx, { manifestDir: fixturesDir });
  const provider = captured.providers[0];
  const candidates = await provider.list();
  assert.equal(candidates.length, 2);

  const byName = new Map(candidates.map((c) => [c.name, c]));
  const normal = byName.get("demo-skill");
  const slashOnly = byName.get("demo-slash-only");
  assert.ok(normal && slashOnly, "both fixture skills present");

  // shared candidate shape
  for (const c of candidates) {
    assert.equal(c.provider, "@iasiv5/dsh-skills");
    assert.equal(c.source, "bundled");
    assert.equal(c.rank, 600);
    assert.match(c.path, /SKILL\.md$/);
    assert.equal(c.resourceBase.kind, "directory");
    assert.equal(c.resourceBase.path, dirname(c.path));
  }

  // invocation passthrough, not hardcoded
  assert.deepEqual(normal.invocation, { modelInvocable: true, userInvocable: true });
  assert.deepEqual(slashOnly.invocation, { modelInvocable: false, userInvocable: true });

  // paths resolve inside the manifestDir base (fixture), not packageRoot
  assert.ok(normal.path.startsWith(fixturesDir), `candidate path under fixture dir: ${normal.path}`);
});

test("get() strips frontmatter and returns full summary + content", async () => {
  const { ctx, captured } = fakeCtx();
  apply(ctx, { manifestDir: fixturesDir });
  const provider = captured.providers[0];
  const [candidate] = (await provider.list()).filter((c) => c.name === "demo-skill");
  const skill = await provider.get(candidate);
  assert.equal(skill.name, "demo-skill");
  assert.equal(skill.description, "Demo skill for provider tests.");
  assert.deepEqual(skill.invocation, { modelInvocable: true, userInvocable: true });
  assert.equal(skill.provider, "@iasiv5/dsh-skills");
  assert.equal(skill.source, "bundled");
  assert.equal(skill.rank, undefined, "rank is a catalog field, not part of the loaded skill");
  assert.ok(skill.content.includes("This is the demo body text."), "body preserved");
  assert.ok(!skill.content.startsWith("---"), "frontmatter stripped");
  assert.ok(!skill.content.includes("description:"), "frontmatter keys stripped");
});

test("apply throws immediately when the manifest is missing (fail-fast at activation)", () => {
  const { ctx } = fakeCtx();
  assert.throws(
    () => apply(ctx, { manifestDir: join(fixturesDir, "no-such-dir") }),
    /skills-manifest\.json/
  );
});
