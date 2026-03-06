# Manual JavaScript Test Procedures

This document defines **manual JavaScript procedures** for assessing the full web application across:
- Functionality
- Usability
- Responsiveness
- Data management

These procedures are intended to be executed from the browser DevTools console on the running app.

## 1. Setup

1. Start the app and open it in the browser.
2. Open DevTools (`F12`) and switch to `Console`.
3. Load the helper runner from `scripts/manual_js_test_runner.js`.
4. Paste it into the console and run it.
5. Verify the loader message:

```text
OnlyStudiesManualTests loaded. Run: OnlyStudiesManualTests.runAll()
```

## 2. Procedure Execution

Run all checks:

```javascript
await OnlyStudiesManualTests.runAll();
```

Or run area-by-area:

```javascript
await OnlyStudiesManualTests.functionality();
OnlyStudiesManualTests.usability();
OnlyStudiesManualTests.responsiveness();
await OnlyStudiesManualTests.dataManagement();
```

## 3. Manual JavaScript Checks by Area

## 3.1 Functionality

Scope:
- Core navigation elements and search form presence
- Protected route behavior probes (`/tasks/`, `/appointments/`, `/notifications/`, `/blog/create/`)
- Required-field browser validation hooks

Expected outcome:
- Console shows `[PASS]` for baseline controls.
- Protected route checks:
  - While logged out: redirect-style behavior should be observed.
  - While logged in: `200` may be expected for authorized pages.

## 3.2 Usability

Scope:
- Skip-link presence
- Focusable controls availability
- Potentially unlabeled form controls detection

Expected outcome:
- Skip link and focusable controls pass.
- Any unlabeled controls appear as `[WARN]` and should be reviewed in templates.

## 3.3 Responsiveness

Scope:
- Horizontal overflow at current viewport
- Navbar toggler availability
- Approximate touch target sizing for clickable controls

Expected outcome:
- No horizontal overflow.
- Navbar toggler exists.
- No undersized primary tap targets, or warnings tracked for remediation.

Manual viewport repetition:
1. Enable device emulation in DevTools.
2. Repeat `OnlyStudiesManualTests.responsiveness()` at 375px, 768px, 1024px, and 1440px.
3. Record any overflow or target-size warnings by breakpoint.

## 3.4 Data Management

Scope:
- Notifications API payload shape
- Basic sensitive-field leak smoke check
- Manual cross-user dataset isolation verification

Expected outcome:
- `notifications` key exists in payload.
- No obvious sensitive field terms in payload.
- Cross-user data overlap is not observed when repeating checks in a second browser profile/session.

## 4. Recording Results

Use this table format in test evidence:

| Area | Console Procedure | Result | Notes |
|---|---|---|---|
| Functionality | `OnlyStudiesManualTests.functionality()` | PASS/FAIL/WARN | |
| Usability | `OnlyStudiesManualTests.usability()` | PASS/FAIL/WARN | |
| Responsiveness | `OnlyStudiesManualTests.responsiveness()` at 4 breakpoints | PASS/FAIL/WARN | |
| Data Management | `OnlyStudiesManualTests.dataManagement()` (+ cross-user repeat) | PASS/FAIL/WARN | |

## 5. Exit Criteria

- All four areas executed and logged.
- Any warnings triaged with notes.
- No FAIL results remain unresolved.
