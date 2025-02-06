# main.py

import customtkinter as ctk
from employee_form import EmployeeForm
from employee_list import EmployeeList
from schedule_generator import ScheduleGenerator
from employee_selection import EmployeeSelection

class MainPage(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Employee Management System")
        self.geometry("400x300")

        self.addEmployeeButton = ctk.CTkButton(self, text="Add Employee", command=self.open_employee_form)
        self.addEmployeeButton.pack(pady=10)

        self.editEmployeeButton = ctk.CTkButton(self, text="Edit Employee", command=self.open_employee_list)
        self.editEmployeeButton.pack(pady=10)

        self.generateScheduleButton = ctk.CTkButton(self, text="Generate Schedule", command=self.open_employee_selection)
        self.generateScheduleButton.pack(pady=10)

    def open_employee_form(self):
        """Open the employee form."""
        form = EmployeeForm(self)
        form.grab_set()
        form.focus_force()

    def open_employee_list(self):
        """Open the employee list for editing."""
        try:
            EmployeeList(self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open employee list: {e}")

    def open_employee_selection(self):
        """Open the employee selection menu before generating the schedule."""
        try:
            EmployeeSelection(self, self.generate_schedule)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open employee selection: {e}")

    def generate_schedule(self, selected_employees):
        """Generate and display the schedule for selected employees."""
        try:
            ScheduleGenerator(self, selected_employees)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate schedule: {e}")

if __name__ == "__main__":
    app = MainPage()
    app.mainloop()