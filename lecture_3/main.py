students = []

def find_student(name):
    for student in students:
        if student["name"] == name:
            return student
    return None

while True:
    print("--- Student Grade Analyzer ---")
    print("1. Add a new student")
    print("2. Add grades for a student")
    print("3. Generate a full report")
    print("4. Find the top student")
    print("5. Exit program")

    try:
        choice = int(input("\nEnter your choice: "))
    except ValueError:
        print("Invalid input. Please enter a number.\n")
        continue

    if choice == 1:
        name = input("\nEnter student name: ")
        if not name:
            print("Name cannot be empty.\n")
            continue
        if find_student(name):
            print("This student already exists.\n")
        else:
            students.append({"name": name, "grades": []})

    elif choice == 2:
        name = input("\nEnter student name: ")
        student = find_student(name)
        if not student:
            print("Student not found.\n")
            continue

        print()
        while True:
            grade_input = input("Enter a grade (or 'done' to finish): ")
            if grade_input.lower() == "done":
                print()
                break
            try:
                grade = int(grade_input)
                student["grades"].append(grade)
            except ValueError:
                print("Invalid input. Please enter a number.")

    elif choice == 3:
        if not students:
            print("\nNo students added yet.\n")
            continue

        print("\n--- Student Report ---")
        valid_averages = []

        for student in students:
            grades = student["grades"]
            try:
                avg = sum(grades) / len(grades)
                print(f"{student['name']}'s average grade is {avg:.1f}.")
                valid_averages.append(avg)
            except ZeroDivisionError:
                print(f"{student['name']}'s average grade is N/A.")

        if valid_averages:
            max_avg = max(valid_averages)
            min_avg = min(valid_averages)
            overall_avg = sum(valid_averages) / len(valid_averages)
            print("-------------------------")
            print(f"Max Average: {max_avg:.1f}")
            print(f"Min Average: {min_avg:.1f}")
            print(f"Overall Average: {overall_avg:.1f}")
        print()

    elif choice == 4:
        valid_students = [s for s in students if s["grades"]]
        if not valid_students:
            print("\nNo students with grades to determine the top performer.\n")
            continue

        top_student = max(valid_students, key=lambda s: sum(s["grades"]) / len(s["grades"]))
        top_avg = sum(top_student["grades"]) / len(top_student["grades"])
        print(f"\nThe student with the highest average is {top_student['name']} with a grade of {top_avg:.1f}.\n")

    elif choice == 5:
        print("\nExiting program.")
        break

    else:
        print("Invalid choice. Please enter a number between 1 and 5.\n")