# Full Application Test Procedures

This document defines manual and automated Python test procedures to assess:
- Functionality
- Usability
- Responsiveness
- Data management

For browser-console-based manual JavaScript procedures, see:
- `docs/JS_MANUAL_TEST_PROCEDURES.md`

## 1. Automated Procedures (Python)

### 1.1 Run full app procedure suite
```bash
python manage.py test app_onlystudies.test_procedures -v 2
```

### 1.2 Coverage by area
- `FullAppFunctionalityProcedureTest`:
  - Public route availability
  - Login-required endpoint protection
  - Role-restricted blog management access
- `FullAppUsabilityResponsivenessProcedureTest`:
  - Presence of responsive and accessibility hooks in rendered templates
  - Login-state visibility (guest vs authenticated)
- `FullAppDataManagementProcedureTest`:
  - Per-user data isolation for tasks/appointments/notifications
  - DB integrity checks (vote uniqueness, appointment temporal validation)

### 1.3 Exit criteria
- All tests in `app_onlystudies.test_procedures` pass
- No Django system-check errors

## 2. Manual Procedures

## 2.1 Functionality
1. Register one `Student` and one `Instructor` account.
2. Verify `Student` can log in and use tasks, appointments, forum.
3. Verify `Student` cannot access `Create News Story` endpoint directly (`/blog/create/`).
4. Verify `Instructor` can access `Create News Story` and submit a post.
5. Verify edit/delete permissions: users can only manage their own records unless admin.

Expected result:
- Core flows work end-to-end and restricted actions are blocked for unauthorized users.

## 2.2 Usability
1. Confirm navigation shows `Login/Sign Up` when logged out.
2. Confirm navigation shows `Welcome, <name>` and `Logout` when logged in.
3. Trigger invalid form submissions and verify clear field-level errors.
4. Verify keyboard navigation can reach major controls and skip link.

Expected result:
- Login state and validation feedback are clearly visible.

## 2.3 Responsiveness
1. Open home page and test breakpoints at 375px, 768px, 1024px, 1440px.
2. Check navbar toggling on small screens.
3. Confirm blog/notifications cards reflow correctly.
4. Validate forms remain usable on mobile (controls are readable and tappable).

Expected result:
- Layout remains stable and usable across viewport sizes.

## 2.4 Data Management
1. Create records for User A and User B (tasks, appointments).
2. Log in as User A and verify User B records are not visible.
3. Verify notifications API only returns current-user notifications.
4. Attempt duplicate same-user vote on same post and verify integrity enforcement.

Expected result:
- Data is isolated per user and integrity constraints prevent invalid states.

## 3. Recommended Execution Order
1. `python manage.py check`
2. `python manage.py test app_onlystudies.test_procedures -v 2`
3. Manual procedures in sections 2.1 -> 2.4

## 4. Reporting Template
Use this simple pass/fail table for assessment evidence:

| Area | Procedure | Result | Notes |
|---|---|---|---|
| Functionality | Automated suite | PASS/FAIL | |
| Usability | Manual 2.2 | PASS/FAIL | |
| Responsiveness | Manual 2.3 | PASS/FAIL | |
| Data Management | Automated + Manual 2.4 | PASS/FAIL | |
