# Reflection

The handout asks for four reflection answers but does not include their exact
wording. These responses address the stated learning outcomes and the issues
found in this program.

## 1. What is static analysis, and how is it different from running the program?

Static analysis checks source code without executing its normal application
flow. It caught issues such as SQL built by concatenating text, unsafe `exec`,
weak hashing, and style problems before those paths were safely exercised.
Running the program was still useful because it exposed incorrect rental
results that the tools did not identify, such as a reversed date range and a
negative daily rate.

## 2. Which findings were most important, and why?

The highest-risk findings were the unsalted SHA-1 digest and the world-readable
receipt permissions. The SQL injection and arbitrary promo execution were also
important because they could expose customer data or run unintended code. I
addressed these before style-only findings.

## 3. How did Pylint, Bandit, and Flake8 complement one another?

Bandit highlighted security patterns, including query construction,
credential-handling, file permissions, and unsafe execution. Pylint identified
maintainability and correctness concerns such as the mutable default and
inconsistent naming. Flake8 made spacing, unused imports, and line length
consistent; the tools overlapped on some issues but caught different classes
of problems.

## 4. What changed in the program, and what did I learn?

I replaced unsafe or ambiguous behavior with explicit validation and errors,
then verified the changes with the three tools and nine regression tests.
Static analysis is most useful when its findings are reviewed in context:
the invalid demo dates and prices required actually running the program, while
tests helped confirm that the security fixes did not break normal rentals.
