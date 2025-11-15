import tkinter as tk
from tkinter import ttk
from src.calculations.force_calculator import SuspensionForceCalculator


class LoadConditionsTab:
    def __init__(self, parent_notebook, data_loader):
        self.data_loader = data_loader
        self.force_calculator = SuspensionForceCalculator()

        self.load_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.load_frame, text="Load Conditions")

        # Create main layout
        self.setup_ui()

        # Initialize with default values
        self.update_results()

    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.load_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="External Forces (lbf)", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Force inputs
        forces_frame = ttk.Frame(input_frame)
        forces_frame.pack(fill=tk.X)

        # Fx input
        ttk.Label(forces_frame, text="Fx (Longitudinal):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.fx_var = tk.DoubleVar(value=0.0)
        fx_entry = ttk.Entry(forces_frame, textvariable=self.fx_var, width=15)
        fx_entry.grid(row=0, column=1, padx=(0, 20))
        ttk.Label(forces_frame, text="lbf").grid(row=0, column=2, sticky=tk.W)

        # Fy input
        ttk.Label(forces_frame, text="Fy (Lateral):").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.fy_var = tk.DoubleVar(value=371.423)
        fy_entry = ttk.Entry(forces_frame, textvariable=self.fy_var, width=15)
        fy_entry.grid(row=1, column=1, padx=(0, 20), pady=5)
        ttk.Label(forces_frame, text="lbf").grid(row=1, column=2, sticky=tk.W, pady=5)

        # Fz input
        ttk.Label(forces_frame, text="Fz (Vertical):").grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        self.fz_var = tk.DoubleVar(value=400.0)
        fz_entry = ttk.Entry(forces_frame, textvariable=self.fz_var, width=15)
        fz_entry.grid(row=2, column=1, padx=(0, 20))
        ttk.Label(forces_frame, text="lbf").grid(row=2, column=2, sticky=tk.W)

        # Suspension type selection
        ttk.Label(forces_frame, text="Suspension Type:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.suspension_var = tk.StringVar(value="pushrod")
        suspension_combo = ttk.Combobox(forces_frame, textvariable=self.suspension_var,
                                       values=["basic", "pushrod"], state="readonly", width=12)
        suspension_combo.grid(row=3, column=1, padx=(0, 20), pady=(10, 0), sticky=tk.W)

        # Calculate button
        calc_button = ttk.Button(forces_frame, text="Calculate Forces", command=self.update_results)
        calc_button.grid(row=4, column=0, columnspan=3, pady=(15, 0))

        # Bind enter key to calculate
        for entry in [fx_entry, fy_entry, fz_entry]:
            entry.bind('<Return>', lambda e: self.update_results())

        suspension_combo.bind('<<ComboboxSelected>>', lambda e: self.update_results())

        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Force Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Results text area
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=25, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Make text area read-only
        self.results_text.config(state=tk.DISABLED)

    def update_results(self):
        """Calculate and display the suspension member forces"""
        try:
            # Get force values
            fx = self.fx_var.get()
            fy = self.fy_var.get()
            fz = self.fz_var.get()
            external_force = [fx, fy, fz]

            # Get suspension type
            suspension_type = self.suspension_var.get()

            # Convert data loader format to coordinates
            coordinates = self.force_calculator.convert_data_loader_to_coordinates(
                self.data_loader, suspension_type)

            # Calculate forces
            results = self.force_calculator.calculate_forces(coordinates, external_force)

            # Format results
            formatted_results = self.force_calculator.get_formatted_results(results)

            # Update text area
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, formatted_results)
            self.results_text.config(state=tk.DISABLED)

        except Exception as e:
            # Display error
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error calculating forces:\n{str(e)}")
            self.results_text.config(state=tk.DISABLED)