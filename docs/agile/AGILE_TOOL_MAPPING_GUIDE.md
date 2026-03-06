# Agile Tool Mapping Guide

This guide shows how to map all user stories from this project into an Agile board.

## Files in This Folder
- `AGILE_USER_STORY_TRACEABILITY.md`: Full story-to-code mapping and status.
- `USER_STORIES_BOARD_IMPORT.csv`: Import-ready backlog for Agile tools.

## Option A: GitHub Projects (Recommended)
1. Create a new project board.
2. Add columns: `Backlog`, `Ready`, `In Progress`, `In Review`, `Done`.
3. Import `USER_STORIES_BOARD_IMPORT.csv` as items.
4. Add custom fields:
   - `Story ID` (text)
   - `Priority` (single select)
   - `Sprint` (single select)
   - `Status` (single select)
5. Move stories to current status using `AGILE_USER_STORY_TRACEABILITY.md`.
6. Link commits/PRs to each story card.

## Option B: Jira
1. Create project with Scrum template.
2. Import `USER_STORIES_BOARD_IMPORT.csv` via CSV importer.
3. Map CSV fields to Jira fields:
   - `Title` -> Summary
   - `Story ID` -> Label or custom field
   - `Priority` -> Priority
   - `Status` -> Status
   - `Sprint` -> Sprint
4. Add acceptance criteria from `docs/USER_STORIES.md` into ticket descriptions.

## Option C: Trello
1. Create board with lists: `Backlog`, `Ready`, `In Progress`, `In Review`, `Done`.
2. Use CSV import power-up or copy stories manually from CSV.
3. Use labels for `Must`, `Should`, `Could`.
4. Store implementation evidence links in card descriptions.

## Evidence Checklist for Assessment
To show this criterion is fulfilled, capture screenshots of:
1. Backlog with all stories imported.
2. Story cards mapped to statuses.
3. Story card showing implementation evidence and linked files/commits.
4. At least one completed sprint/iteration view.

## Current Story Summary
- `Done`: 11 stories
- `Partial`: 6 stories
- `Backlog`: 15 stories

This summary is derived from `AGILE_USER_STORY_TRACEABILITY.md` and should be updated as development progresses.
