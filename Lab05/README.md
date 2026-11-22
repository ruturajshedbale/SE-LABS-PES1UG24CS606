# Lab 5: Static Code Analysis - Car Rental System

This lab applies Pylint, Bandit, and Flake8 to the car-rental demo, records the
original findings, fixes the security and quality issues, and verifies the
updated program with regression tests.

## Aim

To identify and resolve security, correctness, and maintainability issues using
static-analysis tools, then confirm the changes with tests and a program run.

## Run and verify

Use Python 3.10 or newer:

```powershell
python car_rental.py
python -m unittest -v test_car_rental.py
python -m pylint car_rental.py
python -m bandit -r car_rental.py
python -m flake8 car_rental.py test_car_rental.py
```

Final results: Pylint **10.00/10**, Bandit **0 findings**, Flake8 **0
violations**, and all **9 regression tests pass**. The baseline reports record
Pylint **4.94/10**, 11 Bandit findings, and Flake8 violations.

To install the three analysis tools in a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install pylint bandit flake8
```

The admin password is read from `CAR_RENTAL_ADMIN_PASSWORD`; no default
credential is stored in the source.

## Submission files

- `Lab_5_Static_Code_Analysis_Lab_Report.docx` and `.pdf` - lab report with
  aim, eight task observations, conclusion, and an issues appendix.
- `car_rental.py` and `test_car_rental.py` - corrected program and regression
  tests.
- `pylint_report_before.txt`, `bandit_report_before.txt`, and
  `flake8_report_before.txt` - baseline analyzer output.
- `pylint_report.txt`, `bandit_report.txt`, and `flake8_report.txt` - final
  analyzer output.
- `program_output.txt` - output from running the demonstration.
- `issues.md` - original findings, severity, and fixes.
- `reflection.md` - four reflections on the analysis and fixes.

The report does not contain screenshots: genuine terminal-window capture was
unavailable in this environment, so no screenshots have been fabricated.
