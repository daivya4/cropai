# Agents Workspace

This repository is a reusable workspace for AI agent instructions, persistent project memory, and workflow templates. It is intentionally lightweight: instead of containing a product codebase, it provides a structured operating environment that future sessions can reuse across many different projects.

The main goal is consistency. Each session should be able to recover context quickly, make small and verifiable changes, and preserve durable knowledge in a predictable place.

## What This Repository Contains

The repository is organized around three layers:

1. Repository-level instructions that define how the agent should behave.
2. Persistent memory under `.agent/memory/` that stores project knowledge over time.
3. Reusable workflow and template files under `.agent/workflows/` and `.agent/templates/`.

Together, these files let the workspace act like a memory-backed operating system for future agent sessions.

## Core Ideas

### Persistent Memory

The memory folder is where durable project knowledge lives. It is meant to be concise, factual, and useful for later sessions that need to resume work without rescanning the entire repository.

The standard memory files are:

- `overview.md` for the project summary
- `architecture.md` for high-level structure and flow
- `index.md` for a semantic map of important features and files
- `current.md` for the current working state
- `decisions.md` for durable architectural or workflow decisions
- `roadmap.md` for completed, in-progress, and planned work
- `known_issues.md` for visible issues, TODOs, and warnings
- `sessions/` for chronological session summaries

### Workflow Templates

The workflow files in `.agent/workflows/` define repeatable operating procedures for the agent.

- `initialize.md` describes how to build the initial memory set
- `start.md` describes how to resume from existing memory
- `checkpoint.md` describes how to save progress during a session
- `refresh.md` describes how to rebuild memory after meaningful repository changes
- `shutdown.md` describes how to close a session and update the affected memory files
- `review.md` describes how to inspect work for correctness and consistency

### Reusable Memory Templates

The template files in `.agent/templates/` define the expected structure for future memory files. They are generic and do not assume any specific project type.

- `overview.md`
- `architecture.md`
- `current.md`
- `decision.md`
- `session.md`

## How the Agent Should Use This Repository

The intended workflow is simple:

1. Read the repository instructions first.
2. Load the persistent memory files in the defined order.
3. Consult the semantic index before searching broadly.
4. Make the smallest change that solves the task.
5. Update only the memory files that changed in meaning.
6. Preserve historical session notes rather than rewriting them.

This approach keeps the workspace efficient and prevents the agent from repeatedly rediscovering the same context.

## Memory Update Principles

The persistent memory should stay high signal. Use it to store facts that are stable enough to help future sessions, not raw notes or full source copies.

Good memory content includes:

- Repository purpose
- Important architecture decisions
- Major folders and file responsibilities
- Current working state
- Durable blockers or known issues
- Verified session outcomes

Avoid putting these into memory:

- Long code snippets
- Unverified guesses
- Temporary debug notes
- Full directory trees
- Redundant copy-paste from source files

## Repository Layout

The current top-level structure is intentionally small:

- `.agent/` contains instructions, memory, workflows, templates, and repository-specific support files
- `AGENT.md` contains permanent operating rules for the agent in this workspace
- `PROMPT.md` contains the repository initialization guidance and memory system expectations
- `README.md` provides this overview for humans and agents alike

Inside `.agent/`, the main subdirectories are:

- `.agent/memory/` for durable project knowledge
- `.agent/workflows/` for agent lifecycle procedures
- `.agent/templates/` for reusable memory file structures

## Recommended Session Flow

For a new or returning session, the intended flow is:

1. Start by reading the repository instructions.
2. Load the memory files in order.
3. Use the index to find the relevant feature or area.
4. Inspect only the minimum additional files needed for the task.
5. Make the change.
6. Validate the result.
7. Save the session state in memory.

This sequence is designed to keep work grounded and avoid unnecessary repository scanning.

## Maintaining The Workspace

If you extend this repository, keep the following in mind:

- Update memory only when the repository meaningfully changes.
- Keep the workflow files generic so they remain useful across projects.
- Preserve the distinction between memory, templates, and live source files.
- Prefer small, deliberate edits over broad rewrites.

## Notes For Future Projects

This workspace is meant to be copied or adapted for other software projects. The memory files should be repopulated from the new repository’s evidence, while the workflow and template files can usually be reused as-is.

If the repository is used as a starter kit for other projects, the first thing to update should be the memory set, followed by any workflow refinements needed for that new codebase.