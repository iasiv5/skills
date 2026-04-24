# Intent Confidence

- Confidence score: `30/100`
- Confidence band: `low`
- Gate passed: `False`
- Recommended action: Pause before deep authoring and close the highest-leverage gaps first.

## Current Reading

Create, refactor, evaluate, and package agent skills from workflows, prompts, transcripts, docs, or notes. Use when asked to create a skill, turn a repeated process into a reusable skill, improve an existing skill, add evals, or package a skill for team reuse.

## Strong Signals

- The recurring job is concrete enough to anchor the package.

## Gaps To Close

- **Real inputs are missing** (`high`): Without real inputs, it is hard to choose assets, scripts, or examples.
- **Primary output is missing** (`high`): The package does not yet know what it must hand back.
- **Near-neighbor exclusions are missing** (`high`): The route may blur into nearby requests without an exclusion list.
- **Constraints are missing** (`high`): The package does not yet know which tradeoffs matter most.
- **Quality bar is implied, not explicit** (`medium`): The first evaluation target is still underspecified.

## Follow-Up Questions

- **What material will people actually hand to this skill in practice?**
  - Why: Real input shape decides whether references, scripts, or examples are needed.
- **What finished hand-back should this skill return so the next person can keep moving?**
  - Why: The output is the anchor for package design and review.
- **What nearby requests should this skill clearly leave out so the boundary stays clean?**
  - Why: Exclusions are the fastest route to better trigger quality.
