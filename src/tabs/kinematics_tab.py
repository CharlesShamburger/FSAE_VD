import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import logging


class KinematicsTab:
    def __init__(self, parent_notebook, basic_data, pushrod_data, basic_members, pushrod_members):
        self.basic_data = basic_data
        self.pushrod_data = pushrod_data
        self.basic_members = basic_members
        self.pushrod_members = pushrod_members

        # Setup logging
        self.logger = logging.getLogger(__name__)

        self.kinematics_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.kinematics_frame, text="Kinematics")

        # Create main layout (vertical split)
        kinematics_paned = ttk.PanedWindow(self.kinematics_frame, orient=tk.VERTICAL)
        kinematics_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top section: Controls and results
        top_frame = ttk.Frame(kinematics_paned)
        kinematics_paned.add(top_frame, weight=0)

        # Bottom section: Analysis plot only
        plot_frame = ttk.LabelFrame(kinematics_paned, text="Analysis Results", padding=5)
        kinematics_paned.add(plot_frame, weight=1)

        # Setup sections
        self.setup_controls(top_frame)
        self.setup_analysis_plot(plot_frame)

    def setup_controls(self, parent):
        """Setup control panel for kinematics analysis"""
        # Create horizontal layout for controls and results
        main_control_frame = ttk.Frame(parent)
        main_control_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Input controls
        input_frame = ttk.LabelFrame(main_control_frame, text="Analysis Parameters", padding=10)
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        # Suspension selection
        ttk.Label(input_frame, text="Suspension Type:").pack(anchor=tk.W, pady=5)
        self.suspension_type = tk.StringVar(value="pushrod")
        ttk.Radiobutton(input_frame, text="Basic Suspension",
                        variable=self.suspension_type, value="basic").pack(anchor=tk.W)
        ttk.Radiobutton(input_frame, text="Pushrod Suspension",
                        variable=self.suspension_type, value="pushrod").pack(anchor=tk.W)

        # Separator
        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Travel range inputs
        ttk.Label(input_frame, text="Travel Range (mm):").pack(anchor=tk.W, pady=5)

        travel_frame = ttk.Frame(input_frame)
        travel_frame.pack(fill=tk.X, pady=5)

        ttk.Label(travel_frame, text="From:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.travel_min = ttk.Entry(travel_frame, width=8)
        self.travel_min.grid(row=0, column=1, padx=(0, 10))
        self.travel_min.insert(0, "-25")

        ttk.Label(travel_frame, text="To:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.travel_max = ttk.Entry(travel_frame, width=8)
        self.travel_max.grid(row=0, column=3)
        self.travel_max.insert(0, "75")

        ttk.Label(input_frame, text="Step size (mm):").pack(anchor=tk.W, pady=(10, 5))
        self.travel_step = ttk.Entry(input_frame, width=8)
        self.travel_step.pack(anchor=tk.W)
        self.travel_step.insert(0, "5")

        # Placeholder for calculation buttons
        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(input_frame, text="Calculations:").pack(anchor=tk.W, pady=5)

        # Add your calculation buttons here as you implement them
        placeholder_label = ttk.Label(input_frame,
                                      text="Calculation buttons will go here",
                                      foreground='gray')
        placeholder_label.pack(pady=20)

        # Right side: Results display
        results_frame = ttk.LabelFrame(main_control_frame, text="Results", padding=10)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Create text widget for results
        result_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text = tk.Text(results_frame, height=15, wrap=tk.WORD,
                                    yscrollcommand=result_scroll.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scroll.config(command=self.results_text.yview)

        # Default content
        default_text = """FSAE Kinematics Analysis

Select suspension type and travel range above.

Calculation results will appear here.
"""
        self.results_text.insert(tk.END, default_text)
        self.results_text.configure(state=tk.DISABLED)

    def setup_analysis_plot(self, parent):
        """Setup analysis results plot"""
        # Create matplotlib figure for analysis plots
        self.analysis_fig = Figure(figsize=(10, 5), dpi=100)
        self.analysis_ax = self.analysis_fig.add_subplot(111)

        # Embed in tkinter
        self.analysis_canvas = FigureCanvasTkAgg(self.analysis_fig, master=parent)
        self.analysis_canvas.draw()
        self.analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add toolbar
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        toolbar = NavigationToolbar2Tk(self.analysis_canvas, toolbar_frame)
        toolbar.update()

        # Initial empty plot
        self.analysis_ax.text(0.5, 0.5, 'Analysis results will appear here',
                              ha='center', va='center', transform=self.analysis_ax.transAxes,
                              fontsize=14, color='gray')
        self.analysis_ax.set_axis_off()
        self.analysis_canvas.draw()

    # Utility methods for your future calculations
    def update_results(self, text: str):
        """Update the results text area"""
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.configure(state=tk.DISABLED)

    def plot_analysis(self, x_data, y_data, xlabel, ylabel, title):
        """Helper method to plot analysis results"""
        self.analysis_ax.clear()
        self.analysis_ax.set_axis_on()
        self.analysis_ax.plot(x_data, y_data, 'bo-', linewidth=2, markersize=6)
        self.analysis_ax.set_xlabel(xlabel)
        self.analysis_ax.set_ylabel(ylabel)
        self.analysis_ax.set_title(title)
        self.analysis_ax.grid(True, alpha=0.3)
        self.analysis_fig.tight_layout()
        self.analysis_canvas.draw()

    def clear_plot(self):
        """Clear the analysis plot"""
        self.analysis_ax.clear()
        self.analysis_ax.text(0.5, 0.5, 'Analysis results will appear here',
                              ha='center', va='center', transform=self.analysis_ax.transAxes,
                              fontsize=14, color='gray')
        self.analysis_ax.set_axis_off()
        self.analysis_canvas.draw()

    # Add your calculation methods here as you implement them
    # Example structure:
    # def calculate_motion_ratio(self):
    #     """Calculate motion ratio"""
    #     try:
    #         travel_min = float(self.travel_min.get())
    #         travel_max = float(self.travel_max.get())
    #         step = float(self.travel_step.get())
    #
    #         # Your calculation code here
    #
    #         # Update results text
    #         self.update_results("Results text here")
    #
    #         # Plot the data
    #         self.plot_analysis(x_data, y_data, "X Label", "Y Label", "Plot Title")
    #     except Exception as e:
    #         self.logger.error(f"Error: {e}")
    #         self.update_results(f"Error: {e}")