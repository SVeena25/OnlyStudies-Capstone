# Agile User Story Traceability Matrix

This file maps all user stories to implementation status and project evidence.
Use this as proof for Agile planning, delivery tracking, and scope management.

## Status Legend
- `Done`: Story implemented and verifiable in current codebase.
- `Partial`: Core flow exists, but one or more acceptance criteria are not complete.
- `Backlog`: Not implemented yet.

## Sprint Legend
- `S1-S2`: Must-have delivery.
- `S3-S4`: Should-have delivery.
- `S5+`: Could-have delivery.

## Story Matrix
| ID | Priority | Status | Sprint | Story Summary | Evidence in Project |
|---|---|---|---|---|---|
| US-001 | Must | Done | S1-S2 | User signup | `app_onlystudies/views.py` (`SignUpView`), `templates/core/signup.html` |
| US-002 | Must | Partial | S1-S2 | User login | `CustomLoginView`, `templates/core/login.html` (no explicit Remember Me behavior) |
| US-003 | Must | Done | S1-S2 | User logout | `CustomLogoutView`, logout form in `templates/core/base.html` |
| US-004 | Must | Done | S1-S2 | Navigate categories/subcategories | Category dropdowns in `templates/core/base.html`, routes in `app_onlystudies/urls.py` |
| US-005 | Must | Done | S1-S2 | View category content | `CategoryView`, `templates/categories/category.html` |
| US-006 | Must | Done | S1-S2 | View subcategory details | `SubCategoryView`, `templates/categories/subcategory.html` |
| US-007 | Must | Done | S1-S2 | Home blog feed | `HomePage` context + `templates/core/index.html` |
| US-008 | Must | Partial | S1-S2 | Notifications | `notifications_api`, `templates/core/index.html` (no explicit count badge) |
| US-009 | Must | Done | S1-S2 | Explore exams | Exam cards in `templates/core/index.html`, `apply_exam` route/view |
| US-010 | Should | Partial | S3-S4 | Search by keyword | `SearchResultsView` works for blog/forum; not full course-wide search |
| US-011 | Should | Backlog | S3-S4 | Difficulty filter | Not implemented |
| US-012 | Should | Backlog | S3-S4 | User profile page/edit | Not implemented |
| US-013 | Should | Backlog | S3-S4 | Favorite courses | Not implemented |
| US-014 | Should | Done | S3-S4 | Ask forum questions | `AskQuestionView`, `templates/forum/ask_question.html` |
| US-015 | Should | Partial | S3-S4 | View answers and vote on answers | Answers and timestamps implemented; answer vote not implemented |
| US-016 | Should | Backlog | S3-S4 | Course curriculum view | Not implemented |
| US-017 | Should | Backlog | S3-S4 | Learning progress tracking | Not implemented |
| US-018 | Could | Backlog | S5+ | Video lectures | Not implemented |
| US-019 | Could | Backlog | S5+ | Download materials | Not implemented |
| US-020 | Could | Backlog | S5+ | Quizzes | Not implemented |
| US-021 | Could | Backlog | S5+ | Student networking | Not implemented |
| US-022 | Could | Backlog | S5+ | Social sharing | Not implemented |
| US-023 | Could | Backlog | S5+ | Study groups | Not implemented |
| US-024 | Could | Backlog | S5+ | Instructor course creation flow | Not implemented |
| US-025 | Could | Backlog | S5+ | Instructor analytics | Not implemented |
| US-026 | Could | Backlog | S5+ | Badges | Not implemented |
| US-027 | Could | Backlog | S5+ | Points system | Not implemented |
| US-028 | Could | Backlog | S5+ | Course purchase | Not implemented |
| US-029 | Could | Backlog | S5+ | Promo codes | Not implemented |
| US-030 | Could | Done | S5+ | Responsive design | Bootstrap responsive layout + custom CSS breakpoints in `static/css/style.css` |
| US-031 | Could | Partial | S5+ | Accessibility compliance | Skip link, focus styles, semantics improved; full WCAG audit evidence pending |
| US-032 | Could | Backlog | S5+ | Admin analytics dashboard | Not implemented |

## Recently Delivered Stories (Code Evidence)
- News posting flow: `CreateBlogPostView`, `templates/blog/create_blog_post.html`
- News comments: `BlogComment` model, `post_blog_comment`, comment UI in `templates/blog/blog_detail.html`
- Post voting: `BlogPostVote` model, `vote_blog_post`, vote UI in `templates/blog/blog_detail.html`
- Forum interactions: ask/answer/edit/delete in `app_onlystudies/views.py` and `templates/forum/*`

## Recommended Agile Board Columns
- `Backlog`
- `Ready`
- `In Progress`
- `In Review`
- `Done`

## Definition of Done (for this project)
- Acceptance criteria pass manually.
- `python manage.py check` passes.
- Relevant tests added/updated.
- Story mapped to evidence file(s) in this matrix.
