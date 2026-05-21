# Prompt Quality Profile

Skill: `yao-meta-skill`
Relevance: `prompt-heavy`
Overall quality score: `82.0/100`

## Primary Task Family

**Dialogue interaction**
- Matched keywords: dialogue, conversation

## Complexity

- Band: `complex`
- Score: `6`
- Reason: multiple inputs, constraints, or task families require tradeoff handling

## Need Model

- Explicit Need: Create, refactor, evaluate, and package agent skills from workflows, prompts, transcripts, docs, or notes. Use when asked to create a skill, turn a repeated process into a reusable skill, improve an existing skill, add evals, or package a skill for team reuse.
- Implicit Need: The reusable skill needs a stable role, task, and output contract rather than a one-off prompt.
- Scenario: not yet explicit
- User Level: infer from examples and standards; ask only if it changes output depth
- Success Standard: usable output with clear validation cues

## RTF To Skill Mapping

- Role: Use a conversational role that asks only high-leverage questions and remembers the user's goal.
- Task: Clarify intent, resolve uncertainty, and converge toward a recommendation instead of a long option list.
- Format: Return concise prompts, decision points, and reviewer-visible assumptions.

## Quality Matrix

### Completeness — 80/100
- Matched signals: output, constraint, standard
- Repair: Name missing inputs, outputs, constraints, or success standards before deepening the package.

### Clarity — 80/100
- Matched signals: none
- Repair: Replace broad verbs with observable actions and define what done means.

### Consistency — 90/100
- Matched signals: aligned, boundary
- Repair: Check that role, task, format, exclusions, and examples do not contradict each other.

### Practicality — 90/100
- Matched signals: use, workflow
- Repair: Add runnable steps, examples, or verification cues instead of abstract advice.

### Specificity — 70/100
- Matched signals: none
- Repair: Anchor wording in the user's audience, domain nouns, and target outcome.

## Matched Task Families

### Dialogue interaction
- Score: `2`
- Keywords: dialogue, conversation
- Role: Use a conversational role that asks only high-leverage questions and remembers the user's goal.
- Task: Clarify intent, resolve uncertainty, and converge toward a recommendation instead of a long option list.
- Format: Return concise prompts, decision points, and reviewer-visible assumptions.

### Execution operation
- Score: `1`
- Keywords: workflow
- Role: Use an operator role with explicit boundaries, inputs, outputs, and failure handling.
- Task: Convert the job into ordered steps with validation checks and stop conditions.
- Format: Return a runbook-like handoff with commands, checks, owners, and next actions when relevant.

### Teaching guidance
- Score: `1`
- Keywords: teach
- Role: Use a teacher role that adapts to learner level and avoids overloading the first pass.
- Task: Explain through progressive steps, examples, and visible success checks.
- Format: Return learner-facing sections, worked examples, checkpoints, and common mistakes.

### Prompt engineering
- Score: `1`
- Keywords: prompt
- Role: Use a prompt engineer role only when role design materially improves execution.
- Task: Map Role, Task, and Format into skill behavior rather than copying a large prompt template.
- Format: Return a compact prompt contract plus tests, quality matrix, and usage notes.

## Self-Repair Checks

- Check explicit need, implicit need, scenario, user level, and success standard before deepening.
- Map Role, Task, and Format into skill behavior, not decorative prompt labels.
- Ask one focused clarification only when missing information changes the package boundary.
- Add tests or examples for prompt-heavy behavior before treating it as reusable.
- Keep prompt methodology in references and reports instead of bloating SKILL.md.

## Reviewer Note

Use this profile when the package depends on prompt behavior, role design, output contracts, or conversation quality.
