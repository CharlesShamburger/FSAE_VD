"""
src/tabs/tire_analysis_tab.py

Tire Analysis Tab for FSAE TTC data analysis using Pacejka model
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
from scipy.io import loadmat
import logging


class TireAnalysisTab:
    def __init__(self, parent_notebook):
        self.logger = logging.getLogger(__name__)

        # Data storage
        self.raw_data = None
        self.filtered_data = None
        self.tire_model = None
        self.current_file = None

        # Create main frame
        self.tire_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.tire_frame, text="Tire Analysis")

        # Create main layout (horizontal split)
        main_paned = ttk.PanedWindow(self.tire_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Controls (notebook with tabs)
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=0)

        # Create notebook for left side tabs
        self.left_notebook = ttk.Notebook(left_frame)
        self.left_notebook.pack(fill=tk.BOTH, expand=True)

        # Data Filters tab
        filters_tab = ttk.Frame(self.left_notebook)
        self.left_notebook.add(filters_tab, text="Data Filters")

        # Create scrollable frame for filters tab
        filters_canvas = tk.Canvas(filters_tab)
        filters_scrollbar = ttk.Scrollbar(filters_tab, orient="vertical", command=filters_canvas.yview)
        filters_scrollable_frame = ttk.Frame(filters_canvas)

        filters_scrollable_frame.bind(
            "<Configure>",
            lambda e: filters_canvas.configure(scrollregion=filters_canvas.bbox("all"))
        )

        filters_canvas.create_window((0, 0), window=filters_scrollable_frame, anchor="nw")
        filters_canvas.configure(yscrollcommand=filters_scrollbar.set)

        filters_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        filters_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Analysis tab
        analysis_tab = ttk.Frame(self.left_notebook)
        self.left_notebook.add(analysis_tab, text="Analysis")

        # Create scrollable frame for analysis tab
        analysis_canvas = tk.Canvas(analysis_tab)
        analysis_scrollbar = ttk.Scrollbar(analysis_tab, orient="vertical", command=analysis_canvas.yview)
        analysis_scrollable_frame = ttk.Frame(analysis_canvas)

        analysis_scrollable_frame.bind(
            "<Configure>",
            lambda e: analysis_canvas.configure(scrollregion=analysis_canvas.bbox("all"))
        )

        analysis_canvas.create_window((0, 0), window=analysis_scrollable_frame, anchor="nw")
        analysis_canvas.configure(yscrollcommand=analysis_scrollbar.set)

        analysis_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        analysis_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right side: Results and plots (vertical split)
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=1)

        # Top right: Results text
        results_frame = ttk.LabelFrame(right_paned, text="Analysis Results", padding=5)
        right_paned.add(results_frame, weight=0)

        # Bottom right: Plots
        plot_frame = ttk.LabelFrame(right_paned, text="Visualization", padding=5)
        right_paned.add(plot_frame, weight=1)

        # Setup all sections
        self.setup_data_loading(filters_scrollable_frame)
        self.setup_filters(filters_scrollable_frame)
        self.setup_analysis_controls(analysis_scrollable_frame)
        self.setup_results_display(results_frame)
        self.setup_plot_area(plot_frame)

    def setup_data_loading(self, parent):
        """Setup data loading controls"""
        frame = ttk.LabelFrame(parent, text="Data Source", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)

        # File path display
        self.file_path_var = tk.StringVar(value="No file loaded")
        file_label = ttk.Label(frame, textvariable=self.file_path_var,
                               wraplength=200, relief=tk.SUNKEN, padding=5)
        file_label.pack(fill=tk.X, pady=(0, 5))

        # Browse button
        browse_btn = ttk.Button(frame, text="Browse .mat File",
                                command=self.browse_file)
        browse_btn.pack(fill=tk.X, pady=2)

        # Load button
        self.load_btn = ttk.Button(frame, text="Load Data",
                                   command=self.load_data, state=tk.DISABLED)
        self.load_btn.pack(fill=tk.X, pady=2)

        # Status indicator
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(frame, textvariable=self.status_var,
                                 foreground="gray")
        status_label.pack(pady=(5, 0))

    def setup_filters(self, parent):
        """Setup data filtering controls"""
        # Time Range Filter
        time_frame = ttk.LabelFrame(parent, text="Time Range (s)", padding=5)
        time_frame.pack(fill=tk.X, pady=5)

        ttk.Label(time_frame, text="Start:").grid(row=0, column=0, sticky=tk.W)
        self.time_start = ttk.Entry(time_frame, width=10)
        self.time_start.grid(row=0, column=1, padx=5)
        self.time_start.insert(0, "900")

        ttk.Label(time_frame, text="End:").grid(row=1, column=0, sticky=tk.W)
        self.time_end = ttk.Entry(time_frame, width=10)
        self.time_end.grid(row=1, column=1, padx=5)
        self.time_end.insert(0, "1250")

        # Normal Load Filter
        fz_frame = ttk.LabelFrame(parent, text="Normal Load (N)", padding=5)
        fz_frame.pack(fill=tk.X, pady=5)

        self.fz_filter_type = tk.StringVar(value="all")
        ttk.Radiobutton(fz_frame, text="All", variable=self.fz_filter_type,
                        value="all").pack(anchor=tk.W)
        ttk.Radiobutton(fz_frame, text="Range", variable=self.fz_filter_type,
                        value="range").pack(anchor=tk.W)

        range_frame = ttk.Frame(fz_frame)
        range_frame.pack(fill=tk.X, padx=20)
        ttk.Label(range_frame, text="Min:").grid(row=0, column=0, sticky=tk.W)
        self.fz_min = ttk.Entry(range_frame, width=10)
        self.fz_min.grid(row=0, column=1, padx=5)
        self.fz_min.insert(0, "-1600")

        ttk.Label(range_frame, text="Max:").grid(row=1, column=0, sticky=tk.W)
        self.fz_max = ttk.Entry(range_frame, width=10)
        self.fz_max.grid(row=1, column=1, padx=5)
        self.fz_max.insert(0, "-200")

        # Slip Angle Filter
        sa_frame = ttk.LabelFrame(parent, text="Slip Angle (deg)", padding=5)
        sa_frame.pack(fill=tk.X, pady=5)

        self.sa_filter_type = tk.StringVar(value="all")
        ttk.Radiobutton(sa_frame, text="All", variable=self.sa_filter_type,
                        value="all").pack(anchor=tk.W)
        ttk.Radiobutton(sa_frame, text="Range", variable=self.sa_filter_type,
                        value="range").pack(anchor=tk.W)

        range_frame = ttk.Frame(sa_frame)
        range_frame.pack(fill=tk.X, padx=20)
        ttk.Label(range_frame, text="Min:").grid(row=0, column=0, sticky=tk.W)
        self.sa_min = ttk.Entry(range_frame, width=10)
        self.sa_min.grid(row=0, column=1, padx=5)
        self.sa_min.insert(0, "-12")

        ttk.Label(range_frame, text="Max:").grid(row=1, column=0, sticky=tk.W)
        self.sa_max = ttk.Entry(range_frame, width=10)
        self.sa_max.grid(row=1, column=1, padx=5)
        self.sa_max.insert(0, "12")

        # Pressure Filter
        p_frame = ttk.LabelFrame(parent, text="Pressure (psi)", padding=5)
        p_frame.pack(fill=tk.X, pady=5)

        self.p_filter_type = tk.StringVar(value="all")
        ttk.Radiobutton(p_frame, text="All", variable=self.p_filter_type,
                        value="all").pack(anchor=tk.W)
        ttk.Radiobutton(p_frame, text="Specific", variable=self.p_filter_type,
                        value="specific").pack(anchor=tk.W)

        p_options_frame = ttk.Frame(p_frame)
        p_options_frame.pack(fill=tk.X, padx=20)
        self.p_specific = ttk.Combobox(p_options_frame, width=10,
                                       values=["10", "12", "14", "16"])
        self.p_specific.pack()
        self.p_specific.set("12")

        # Apply filters button
        ttk.Button(parent, text="Apply Filters",
                   command=self.apply_filters).pack(fill=tk.X, pady=10)

    def setup_analysis_controls(self, parent):
        """Setup analysis control buttons"""
        frame = ttk.LabelFrame(parent, text="Analysis", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)

        # Pacejka model fitting
        ttk.Label(frame, text="Pacejka Model Fitting:").pack(anchor=tk.W, pady=(0, 5))

        # Initial parameters frame
        param_frame = ttk.LabelFrame(frame, text="Initial Parameters", padding=5)
        param_frame.pack(fill=tk.X, pady=5)

        # D1, D2, B, C parameters
        params = [("D1:", "0.0817"), ("D2:", "-0.5734"),
                  ("B:", "-0.5681"), ("C:", "-0.1447")]

        self.param_entries = {}
        for i, (label, default) in enumerate(params):
            ttk.Label(param_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=2)
            entry = ttk.Entry(param_frame, width=10)
            entry.grid(row=i, column=1, padx=5)
            entry.insert(0, default)
            self.param_entries[label[:-1]] = entry

        # Analysis type
        self.analysis_type = tk.StringVar(value="fy")
        ttk.Radiobutton(frame, text="Lateral Force (FY)",
                        variable=self.analysis_type, value="fy").pack(anchor=tk.W)
        ttk.Radiobutton(frame, text="Longitudinal Force (FX)",
                        variable=self.analysis_type, value="fx").pack(anchor=tk.W)

        # Fit button
        ttk.Button(frame, text="Fit Pacejka Model",
                   command=self.fit_model).pack(fill=tk.X, pady=5)

        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Find optimum section
        opt_frame = ttk.LabelFrame(frame, text="Find Optimum", padding=5)
        opt_frame.pack(fill=tk.X, pady=5)

        ttk.Label(opt_frame, text="Target FZ (N):").pack(anchor=tk.W)
        self.target_fz = ttk.Entry(opt_frame, width=10)
        self.target_fz.pack(fill=tk.X, pady=2)
        self.target_fz.insert(0, "-613")

        ttk.Button(opt_frame, text="Find Max Lateral Force",
                   command=self.find_max_force).pack(fill=tk.X, pady=2)

    def setup_results_display(self, parent):
        """Setup results text display"""
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text widget
        self.results_text = tk.Text(parent, height=12, wrap=tk.WORD,
                                    yscrollcommand=scrollbar.set, font=("Courier", 9))
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)

        # Initial text
        default_text = """FSAE Tire Analysis Tool

1. Load tire test data (.mat file)
2. Apply filters to select desired conditions
3. Fit Pacejka model to data
4. Find optimal operating conditions

Results will appear here.
"""
        self.results_text.insert(tk.END, default_text)
        self.results_text.configure(state=tk.DISABLED)

    def setup_plot_area(self, parent):
        """Setup matplotlib plot area"""
        # Create notebook for multiple plot types
        self.plot_notebook = ttk.Notebook(parent)
        self.plot_notebook.pack(fill=tk.BOTH, expand=True)

        # 3D Surface Plot
        surface_frame = ttk.Frame(self.plot_notebook)
        self.plot_notebook.add(surface_frame, text="3D Surface")

        self.fig_3d = Figure(figsize=(8, 6), dpi=100)
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        self.canvas_3d = FigureCanvasTkAgg(self.fig_3d, master=surface_frame)
        self.canvas_3d.draw()
        self.canvas_3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar_frame_3d = ttk.Frame(surface_frame)
        toolbar_frame_3d.pack(side=tk.BOTTOM, fill=tk.X)
        NavigationToolbar2Tk(self.canvas_3d, toolbar_frame_3d)

        # 2D Plot (FY vs SA)
        plot_2d_frame = ttk.Frame(self.plot_notebook)
        self.plot_notebook.add(plot_2d_frame, text="FY vs SA")

        self.fig_2d = Figure(figsize=(8, 6), dpi=100)
        self.ax_2d = self.fig_2d.add_subplot(111)
        self.canvas_2d = FigureCanvasTkAgg(self.fig_2d, master=plot_2d_frame)
        self.canvas_2d.draw()
        self.canvas_2d.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar_frame_2d = ttk.Frame(plot_2d_frame)
        toolbar_frame_2d.pack(side=tk.BOTTOM, fill=tk.X)
        NavigationToolbar2Tk(self.canvas_2d, toolbar_frame_2d)

        # Initial empty plots
        self.clear_all_plots()

    def browse_file(self):
        """Browse for .mat file"""
        filename = filedialog.askopenfilename(
            title="Select FSAE TTC Data File",
            filetypes=[("MATLAB files", "*.mat"), ("All files", "*.*")]
        )

        if filename:
            self.current_file = filename
            self.file_path_var.set(filename.split('/')[-1])
            self.load_btn.config(state=tk.NORMAL)
            self.status_var.set("File selected - Click Load Data")

    def load_data(self):
        """Load data from .mat file"""
        if not self.current_file:
            messagebox.showerror("Error", "No file selected")
            return

        try:
            self.status_var.set("Loading...")
            self.tire_frame.update()

            # Load MATLAB file
            data = loadmat(self.current_file)

            # Extract variables
            self.raw_data = {
                'ET': data['ET'].flatten(),
                'SA': data['SA'].flatten(),
                'FZ': data['FZ'].flatten(),
                'FY': data['FY'].flatten(),
                'FX': data['FX'].flatten(),
                'P': data['P'].flatten() * 0.145038,  # kPa to psi
                'V': data['V'].flatten(),
                'IA': data['IA'].flatten() if 'IA' in data else None
            }

            n_points = len(self.raw_data['ET'])
            self.status_var.set(f"Loaded {n_points} data points")

            self.update_results(f"""Data Loaded Successfully!

File: {self.current_file.split('/')[-1]}
Total points: {n_points}

Data ranges:
  Time: {self.raw_data['ET'].min():.1f} - {self.raw_data['ET'].max():.1f} s
  Slip Angle: {self.raw_data['SA'].min():.1f} - {self.raw_data['SA'].max():.1f} deg
  Normal Load: {self.raw_data['FZ'].min():.1f} - {self.raw_data['FZ'].max():.1f} N
  Pressure: {self.raw_data['P'].min():.1f} - {self.raw_data['P'].max():.1f} psi
  Velocity: {self.raw_data['V'].min():.1f} - {self.raw_data['V'].max():.1f} mph

Apply filters to select data subset for analysis.
""")

        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")
            self.status_var.set("Error loading data")

    def apply_filters(self):
        """Apply filters to raw data"""
        if self.raw_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return

        try:
            # Start with all data
            idx = np.ones(len(self.raw_data['ET']), dtype=bool)

            # Time filter
            t_start = float(self.time_start.get())
            t_end = float(self.time_end.get())
            idx &= (self.raw_data['ET'] >= t_start) & (self.raw_data['ET'] <= t_end)

            # Normal load filter
            if self.fz_filter_type.get() == "range":
                fz_min = float(self.fz_min.get())
                fz_max = float(self.fz_max.get())
                idx &= (self.raw_data['FZ'] >= fz_min) & (self.raw_data['FZ'] <= fz_max)

            # Slip angle filter
            if self.sa_filter_type.get() == "range":
                sa_min = float(self.sa_min.get())
                sa_max = float(self.sa_max.get())
                idx &= (self.raw_data['SA'] >= sa_min) & (self.raw_data['SA'] <= sa_max)

            # Pressure filter
            if self.p_filter_type.get() == "specific":
                p_target = float(self.p_specific.get())
                # Allow ±0.5 psi tolerance
                idx &= np.abs(self.raw_data['P'] - p_target) < 0.5

            # Apply filters
            self.filtered_data = {key: val[idx] for key, val in self.raw_data.items()}

            n_filtered = idx.sum()
            self.status_var.set(f"Filtered: {n_filtered} points")

            self.update_results(f"""Filters Applied!

Selected {n_filtered} points from {len(self.raw_data['ET'])} total

Filtered data ranges:
  Time: {self.filtered_data['ET'].min():.1f} - {self.filtered_data['ET'].max():.1f} s
  Slip Angle: {self.filtered_data['SA'].min():.1f} - {self.filtered_data['SA'].max():.1f} deg
  Normal Load: {self.filtered_data['FZ'].min():.1f} - {self.filtered_data['FZ'].max():.1f} N
  Pressure: {self.filtered_data['P'].min():.1f} - {self.filtered_data['P'].max():.1f} psi

Ready for Pacejka model fitting.
""")

        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")
            messagebox.showerror("Error", f"Failed to apply filters:\n{str(e)}")

    def fit_model(self):
        """Fit Pacejka model to filtered data"""
        if self.filtered_data is None:
            messagebox.showwarning("Warning", "No filtered data available")
            return

        try:
            from src.calculations.tire_model import PacejkaTireModel

            self.status_var.set("Fitting model...")
            self.tire_frame.update()

            # Get initial parameters
            initial_guess = [
                float(self.param_entries['D1'].get()),
                float(self.param_entries['D2'].get()),
                float(self.param_entries['B'].get()),
                float(self.param_entries['C'].get())
            ]

            # Initialize model
            self.tire_model = PacejkaTireModel()

            # Fit based on analysis type
            if self.analysis_type.get() == "fy":
                results = self.tire_model.fit_tire_data(
                    self.filtered_data['SA'],
                    self.filtered_data['FZ'],
                    self.filtered_data['FY'],
                    initial_guess=initial_guess
                )
                force_type = "Lateral"
            else:
                results = self.tire_model.fit_tire_data(
                    self.filtered_data['SA'],
                    self.filtered_data['FZ'],
                    self.filtered_data['FX'],
                    initial_guess=initial_guess
                )
                force_type = "Longitudinal"

            # Display results
            params = results['FY_params']
            resnorm = results['FY_resnorm']

            self.update_results(f"""Pacejka Model Fitted!

{force_type} Force Parameters:
  D1 = {params[0]:10.6f}
  D2 = {params[1]:10.6f}
  B  = {params[2]:10.6f}
  C  = {params[3]:10.6f}

Residual Norm: {resnorm:12.2f}

Model equation:
  D = (D1 + D2/1000 * FZ) * FZ
  F = D * sin(C * arctan(B * SA))

Use 'Find Max Lateral Force' to find optimal conditions.
""")

            self.status_var.set("Model fitted successfully")

            # Generate and plot surface
            self.plot_fitted_surface()

        except Exception as e:
            self.logger.error(f"Error fitting model: {e}")
            messagebox.showerror("Error", f"Failed to fit model:\n{str(e)}")
            self.status_var.set("Error fitting model")

    def find_max_force(self):
        """Find maximum lateral force at target vertical load"""
        if self.tire_model is None or self.tire_model.FY_params is None:
            messagebox.showwarning("Warning", "Fit model first")
            return

        try:
            target_fz = float(self.target_fz.get())

            results = self.tire_model.find_max_lateral_force(target_fz)

            self.update_results(f"""Maximum Lateral Force Analysis

Target Vertical Load: {results['target_vertical_load']:8.2f} N

Results:
  Max Lateral Force: {results['max_lateral_force']:8.2f} N
  Optimal Slip Angle: {results['optimal_slip_angle']:8.2f} degrees

Friction Coefficient: {abs(results['max_lateral_force'] / results['target_vertical_load']):.3f}

This represents the peak cornering grip available at this load.
""")

            # Plot FY vs SA at this load
            self.plot_fy_vs_sa(results)

        except Exception as e:
            self.logger.error(f"Error finding max force: {e}")
            messagebox.showerror("Error", f"Failed to find max force:\n{str(e)}")

    def plot_fitted_surface(self):
        """Plot 3D surface of fitted model"""
        try:
            surface_data = self.tire_model.generate_surface()

            self.ax_3d.clear()

            # Plot raw data
            if self.filtered_data is not None:
                self.ax_3d.scatter(self.filtered_data['SA'],
                                   self.filtered_data['FZ'],
                                   self.filtered_data['FY'],
                                   c='k', s=1, alpha=0.3, label='Raw Data')

            # Plot surface
            surf = self.ax_3d.plot_surface(surface_data['SA_grid'],
                                           surface_data['FZ_grid'],
                                           surface_data['FY_surface'],
                                           cmap='viridis', alpha=0.8)

            self.ax_3d.set_xlabel('Slip Angle [deg]')
            self.ax_3d.set_ylabel('Normal Load [N]')
            self.ax_3d.set_zlabel('Lateral Force [N]')
            self.ax_3d.set_title('Pacejka Model - Lateral Force')
            self.fig_3d.colorbar(surf, ax=self.ax_3d, shrink=0.5)

            self.fig_3d.tight_layout()
            self.canvas_3d.draw()

        except Exception as e:
            self.logger.error(f"Error plotting surface: {e}")

    def plot_fy_vs_sa(self, max_force_results):
        """Plot FY vs SA at target vertical load"""
        try:
            self.ax_2d.clear()

            sa = max_force_results['sa_array']
            fy = max_force_results['fy_array']

            self.ax_2d.plot(sa, fy, 'b-', linewidth=2, label='Fitted Model')
            self.ax_2d.axvline(max_force_results['optimal_slip_angle'],
                               color='r', linestyle='--',
                               label=f"Optimal SA = {max_force_results['optimal_slip_angle']:.2f}°")
            self.ax_2d.axhline(max_force_results['max_lateral_force'],
                               color='g', linestyle='--',
                               label=f"Max FY = {max_force_results['max_lateral_force']:.0f} N")

            self.ax_2d.set_xlabel('Slip Angle [deg]')
            self.ax_2d.set_ylabel('Lateral Force [N]')
            self.ax_2d.set_title(
                f"Lateral Force vs Slip Angle (FZ = {max_force_results['target_vertical_load']:.0f} N)")
            self.ax_2d.grid(True, alpha=0.3)
            self.ax_2d.legend()

            self.fig_2d.tight_layout()
            self.canvas_2d.draw()

        except Exception as e:
            self.logger.error(f"Error plotting 2D: {e}")

    def clear_all_plots(self):
        """Clear all plots"""
        self.ax_3d.clear()
        self.ax_3d.text(0.5, 0.5, 0.5, 'Load and fit tire data\nto see 3D surface',
                        ha='center', va='center', transform=self.ax_3d.transAxes)
        self.ax_3d.set_axis_off()
        self.canvas_3d.draw()

        self.ax_2d.clear()
        self.ax_2d.text(0.5, 0.5, 'Results will appear here',
                        ha='center', va='center', transform=self.ax_2d.transAxes,
                        fontsize=14, color='gray')
        self.ax_2d.set_axis_off()
        self.canvas_2d.draw()

    def update_results(self, text):
        """Update results text area"""
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.configure(state=tk.DISABLED)