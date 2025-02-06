import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
from employee_form import EmployeeForm
from utils import read_employees

class EmployeeList(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Edit Employee")
        self.geometry("400x500")

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill="both", expand=True, padx=20, pady=20)

        try:
            self.load_employees()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load employees: {e}")
            self.listbox.insert(tk.END, "No employees found")
            self.listbox.config(state=tk.DISABLED)

        self.editButton = ctk.CTkButton(self, text="Edit Selected", command=self.open_edit_form)
        self.editButton.pack(pady=10)

    def load_employees(self):
        """Load employees from the file."""
        employees = read_employees()
        if not employees:
            raise Exception("No employees found in the file.")
        for emp in employees:
            self.listbox.insert(tk.END, emp["name"])

    def open_edit_form(self):
        """Open the edit form for the selected employee."""
        selected_index = self.listbox.curselection()
        if selected_index:
            try:
                employees = read_employees()
                EmployeeForm(self.master, json.dumps(employees[selected_index[0]]))
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open edit form: {e}")