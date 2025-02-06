import json
from tkinter import messagebox

def read_employees():
    """Read employees from the JSON file."""
    try:
        with open("employee.json", "r") as file:
            return [json.loads(line) for line in file]
    except FileNotFoundError:
        return []
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read employees: {e}")
        return []

def write_employees(employees):
    """Write employees to the JSON file."""
    try:
        with open("employee.json", "w") as file:
            for emp in employees:
                file.write(json.dumps(emp) + "\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write employees: {e}")

def is_duplicate_name(name):
    """Check if an employee name already exists (case-insensitive)."""
    employees = read_employees()
    for emp in employees:
        if emp["name"].strip().lower() == name.strip().lower():
            return True
    return False

def validate_name(name):
    """Validate the employee name."""
    if not name:
        return "Name is required!"
    if not name.replace(" ", "").isalpha():
        return "Name should only contain alphabets and spaces."
    return None