# Assessment Checklist Coverage

This file maps the project implementation to the requested assessment criteria.

## 1) At least 1 original custom model with associated functionalities
- Custom model: `Task` in `app_onlystudies/models.py`
- Functionalities:
  - List: `/tasks/`
  - Create: `/tasks/add/`
  - Update: `/tasks/<pk>/edit/`
  - Delete: `/tasks/<pk>/delete/`
  - Filter + sorting support in `TaskListView`

## 2) At least one front-end form with CRUD (no admin required)
- Front-end forms for `Task`:
  - Create form: `templates/create_task.html`
  - Update form: `templates/edit_task.html`
  - Delete confirmation form: `templates/task_confirm_delete.html`
- Views in `app_onlystudies/views.py`: `CreateTaskView`, `UpdateTaskView`, `DeleteTaskView`

## 3) Front-end UI element to delete records (no admin required)
- Delete button included on `templates/tasks.html` for each task.
- Confirmation + delete submission on `templates/task_confirm_delete.html`.

## 4) Evidence of Agile methodologies in repository
- `docs/USER_STORIES.md`
- `docs/COMMIT_CHECKLIST.txt`
- Iterative delivery captured in Git commit history and deployment notes.

## 5) DEBUG mode set to False
- Configured in `only_studies/settings.py`:
  - `DEBUG = False`

## 6) Working register/login/logout
- Views and routes:
  - Signup: `/signup/`
  - Login: `/login/`
  - Logout: `/logout/`
- Tests: `AuthenticationTest` in `app_onlystudies/tests.py`

## 7) Detailed testing write-ups beyond validation tools
- `docs/Manual_Testing_Guide.md`
- `docs/AUTHENTICATION_TESTS.md`
- `docs/SECURITY_VERIFICATION.md`
- `docs/DATABASE_DEBUG_REPORT.md`

## Verification command
```bash
python manage.py test app_onlystudies
```
