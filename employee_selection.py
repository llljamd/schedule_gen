# employee_selection.py

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
from utils import read_employees
import platform  # To handle platform-specific mouse wheel behavior

class EmployeeSelection(ctk.CTkToplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("Select Employees for Scheduling")
        self.geometry("500x600")
        self.callback = callback

        # Load employees and their selection state
        self.employees = read_employees()
        self.selection_state = self.load_selection_state()

        # Create a main frame to hold everything
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create a canvas and a scrollbar
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ctk.CTkScrollbar(self.main_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)

        # Configure the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Add mouse wheel support for scrolling
        self.bind_mouse_wheel(self.canvas)

        # Add a label for instructions
        self.instruction_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Select employees to include in the schedule:",
            font=("Arial", 14, "bold")
        )
        self.instruction_label.pack(pady=(10, 5), anchor="w")

        # Add checkboxes for each employee inside the scrollable frame
        self.checkbox_vars = {}
        for i, emp in enumerate(self.employees):
            var = tk.BooleanVar(value=self.selection_state.get(emp["name"], True))
            checkbox = ctk.CTkCheckBox(self.scrollable_frame, text=emp["name"], variable=var)
            checkbox.pack(anchor="w", pady=5, padx=10)
            self.checkbox_vars[emp["name"]] = var

        # Add a button frame at the bottom for the "Confirm" button
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", padx=10, pady=10)

        # Add the "Confirm" button
        self.confirm_button = ctk.CTkButton(
            self.button_frame,
            text="Confirm",
            command=self.confirm_selection,
            font=("Arial", 14),
            width=100,
            height=40
        )
        self.confirm_button.pack(pady=10)

    def bind_mouse_wheel(self, widget):
        """Bind mouse wheel events to enable scrolling."""
        if platform.system() == "Windows" or platform.system() == "Linux":
            widget.bind_all("<MouseWheel>", lambda e: widget.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        elif platform.system() == "Darwin":  # macOS
            widget.bind_all("<MouseWheel>", lambda e: widget.yview_scroll(int(-1 * e.delta), "units"))

    def load_selection_state(self):
        """Load the selection state of employees from a JSON file."""
        try:
            with open("employee_selection.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_selection_state(self):
        """Save the selection state of employees to a JSON file."""
        selection_state = {emp["name"]: var.get() for emp, var in zip(self.employees, self.checkbox_vars.values())}
        try:
            with open("employee_selection.json", "w") as file:
                json.dump(selection_state, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save selection state: {e}")

    def confirm_selection(self):
        """Confirm the selection and pass the selected employees to the callback."""
        selected_employees = [emp["name"] for emp, var in zip(self.employees, self.checkbox_vars.values()) if var.get()]
        self.save_selection_state()
        self.callback(selected_employees)
        self.destroy()