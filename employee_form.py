import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
import json
from utils import read_employees, write_employees, is_duplicate_name, validate_name
from constants import STORES, DAYS, SHIFTS

class EmployeeForm(ctk.CTkToplevel):
    def __init__(self, master, employee_data=None):
        super().__init__(master)
        self.title("Employee Form")
        self.geometry("1200x800")
        self.minsize(1200, 800)
        self.original_data = employee_data  # Store original data for reference

        # Configure grid layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure((1, 2, 3, 4, 5, 6, 7), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)

        # Name Section
        self.nameLabel = ctk.CTkLabel(self, text="Name")
        self.nameLabel.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.nameEntry = ctk.CTkEntry(self)
        self.nameEntry.grid(row=0, column=1, columnspan=6, padx=10, pady=10, sticky="ew")

        # Store Section
        self.create_store_section()
        # Hours Section
        self.create_hours_section()
        # Collaborate Section
        self.create_collab_section()

        # Buttons
        self.generateResultsButton = ctk.CTkButton(
            self, text="Add Employee" if not employee_data else "Update Employee",
            command=self.generateResults if not employee_data else self.update_employee
        )
        self.generateResultsButton.grid(row=6, column=1, columnspan=3, padx=20, pady=20, sticky="ew")

        self.clearButton = ctk.CTkButton(self, text="Clear Form", command=self.clear_form)
        self.clearButton.grid(row=6, column=4, columnspan=3, padx=20, pady=20, sticky="ew")

        if employee_data:
            self.load_existing_data(employee_data)

    def create_store_section(self):
        """Create the store selection section with checkboxes."""
        self.choiceLabel = ctk.CTkLabel(self, text="Available Store")
        self.choiceLabel.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.store_vars = {store: tk.BooleanVar(value=False) for store in STORES}
        for i, store in enumerate(STORES):
            checkbox = ctk.CTkCheckBox(self, text=store, variable=self.store_vars[store])
            checkbox.grid(row=1, column=i + 1, padx=5, pady=5, sticky="w")

    def create_hours_section(self):
        """Create the hours selection section with checkboxes."""
        self.choiceLabel = ctk.CTkLabel(self, text="Available Hours")
        self.choiceLabel.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.hour_vars = {f"{period} {day[:3].upper()}": tk.BooleanVar(value=False) for day in DAYS for period in SHIFTS}
        for i, day in enumerate(DAYS):
            label = ctk.CTkLabel(self, text=day)
            label.grid(row=2, column=i + 1, pady=5, padx=(5, 2), sticky="w")
            for j, period in enumerate(SHIFTS):
                checkbox = ctk.CTkCheckBox(self, text=period, variable=self.hour_vars[f"{period} {day[:3].upper()}"])
                checkbox.grid(row=3 + j, column=i + 1, padx=2, pady=5, sticky="w")

    def create_collab_section(self):
        """Create the collaborator dropdown section."""
        self.collab = ctk.CTkLabel(self, text="Collaborate")
        self.collab.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        values = self.load_collab_values()
        self.collabDrop = ctk.CTkOptionMenu(self, values=values)
        self.collabDrop.grid(row=5, column=1, padx=20, pady=20, columnspan=6, sticky="ew")

    def load_collab_values(self):
        """Load collaborator values from the employee file."""
        employees = read_employees()
        names = sorted([emp["name"] for emp in employees], key=lambda x: x.lower())
        return ["None"] + names

    def load_existing_data(self, employee_data):
        """Load existing employee data into the form."""
        try:
            emp = json.loads(employee_data)
            self.nameEntry.insert(0, emp["name"])
            for store in self.store_vars:
                if store in emp["stores"]:
                    self.store_vars[store].set(True)
            for hour in self.hour_vars:
                if hour in emp["hours"]:
                    self.hour_vars[hour].set(True)
            self.collabDrop.set(emp["collab"] if emp["collab"] != "No Collab" else "None")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load existing data: {e}")

    def generateResults(self):
        """Validate inputs and save the employee data."""
        if not self.validate_inputs():
            return
        text = self.createText()
        if text != "No name was entered":
            try:
                if is_duplicate_name(self.nameEntry.get().strip()):
                    messagebox.showwarning("Error", "Employee name already exists (case-insensitive)!")
                    return
                self.save_employee(text)
                messagebox.showinfo("Success", "Employee added successfully!")
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save employee: {e}")
        else:
            messagebox.showwarning("Error", "No name was entered")

    def validate_inputs(self):
        """Validate form inputs."""
        name = self.nameEntry.get().strip()
        name_error = validate_name(name)
        if name_error:
            messagebox.showwarning("Error", name_error)
            return False
        if not any(var.get() for var in self.store_vars.values()):
            messagebox.showwarning("Error", "At least one store must be selected.")
            return False
        if not any(var.get() for var in self.hour_vars.values()):
            messagebox.showwarning("Error", "At least one hour must be selected.")
            return False
        return True

    def createText(self):
        """Generate a JSON string from the form data."""
        name = self.nameEntry.get().strip()
        if not name:
            return "No name was entered"

        store = [s for s, var in self.store_vars.items() if var.get()] or ["No store selected"]
        hours = [h for h, var in self.hour_vars.items() if var.get()] or ["No hours selected"]
        collab = self.collabDrop.get() if self.collabDrop.get() != "None" else "No Collab"

        return json.dumps({
            "name": name,
            "stores": store,
            "hours": hours,
            "collab": collab
        })

    def save_employee(self, text):
        """Save employee data to the file."""
        try:
            with open("employee.json", "a") as file:
                file.write(text + "\n")
        except Exception as e:
            raise Exception(f"Failed to write to file: {e}")

    def update_employee(self):
        """Update existing employee data."""
        if not self.validate_inputs():
            return
        updated_text = self.createText()
        if updated_text != "No name was entered":
            try:
                self.replace_employee(self.original_data, updated_text)
                messagebox.showinfo("Success", "Employee updated successfully!")
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update employee: {e}")
        else:
            messagebox.showwarning("Error", "No name was entered")

    def replace_employee(self, old_data, new_data):
        """Replace old employee data with new data in the file."""
        employees = read_employees()
        updated_employees = [new_data if json.dumps(emp) == old_data else json.dumps(emp) for emp in employees]
        write_employees(updated_employees)

    def clear_form(self):
        """Clear all form fields."""
        self.nameEntry.delete(0, "end")
        for var in self.store_vars.values():
            var.set(False)
        for var in self.hour_vars.values():
            var.set(False)
        self.collabDrop.set("None")