import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import logging
import numpy as np
from ..calculations.motion_ratio_calculator import MotionRatioCalculator


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

        # Shock travel range inputs (for motion ratio)
        ttk.Label(input_frame, text="Shock Travel Range (in):").pack(anchor=tk.W, pady=(10, 5))

        shock_travel_frame = ttk.Frame(input_frame)
        shock_travel_frame.pack(fill=tk.X, pady=5)

        ttk.Label(shock_travel_frame, text="From:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.shock_min = ttk.Entry(shock_travel_frame, width=8)
        self.shock_min.grid(row=0, column=1, padx=(0, 10))
        self.shock_min.insert(0, "-1.5")

        ttk.Label(shock_travel_frame, text="To:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.shock_max = ttk.Entry(shock_travel_frame, width=8)
        self.shock_max.grid(row=0, column=3)
        self.shock_max.insert(0, "1.5")

        ttk.Label(input_frame, text="Shock step size (in):").pack(anchor=tk.W, pady=(10, 5))
        self.shock_step = ttk.Entry(input_frame, width=8)
        self.shock_step.pack(anchor=tk.W)
        self.shock_step.insert(0, "0.1")

        # Placeholder for calculation buttons
        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(input_frame, text="Calculations:").pack(anchor=tk.W, pady=5)

        # Add calculation buttons
        self.motion_ratio_btn = ttk.Button(input_frame, text="Calculate Motion Ratio",
                                           command=self.calculate_motion_ratio)
        self.motion_ratio_btn.pack(pady=5)

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

    def get_2d_points(self, suspension_type='pushrod'):
        """
        Calculate 2D Y-Z projections for kinematics analysis.
        Returns a dictionary of 2D points (Y, Z) for the specified suspension.

        Args:
            suspension_type: 'basic' or 'pushrod'

        Returns:
            dict: Dictionary with point names as keys and [Y, Z] arrays as values
        """
        if suspension_type == 'basic':
            data = self.basic_data
            # Column indices for basic suspension
            points = {
                'UCA_IN': self._calculate_effective_point(data, [0, 1]),  # Average of front and rear UCA inboard
                'LCA_IN': self._calculate_effective_point(data, [2, 3]),  # Average of front and rear LCA inboard
                'PushRodIN': np.array([data[1, 4], data[2, 4]]),
                'UCA_OUT': np.array([data[1, 5], data[2, 5]]),
                'LCA_OUT': np.array([data[1, 6], data[2, 6]]),
                'PushRodOUT': np.array([data[1, 7], data[2, 7]]),
                'Wheel_center': np.array([data[1, 8], data[2, 8]])
            }
        else:  # pushrod
            data = self.pushrod_data
            # Column indices for pushrod suspension
            points = {
                'UCA_IN': self._calculate_effective_point(data, [0, 1]),  # Average of front and rear UCA inboard
                'LCA_IN': self._calculate_effective_point(data, [2, 3]),  # Average of front and rear LCA inboard
                'PushRodIN': np.array([data[1, 4], data[2, 4]]),
                'UCA_OUT': np.array([data[1, 5], data[2, 5]]),
                'LCA_OUT': np.array([data[1, 6], data[2, 6]]),
                'PushRodOUT': np.array([data[1, 7], data[2, 7]]),
                'Cam_Hinge': np.array([data[1, 8], data[2, 8]]),
                'Shock_OUT': np.array([data[1, 9], data[2, 9]]),
                'Shock_IN': np.array([data[1, 10], data[2, 10]]),
                'Wheel_center': np.array([data[1, 11], data[2, 11]])
            }

        return points

    def _calculate_effective_point(self, data, indices):
        """
        Calculate effective 2D point for control arms that have front and rear mounts.
        Uses centroid of the mounting points projected onto Y-Z plane.

        Args:
            data: 3D coordinate array (3 x N)
            indices: list of column indices to average (e.g., [0, 1] for front and rear UCA)

        Returns:
            np.array: [Y, Z] coordinates
        """
        # Average the Y and Z coordinates
        y_avg = np.mean([data[1, i] for i in indices])
        z_avg = np.mean([data[2, i] for i in indices])

        return np.array([y_avg, z_avg])

    def calculate_motion_ratio(self):
        """Calculate motion ratio using 2D geometry"""
        try:
            # Get shock travel parameters
            shock_min = float(self.shock_min.get())
            shock_max = float(self.shock_max.get())
            shock_step = float(self.shock_step.get())

            # Get suspension type
            suspension_type = self.suspension_type.get()

            # Get 2D points
            points = self.get_2d_points(suspension_type)

            # Use the calculator
            calculator = MotionRatioCalculator()
            results = calculator.calculate_motion_ratio(shock_min, shock_max, shock_step, points)

            avg_motion_ratio = results['avg_motion_ratio']
            shock_displacements = results['shock_displacements']
            wheel_displacements = results['wheel_displacements']
            motion_ratio = results['motion_ratio']
            wheel_travel_mid = results['wheel_travel_mid']
            shock_step = results['shock_step']

            # Update results text
            results_text = f"""Motion Ratio Analysis

Average Motion Ratio = {avg_motion_ratio:.3f} (shock travel / wheel travel)
Interpretation: Shock moves {avg_motion_ratio:.3f} inches for every 1 inch of wheel travel
HIGHER number = MORE shock travel = stiffer feeling suspension
LOWER number = LESS shock travel = softer feeling suspension

Shock travel range: {shock_displacements[0]:.3f} to {shock_displacements[-1]:.3f} in
Wheel travel range: {wheel_displacements[0]:.3f} to {wheel_displacements[-1]:.3f} in
Motion ratio range: {motion_ratio.min():.3f} to {motion_ratio.max():.3f}

Number of points: {len(shock_displacements)}
Step size: {shock_step:.3f}
"""
            self.update_results(results_text)

            # Plot motion ratio vs wheel travel
            self.analysis_ax.clear()
            self.analysis_ax.set_axis_on()
            self.analysis_ax.plot(wheel_travel_mid, motion_ratio, 'b-', linewidth=2, label='Motion Ratio')
            self.analysis_ax.axhline(y=avg_motion_ratio, color='r', linestyle='--', linewidth=1.5,
                                    label=f'Avg = {avg_motion_ratio:.3f}')
            self.analysis_ax.grid(True)
            self.analysis_ax.set_xlabel('Wheel Vertical Travel (in)')
            self.analysis_ax.set_ylabel('Motion Ratio (shock travel / wheel travel)')
            self.analysis_ax.set_title('Motion Ratio vs Wheel Travel')
            self.analysis_ax.legend()

            # Add text box
            textstr = f'Avg MR = {avg_motion_ratio:.3f}\nHigher MR → More shock travel\nLower MR → Less shock travel'
            props = dict(boxstyle='round', facecolor='white', edgecolor='black', alpha=0.8)
            self.analysis_ax.text(0.05, 0.95, textstr, transform=self.analysis_ax.transAxes, fontsize=10,
                                 verticalalignment='top', bbox=props)

            self.analysis_fig.tight_layout()
            self.analysis_canvas.draw()

        except Exception as e:
            self.logger.error(f"Error in motion ratio calculation: {e}")
            self.update_results(f"Error: {e}")
            self.clear_plot()

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