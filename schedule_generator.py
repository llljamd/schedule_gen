# schedule_generator.py

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
import random
import json
from utils import read_employees
from constants import STORES, DAYS, SHIFTS
import platform  # To handle platform-specific mouse wheel behavior

class ScheduleGenerator(ctk.CTkToplevel):
    def __init__(self, master, selected_employees):
        super().__init__(master)
        self.title("Generated Schedule")
        self.geometry("1200x900")
        self.selected_employees = selected_employees  # List of selected employees

        # Open in full-screen mode
        self.attributes("-fullscreen", True)

        # Add a frame to hold the text widget and scrollbars
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Add a vertical scrollbar
        self.v_scrollbar = ctk.CTkScrollbar(self.frame, orientation="vertical")
        self.v_scrollbar.pack(side="right", fill="y")

        # Add the text widget
        self.schedule_text = tk.Text(
            self.frame,
            wrap="none",  # Disable text wrapping
            font=("Courier", 12),  # Fixed-width font for consistent alignment
            yscrollcommand=self.v_scrollbar.set
        )
        self.schedule_text.pack(fill="both", expand=True)

        # Configure the vertical scrollbar
        self.v_scrollbar.configure(command=self.schedule_text.yview)

        # Add mouse wheel support for scrolling
        self.bind_mouse_wheel(self.schedule_text)

        try:
            self.generate_schedule()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate schedule: {e}")
            self.destroy()

    def bind_mouse_wheel(self, widget):
        """Bind mouse wheel events to enable scrolling."""
        if platform.system() == "Windows" or platform.system() == "Linux":
            widget.bind_all("<MouseWheel>", lambda e: widget.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        elif platform.system() == "Darwin":  # macOS
            widget.bind_all("<MouseWheel>", lambda e: widget.yview_scroll(int(-1 * e.delta), "units"))

    def generate_schedule(self):
        """Generate a schedule based on employee availability."""
        employees = read_employees()
        if not employees:
            raise Exception("No employees available to generate a schedule.")

        # Filter employees based on selection
        employees = [emp for emp in employees if emp["name"] in self.selected_employees]

        schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        employee_shifts = defaultdict(int)  # Track shifts per employee

        for day in DAYS:
            for shift in SHIFTS:
                for store in STORES:
                    available_employees = [
                        emp for emp in employees
                        if store in emp["stores"] and f"{shift} {day[:3].upper()}" in emp["hours"]
                        and employee_shifts[emp["name"]] < 5  # Limit shifts per employee
                    ]
                    selected_employees = random.sample(available_employees, min(3, len(available_employees)))
                    schedule[day][shift][store] = [emp["name"] for emp in selected_employees]
                    for emp in selected_employees:
                        employee_shifts[emp["name"]] += 1

        self.display_schedule(schedule)

    def display_schedule(self, schedule):
        """Display the generated schedule in the new layout."""
        # Define column widths
        store_col_width = 15  # Width for the store column
        day_col_width = 12    # Width for each day column
        padding = " " * 2     # Padding between columns

        # Create the header row
        header1 = f"{'Store':<{store_col_width}}" + padding
        header1 += f"{'AM':<{day_col_width}}" + padding
        for day in DAYS:
            header1 += f"{day[:3].upper():<{day_col_width}}" + padding
        header1 += "\n"

        header2 = " " * (store_col_width + len(padding))  # Align with "Store"
        header2 += f"{'PM':<{day_col_width}}" + padding
        header2 += " " * (day_col_width + len(padding)) * len(DAYS)  # Align with days
        header2 += "\n"

        separator = "-" * (store_col_width + (day_col_width + len(padding)) * (len(DAYS) + 1)) + "\n"

        schedule_text = header1 + header2 + separator

        # Insert the header into the text widget
        self.schedule_text.delete("1.0", "end")
        self.schedule_text.insert("1.0", schedule_text)

        # Highlight only the "AM" and "PM" text in the header
        am_start = "1." + str(len("Store") + len(padding))  # Start of "AM"
        am_end = "1." + str(len("Store") + len(padding) + len("AM"))  # End of "AM"
        self.schedule_text.tag_add("am_shift", am_start, am_end)

        pm_start = "2." + str(len("Store") + len(padding))  # Start of "PM"
        pm_end = "2." + str(len("Store") + len(padding) + len("PM"))  # End of "PM"
        self.schedule_text.tag_add("pm_shift", pm_start, pm_end)

        for store in STORES:
            # Store name row
            store_row = f"{store:<{store_col_width}}" + padding
            self.schedule_text.insert("end", store_row + "\n")

            # AM and PM shifts for each day
            for shift in SHIFTS:
                shift_row = " " * (store_col_width + len(padding))  # Align with "Store"
                shift_row += f"{shift}: "  # Add shift label (AM/PM)
                for day in DAYS:
                    employees = schedule.get(day, {}).get(shift, {}).get(store, [])
                    if employees:
                        # Display each employee on a new line under the respective day
                        for emp in employees:
                            shift_row += f"{emp:<{day_col_width}}" + padding
                        shift_row += "\n" + " " * (store_col_width + len(padding) + len("AM: "))  # Align next employee
                    else:
                        # Leave the spot empty if no employees are available
                        shift_row += f"{' ':<{day_col_width}}" + padding
                self.schedule_text.insert("end", shift_row + "\n")
            self.schedule_text.insert("end", "\n")  # Extra spacing between stores

        # Add color coding for AM and PM shifts in the schedule
        self.color_code_shifts()

    def color_code_shifts(self):
        """Apply background colors to AM and PM shifts for better readability."""
        self.schedule_text.tag_configure("am_shift", background="#D6EAF8")  # Light blue for AM
        self.schedule_text.tag_configure("pm_shift", background="#FADBD8")  # Light red for PM

        # Apply tags to AM and PM rows
        start_index = "1.0"
        while True:
            # Find the next AM row
            am_start = self.schedule_text.search("AM:", start_index, stopindex="end")
            if not am_start:
                break
            am_end = f"{am_start} lineend"
            self.schedule_text.tag_add("am_shift", am_start, am_end)

            # Find the next PM row
            pm_start = self.schedule_text.search("PM:", start_index, stopindex="end")
            if not pm_start:
                break
            pm_end = f"{pm_start} lineend"
            self.schedule_text.tag_add("pm_shift", pm_start, pm_end)

            start_index = pm_end