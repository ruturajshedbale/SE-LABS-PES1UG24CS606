# Lab 2: Agile Backlog Creation & Sprint Simulation in Jira

**Course:** Software Engineering Laboratory
**Student:** PES1UG24CS606
**Project:** Group Travel Expense Simplification Engine
**Jira project key:** `GTES`

## Objective

Convert the functional requirements from Lab 1 into Agile Epics and User Stories, prioritize and estimate the backlog using the Fibonacci scale, simulate two one-week Scrum sprints, and analyse the burndown evidence.

## Deliverables

- [Full PDF report](./LAB2_SE_PES1UG24CS606_Report.pdf)
- [Editable DOCX report](./LAB2_SE_PES1UG24CS606_Report.docx)
- [Backlog screenshot](./screenshots/jira_backlog.png)
- [Sprint 1 board](./screenshots/sprint1_board.png)
- [Sprint 2 board](./screenshots/sprint2_board.png)
- [Sprint 1 burndown](./screenshots/burndown_chart_sprint1.png)
- [Sprint 2 burndown](./screenshots/burndown_chart.png)

## Epics

| Epic | Name | Lab 1 requirement |
|---|---|---|
| GTES-EPIC-1 | Debt Settlement Engine | FR-001 |
| GTES-EPIC-2 | Expense and Currency Capture | FR-002, FR-003 |
| GTES-EPIC-3 | Traveler Balance Visibility | FR-004 |
| GTES-EPIC-4 | Trip Member Administration | FR-005 |
| GTES-EPIC-5 | Performance and Access Security | NFR-001, NFR-002 |

## Sprint Summary

| Sprint | Commitment | Completed | Velocity |
|---|---:|---:|---:|
| Sprint 1 | 21 pts | 21 pts | 21 |
| Sprint 2 | 16 pts | 16 pts | 16 |
| Total | 37 pts | 37 pts | 37 |

The backlog contains eight User Stories with High or Medium priority and Fibonacci estimates from 3 to 8 points.

## Regenerate

```powershell
.\.venv\Scripts\python.exe .\Lab02\generate_lab2_assets.py
```

The generated screenshots are Jira-style simulation evidence. They can be replaced by actual Jira screenshots exported from the user's workspace.
