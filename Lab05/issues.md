# Static Analysis Findings and Fixes

Line numbers below refer to the original `car_rental.py` before edits.
Findings are ordered by severity. Bandit findings are all addressed; the
original source produced 11 findings (2 high, 4 medium, 5 low).

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---:|---|---|
| Weak licence digest | Bandit B324 — High | 48 | Unsalted SHA-1 is unsuitable for protecting identifying data. | Use PBKDF2-HMAC-SHA-256 with a fresh random salt and return the salt with the digest. |
| World-writable receipt | Bandit B103 — High | 67 | Mode `0o777` allows any local user to modify or read a receipt. | Remove the permissive chmod; create the temporary receipt with the platform's restrictive defaults. |
| SQL injection | Bandit B608 — Medium | 23, 26 | Customer data was interpolated into SQL statements. | Bind all values as SQLite parameters. The injection-shaped lookup now returns no rows. |
| Arbitrary promo execution | Bandit B102 — Medium | 53 | `exec` allowed a typed promo rule to run arbitrary Python. | Parse only the documented amount-times-discount form and reject other input. |
| Predictable temporary file | Bandit B306 — Medium | 63 | `tempfile.mktemp` separates name selection from file creation. | Use `NamedTemporaryFile` with `delete=False`, UTF-8, and a context manager. |
| Mutable default | Pylint W0102 | 16 | A shared `features=[]` list could leak changes between cars. | Use `None` and create a fresh list for each car. |
| Password embedded in source | Bandit B105/B107 — Low | 70–71 | A fixed admin password was embedded in the code. | Read the password from `CAR_RENTAL_ADMIN_PASSWORD`; compare with `hmac.compare_digest`. |
| Assertion used for validation | Bandit B101 — Low | 30 | `assert` checks can disappear under optimized Python. | Raise `ValueError` explicitly when a customer is not registered. |
| Suppressed error | Bandit B110 / Flake8 E722 — Low | 41–42 | A bare exception hid an unknown-car error and returned no clear result. | Raise `KeyError` for an unknown plate and return an explicit excess-distance charge. |
| Weak booking randomness | Bandit B311 — Low | 45 | The standard `random` generator is predictable for booking references. | Generate references with `secrets.token_hex`. |
| Invalid rental amount and dates | Manual behavior check | 31, 83–90 | The starter demo allowed a negative daily rate and a rental ending before it began, producing a negative total. | Validate rates and date order; correct the demo's Innova dates. |
| Booking availability | Manual behavior check | 31–34 | A car could be booked repeatedly without being marked rented. | Reject unavailable cars, mark successful rentals unavailable, and restore availability on return. |
| Style and maintainability | Pylint / Flake8 | Multiple | Missing documentation, camelCase names, unused import, long lines, and spacing violations obscured issues. | Remove unused imports, use snake_case, document functions, and format to satisfy Flake8. |

## Before/after analysis

| Tool | Before | After |
|---|---|---|
| Pylint | 4.94/10 | 10.00/10 |
| Bandit | 11 findings: 2 high, 4 medium, 5 low | 0 findings |
| Flake8 | Formatting and unused-import findings | 0 violations |

The raw, UTF-8 analyzer reports are saved beside this file:
`pylint_report_before.txt`, `bandit_report_before.txt`,
`flake8_report_before.txt`, `pylint_report.txt`, `bandit_report.txt`, and
`flake8_report.txt`.
