Read `.agent/AGENT.md` completely before doing anything else.

Your task is to initialize this repository with a complete persistent memory system.

This is a one-time initialization.

## Goal

Build a project memory system that allows future AI sessions to understand this repository without repeatedly scanning the entire codebase.

The memory should become the primary source of project context.

Future sessions should only need to read the memory first and search the repository only when necessary.

------------------------------------------------------------

## Step 1

Analyze the repository completely.

Understand:

- Project purpose
- Architecture
- Technology stack
- Folder structure
- Main features
- Entry points
- Build system
- Important configuration
- APIs
- Database
- Packages
- Dependencies
- Coding conventions already present

Read whatever is required.

Do not make assumptions.

------------------------------------------------------------

## Step 2

Inside

.agent/memory

create the following files if they do not exist.

overview.md

architecture.md

index.md

current.md

decisions.md

roadmap.md

known_issues.md

------------------------------------------------------------

## overview.md

Describe

- project purpose
- overall goal
- major features
- technologies
- current maturity

Keep under 1 page.

------------------------------------------------------------

## architecture.md

Document

- overall architecture
- major modules
- communication
- important folders
- important entry points
- external services
- major dependencies

This file should only change after architectural changes.

------------------------------------------------------------

## index.md

This is the MOST IMPORTANT memory file.

Do NOT create a directory tree.

Instead create a semantic index.

For every important feature include:

Feature

Purpose

Important folders

Important files

Dependencies

Examples

Authentication

Purpose

Handles login and user sessions.

Folders

lib/features/auth/

Files

login_screen.dart
auth_service.dart

Future AI sessions should always read this file before searching the repository.

------------------------------------------------------------

## current.md

Initialize with

Current feature

Current branch

Completed work

Next recommended task

Known blockers

Recent progress

If information is unavailable, state that explicitly.

------------------------------------------------------------

## decisions.md

Summarize architectural decisions already present in the repository.

Examples

Chosen state management

Chosen database

Chosen backend

Chosen networking library

Folder conventions

Dependency injection

Never invent decisions.

Only record decisions supported by repository evidence.

------------------------------------------------------------

## roadmap.md

Summarize

Completed

In Progress

Planned

based only on repository evidence.

------------------------------------------------------------

## known_issues.md

Record only issues that are clearly visible.

Examples

TODOs

FIXMEs

Broken tests

Known warnings

Missing implementations

Do not speculate.

------------------------------------------------------------

------------------------------------------------------------

## Step 2.5

Inside

.agent/templates

create reusable markdown templates if they do not already exist.

Create:

overview_template.md

architecture_template.md

current_template.md

decision_template.md

session_template.md

------------------------------------------------------------

These templates define the standard structure used by future workflows.

They are generic.

Do NOT include project-specific information.

Do NOT analyze the repository when creating them.

These templates should work for any software project.

------------------------------------------------------------

overview_template.md

Include sections for:

- Project Name
- Description
- Goals
- Technologies
- Major Features
- Repository Structure
- Notes

------------------------------------------------------------

architecture_template.md

Include sections for:

- Architecture Overview
- Major Components
- Data Flow
- External Dependencies
- Entry Points
- Folder Responsibilities
- Important Design Notes

------------------------------------------------------------

current_template.md

Include sections for:

- Current Feature
- Current Branch
- Current Goal
- Completed
- Next Task
- Blockers
- Last Updated

------------------------------------------------------------

decision_template.md

Include sections for:

- Decision
- Date
- Context
- Decision Made
- Reasoning
- Consequences

This template should encourage appending new decisions instead of rewriting history.

------------------------------------------------------------

session_template.md

Include sections for:

- Date
- Session Summary
- Completed Work
- Decisions Made
- Issues Encountered
- Next Session
- Notes

This template should be suitable for every future work session.

------------------------------------------------------------

Future workflows should use these templates whenever creating or updating memory files to ensure a consistent structure across every project.



## Step 3

Inside

.agent/workflows

create

initialize.md

start.md

shutdown.md

refresh.md

checkpoint.md

review.md

------------------------------------------------------------

initialize.md

Purpose

One-time repository onboarding.

Workflow

- Read AGENT.md
- Analyze repository
- Create all memory files
- Build semantic index
- Summarize project
- Wait for user review

------------------------------------------------------------

start.md

Purpose

Beginning of every new chat.

Workflow

1. Read AGENT.md
2. Load overview.md
3. Load architecture.md
4. Load index.md
5. Load current.md
6. Load decisions.md
7. Load latest session
8. Summarize current project
9. Identify current work
10. Wait for user instructions

Never rewrite memory during startup.

------------------------------------------------------------

shutdown.md

Purpose

End of work session.

Workflow

Review:

- today's conversation
- changed files
- repository state

Update

current.md

Append today's session log

Update decisions.md only if new architectural decisions were made

Update index.md only if project structure changed

Update roadmap.md if progress changed

Update known_issues.md if new confirmed issues appeared

Produce a concise end-of-session summary.

Never regenerate the entire memory.

Only modify affected sections.

------------------------------------------------------------

checkpoint.md

Purpose

Save progress during long work sessions.

Update current.md.

Append temporary session summary.

Do not rewrite architecture.

------------------------------------------------------------

refresh.md

Purpose

Repository re-analysis after major refactors.

Re-scan repository.

Update

architecture.md

index.md

overview.md (only if necessary)

Preserve all session history.

------------------------------------------------------------

review.md

Purpose

Pre-commit / pre-PR review.

Check

architecture consistency

coding style

dead code

duplicated code

missing tests

possible bugs

Do not modify project memory.

------------------------------------------------------------

## Step 4

Create today's session inside

.agent/memory/sessions/

Use today's date as the filename.

Initialize it with

Repository initialized.

Summary of repository.

Current project status.

------------------------------------------------------------

## Step 5

Review everything.

Ensure

- no duplicated information
- memory is concise
- memory references repository instead of copying code
- index.md is semantic rather than a directory listing

------------------------------------------------------------

Finally provide

1. A summary of what was created.

2. Any assumptions made.

3. Any information you could not determine from the repository.

Wait for my review before making any code changes.