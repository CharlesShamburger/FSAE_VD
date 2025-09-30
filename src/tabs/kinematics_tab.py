import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from src.utils.plotting import PlottingUtils
import numpy as np
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

        # Top section: Controls and calculations
        top_frame = ttk.Frame(kinematics_paned)
        kinematics_paned.add(top_frame, weight=0)

        # Bottom section: Graph
        graph_frame = ttk.LabelFrame(kinematics_paned, text="Analysis Results", padding=5)
        kinematics_paned.add(graph_frame, weight=1)

        # Setup sections
        self.setup_kinematics_controls(top_frame)
        self.setup_kinematics_graph(graph_frame)

    def setup_kinematics_controls(self, parent):
        """Setup kinematics analysis controls and results"""
        # Create horizontal layout for controls and results
        main_control_frame = ttk.Frame(parent)
        main_control_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Input controls
        input_frame = ttk.LabelFrame(main_control_frame, text="Analysis Parameters", padding=10)
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        # Suspension selection
        ttk.Label(input_frame, text="Suspension Type:").pack(anchor=tk.W, pady=5)
        self.kinematics_suspension = tk.StringVar(value="pushrod")
        ttk.Radiobutton(input_frame, text="Basic Suspension",
                        variable=self.kinematics_suspension, value="basic").pack(anchor=tk.W)
        ttk.Radiobutton(input_frame, text="Pushrod Suspension",
                        variable=self.kinematics_suspension, value="pushrod").pack(anchor=tk.W)

        # Separator
        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Travel range inputs
        ttk.Label(input_frame, text="Wheel Travel Range (mm):").pack(anchor=tk.W, pady=5)

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

        # Calculation buttons
        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(input_frame, text="Calculations:").pack(anchor=tk.W, pady=5)

        ttk.Button(input_frame, text="Motion Ratio",
                   command=self.calculate_motion_ratio).pack(fill=tk.X, pady=2)
        ttk.Button(input_frame, text="Camber Curve",
                   command=self.calculate_camber_curve, state=tk.DISABLED).pack(fill=tk.X, pady=2)
        ttk.Button(input_frame, text="Roll Center Height",
                   command=self.calculate_roll_center).pack(fill=tk.X, pady=2)

        # Right side: Results display
        results_frame = ttk.LabelFrame(main_control_frame, text="Calculation Results", padding=10)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Create text widget for results
        self.kinematics_results = tk.Text(results_frame, height=15, wrap=tk.WORD)
        results_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL,
                                       command=self.kinematics_results.yview)

        self.kinematics_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.kinematics_results.configure(yscrollcommand=results_scroll.set)

        # Default content
        default_text = """FSAE Kinematics Analysis

Select suspension type and travel range, then click a calculation button.

Motion Ratio: Calculates the ratio of wheel movement to shock/spring movement

Camber Curve: Shows how camber angle changes with suspension travel

Roll Center Height: Determines the instantaneous center of roll rotation

Results will appear here after running calculations."""

        self.kinematics_results.insert(tk.END, default_text)
        self.kinematics_results.configure(state=tk.DISABLED)

    def setup_kinematics_graph(self, parent):
        """Setup the kinematics analysis graph and geometry viewer"""
        # Create notebook for bottom section tabs
        self.kinematics_notebook = ttk.Notebook(parent)
        self.kinematics_notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Analysis Results (graphs/charts)
        results_frame = ttk.Frame(self.kinematics_notebook)
        self.kinematics_notebook.add(results_frame, text="Analysis Results")

        # Tab 2: Geometry Viewer (3D interactive)
        geometry_frame = ttk.Frame(self.kinematics_notebook)
        self.kinematics_notebook.add(geometry_frame, text="Geometry View")

        # Setup analysis results graph
        self.setup_analysis_graph(results_frame)

        # Setup geometry viewer using the existing PlottingUtils class
        self.setup_kinematics_geometry(geometry_frame)

    def setup_analysis_graph(self, parent):
        """Setup the analysis results graph"""
        # Create control frame for graph options
        graph_control_frame = ttk.Frame(parent)
        graph_control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # Save plot button
        ttk.Button(graph_control_frame, text="Save Plot",
                   command=self.save_kinematics_plot).pack(side=tk.LEFT, padx=(0, 5))

        # Reset view button
        ttk.Button(graph_control_frame, text="Reset View",
                   command=self.reset_kinematics_view).pack(side=tk.LEFT, padx=(0, 10))

        # Grid toggle
        self.kinematics_grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(graph_control_frame, text="Show Grid",
                        variable=self.kinematics_grid_var,
                        command=self.toggle_kinematics_grid).pack(side=tk.LEFT, padx=(0, 10))

        # Axis limits controls
        ttk.Label(graph_control_frame, text="X Limits:").pack(side=tk.LEFT, padx=(10, 2))
        self.kinematics_xlim_min = ttk.Entry(graph_control_frame, width=6)
        self.kinematics_xlim_min.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Label(graph_control_frame, text="to").pack(side=tk.LEFT, padx=2)
        self.kinematics_xlim_max = ttk.Entry(graph_control_frame, width=6)
        self.kinematics_xlim_max.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(graph_control_frame, text="Y Limits:").pack(side=tk.LEFT, padx=(10, 2))
        self.kinematics_ylim_min = ttk.Entry(graph_control_frame, width=6)
        self.kinematics_ylim_min.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Label(graph_control_frame, text="to").pack(side=tk.LEFT, padx=2)
        self.kinematics_ylim_max = ttk.Entry(graph_control_frame, width=6)
        self.kinematics_ylim_max.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(graph_control_frame, text="Apply Limits",
                   command=self.apply_kinematics_limits).pack(side=tk.LEFT)

        # Create matplotlib figure - SMALLER SIZE
        self.kinematics_fig = Figure(figsize=(10, 5), dpi=100)
        self.kinematics_ax = self.kinematics_fig.add_subplot(111)

        # Embed in tkinter
        self.kinematics_canvas = FigureCanvasTkAgg(self.kinematics_fig, master=parent)
        self.kinematics_canvas.draw()
        self.kinematics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add toolbar - this goes AFTER the canvas
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        kinematics_toolbar = NavigationToolbar2Tk(self.kinematics_canvas, toolbar_frame)
        kinematics_toolbar.update()

        # Initial plot setup
        self.kinematics_ax.set_title("Kinematics Analysis Results")
        self.kinematics_ax.grid(True, alpha=0.3)
        self.kinematics_canvas.draw()

        # Enable mouse wheel zoom
        def on_scroll(event):
            if event.inaxes == self.kinematics_ax:
                xlim = self.kinematics_ax.get_xlim()
                ylim = self.kinematics_ax.get_ylim()

                xdata = event.xdata
                ydata = event.ydata

                zoom_factor = 1.2 if event.button == 'down' else 1 / 1.2

                x_range = (xlim[1] - xlim[0]) * zoom_factor
                y_range = (ylim[1] - ylim[0]) * zoom_factor

                self.kinematics_ax.set_xlim([xdata - x_range / 2, xdata + x_range / 2])
                self.kinematics_ax.set_ylim([ydata - y_range / 2, ydata + y_range / 2])

                self.kinematics_canvas.draw()

        self.kinematics_canvas.mpl_connect('scroll_event', on_scroll)

    def setup_kinematics_geometry(self, parent):
        """Setup 3D geometry viewer for kinematics tab using PlottingUtils"""
        # Create layout with controls on left, 3D plot on right
        geo_main_frame = ttk.Frame(parent)
        geo_main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Simple controls
        geo_control_frame = ttk.LabelFrame(geo_main_frame, text="View Controls", padding=10)
        geo_control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        # View control buttons
        ttk.Button(geo_control_frame, text="Top View",
                   command=self.set_kinematics_top_view).pack(fill=tk.X, pady=2)
        ttk.Button(geo_control_frame, text="Side View",
                   command=self.set_kinematics_side_view).pack(fill=tk.X, pady=2)
        ttk.Button(geo_control_frame, text="Isometric",
                   command=self.set_kinematics_iso_view).pack(fill=tk.X, pady=2)

        # Separator
        ttk.Separator(geo_control_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Display options
        ttk.Label(geo_control_frame, text="Display:").pack(anchor=tk.W)

        self.kin_show_basic = tk.BooleanVar(value=True)
        self.kin_show_pushrod = tk.BooleanVar(value=True)

        ttk.Checkbutton(geo_control_frame, text="Basic",
                        variable=self.kin_show_basic,
                        command=self.update_kinematics_geometry).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(geo_control_frame, text="Pushrod",
                        variable=self.kin_show_pushrod,
                        command=self.update_kinematics_geometry).pack(anchor=tk.W, pady=2)

        # Right side: 3D plot using PlottingUtils
        geo_plot_frame = ttk.Frame(geo_main_frame)
        geo_plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create PlottingUtils instance for kinematics geometry view
        self.kinematics_plotting = PlottingUtils(
            geo_plot_frame,
            self.basic_data,
            self.pushrod_data,
            self.basic_members,
            self.pushrod_members
        )

        # Set references for easy access
        self.kinematics_geo_ax = self.kinematics_plotting.ax
        self.kinematics_geo_canvas = self.kinematics_plotting.canvas

        # Initial plot with both suspensions visible
        self.update_kinematics_geometry()

    def update_kinematics_geometry(self):
        """Update the kinematics 3D geometry plot using PlottingUtils"""
        self.kinematics_plotting.update_plot(
            self.kin_show_basic.get(),
            self.kin_show_pushrod.get()
        )

    def set_kinematics_top_view(self):
        """Set top view for kinematics geometry"""
        self.kinematics_geo_ax.view_init(elev=90, azim=0)
        self.kinematics_geo_canvas.draw()

    def set_kinematics_side_view(self):
        """Set side view for kinematics geometry"""
        self.kinematics_geo_ax.view_init(elev=0, azim=0)
        self.kinematics_geo_canvas.draw()

    def set_kinematics_iso_view(self):
        """Set isometric view for kinematics geometry"""
        self.kinematics_geo_ax.view_init(elev=20, azim=45)
        self.kinematics_geo_canvas.draw()

    def save_kinematics_plot(self):
        """Save the current kinematics plot"""
        from tkinter import filedialog
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg"), ("All files", "*.*")]
            )
            if file_path:
                self.kinematics_fig.savefig(file_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Plot saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving plot: {e}")

    def reset_kinematics_view(self):
        """Reset the kinematics plot view to default"""
        try:
            self.kinematics_ax.autoscale()
            self.kinematics_fig.tight_layout()
            self.kinematics_canvas.draw()
            self.logger.info("Kinematics plot view reset")
        except Exception as e:
            self.logger.error(f"Error resetting view: {e}")

    def toggle_kinematics_grid(self):
        """Toggle grid visibility on kinematics plot"""
        try:
            self.kinematics_ax.grid(self.kinematics_grid_var.get(), alpha=0.3)
            self.kinematics_canvas.draw()
            self.logger.info(f"Grid {'enabled' if self.kinematics_grid_var.get() else 'disabled'}")
        except Exception as e:
            self.logger.error(f"Error toggling grid: {e}")

    def apply_kinematics_limits(self):
        """Apply custom axis limits to kinematics plot"""
        try:
            xlim_min = float(self.kinematics_xlim_min.get()) if self.kinematics_xlim_min.get() else None
            xlim_max = float(self.kinematics_xlim_max.get()) if self.kinematics_xlim_max.get() else None
            ylim_min = float(self.kinematics_ylim_min.get()) if self.kinematics_ylim_min.get() else None
            ylim_max = float(self.kinematics_ylim_max.get()) if self.kinematics_ylim_max.get() else None

            if xlim_min is not None and xlim_max is not None:
                self.kinematics_ax.set_xlim(xlim_min, xlim_max)
            if ylim_min is not None and ylim_max is not None:
                self.kinematics_ax.set_ylim(ylim_min, ylim_max)

            self.kinematics_fig.tight_layout()
            self.kinematics_canvas.draw()
            self.logger.info("Applied custom axis limits")
        except ValueError as e:
            self.logger.error(f"Invalid limit values: {e}")
        except Exception as e:
            self.logger.error(f"Error applying limits: {e}")

    def calculate_motion_ratio(self):
        """Calculate motion ratio through suspension travel"""
        try:
            travel_min = float(self.travel_min.get())
            travel_max = float(self.travel_max.get())
            step = float(self.travel_step.get())
            self.logger.info(f"Calculating motion ratio: suspension={self.kinematics_suspension.get()}, "
                             f"travel {travel_min} to {travel_max}, step {step}")

            if self.kinematics_suspension.get() == "basic":
                travel_vals, mr_vals = calculate_motion_ratio_basic(
                    self.basic_data,
                    travel_range=(travel_min, travel_max),
                    step=step
                )
            else:
                travel_vals, mr_vals = calculate_motion_ratio_pushrod(
                    self.pushrod_data,
                    travel_range=(travel_min, travel_max),
                    step=step
                )

            # Update results text box
            result_text = "Motion Ratio Results:\n"
            for t, m in zip(travel_vals, mr_vals):
                result_text += f"Travel {t:.1f} mm -> MR {m:.3f}\n"
            self.update_kinematics_results(result_text)

            # COMPLETELY RESET THE AXIS
            self.kinematics_ax.clear()
            self.kinematics_ax.set_aspect('auto')  # Reset aspect ratio

            # Plot results
            self.kinematics_ax.plot(travel_vals, mr_vals, marker="o", linewidth=2)
            self.kinematics_ax.set_xlabel("Wheel Travel (mm)", fontsize=11)
            self.kinematics_ax.set_ylabel("Motion Ratio (wheel/shock)", fontsize=11)
            self.kinematics_ax.set_title("Motion Ratio Curve", fontsize=12, fontweight='bold')
            self.kinematics_ax.grid(True, alpha=0.3)

            self.kinematics_fig.tight_layout()
            self.kinematics_canvas.draw()
            self.logger.info(f"Motion ratio calculated successfully: {len(travel_vals)} points")
        except Exception as e:
            self.logger.error(f"Error calculating motion ratio: {e}")
            self.update_kinematics_results(f"Error calculating motion ratio: {e}")

    def calculate_camber_curve(self):
        """Calculate camber curve through suspension travel"""
        self.update_kinematics_results("Camber Curve calculation - feature coming soon!")

    def calculate_roll_center(self):
        """Calculate roll center height through suspension travel"""
        from src.utils.roll_center import RollCenterCalculator

        # Get suspension type
        susp_type = self.kinematics_suspension.get()
        data = self.basic_data if susp_type == "basic" else self.pushrod_data

        # Create calculator (always in mm for now)
        calculator = RollCenterCalculator(track_width=1200.0, units="mm")

        # Calculate
        results = calculator.calculate_roll_center(data, susp_type)

        # Display results in text area
        output = calculator.format_results(results)
        self.update_kinematics_results(output)

        # COMPLETELY RESET THE AXIS BEFORE PLOTTING
        self.kinematics_ax.clear()
        self.kinematics_ax.set_aspect('auto')  # Important: reset aspect ratio

        # Plot the 2D visualization with roll center
        calculator.plot_roll_center(self.kinematics_ax, data, results, susp_type)
        self.kinematics_canvas.draw()

    def update_kinematics_results(self, text):
        """Update the results text area"""
        self.kinematics_results.configure(state=tk.NORMAL)
        self.kinematics_results.delete(1.0, tk.END)
        self.kinematics_results.insert(tk.END, text)
        self.kinematics_results.configure(state=tk.DISABLED)


def calculate_motion_ratio_basic(data, travel_range=(-30, 30), step=1.0):
    """Motion ratio for basic suspension (shock directly on arm)."""
    shock_top = data[:, 4]
    lca_out = data[:, 6]
    shock_bot = data[:, 7]

    wheel_ref_z = lca_out[2]
    spring_ref_len = np.linalg.norm(shock_top - shock_bot)

    travel_vals = np.arange(travel_range[0], travel_range[1] + step, step)
    mr_vals = []

    for dz in travel_vals:
        lca_out_new = lca_out.copy()
        lca_out_new[2] = wheel_ref_z + dz

        shock_bot_new = shock_bot.copy()
        shock_bot_new[2] += dz

        spring_len_new = np.linalg.norm(shock_top - shock_bot_new)
        dy = dz
        dx = spring_ref_len - spring_len_new
        mr = dy / dx if abs(dx) > 1e-6 else np.nan
        mr_vals.append(mr)

    return travel_vals, np.array(mr_vals)


def calculate_motion_ratio_pushrod(data, travel_range=(-30, 30), step=1.0):
    """Motion ratio for pushrod suspension using pushrod -> rocker -> shock."""
    travel_vals = np.arange(travel_range[0], travel_range[1] + step, step)
    mr_vals = []

    wheel_ref_z = data[2, 6]
    pushrod_bot_z = data[2, 7]
    shock_bot_z = data[2, 9]
    shock_top_z = data[2, 10]

    shock_ref_len = shock_top_z - shock_bot_z

    for dz in travel_vals:
        wheel_z_new = wheel_ref_z + dz
        pushrod_bot_new_z = pushrod_bot_z + dz

        shock_disp = (pushrod_bot_new_z - pushrod_bot_z) * (shock_bot_z - shock_top_z) / (pushrod_bot_z - shock_top_z)

        mr = dz / shock_disp if abs(shock_disp) > 1e-6 else np.nan
        mr_vals.append(mr)

    return travel_vals, np.array(mr_vals)