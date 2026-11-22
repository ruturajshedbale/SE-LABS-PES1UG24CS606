def format_course_code(code):
    """
    Formats 'cs 301' as 'CS301'.
    """
    if not isinstance(code, str):
        return ""

    parts = code.strip().split()
    if len(parts) != 2:
        return ""

    dept, number = parts
    if not dept or not number:
        return ""
    return dept.upper() + number

def total_credits(text):
    """
    Adds up comma-separated course credits.
    """
    if not isinstance(text, str):
        return 0

    total = 0
    for credit in text.split(','):
        credit = credit.strip()
        if not credit:
            continue
        try:
            value = int(credit)
        except (TypeError, ValueError):
            continue
        if value >= 0:
            total += value
    return total

def parse_student_record(line):
    """
    Parses 'SRN|name|status' into a dictionary.
    """
    if not isinstance(line, str):
        line = ""

    parts = line.split('|')
    parts.extend([""] * (3 - len(parts)))
    return {"srn": parts[0].strip().upper(),
            "name": parts[1].strip(),
            "status": parts[2].strip().lower()}

def main():
    print("==== Running format_course_code ====")
    value = input("Enter a course code as DEPT NUMBER (e.g. cs 301): ")
    print("Formatted course code:", format_course_code(value))

    print("\n==== Running total_credits ====")
    value = input("Enter course credits separated by commas (e.g. 4,3,4): ")
    print("Total credits:", total_credits(value))

    print("\n==== Running parse_student_record ====")
    value = input("Enter a student record as SRN|name|status (e.g. pes1ug23cs001|Asha|regular): ")
    print("Student record:", parse_student_record(value))

if __name__ == "__main__":
    main()
