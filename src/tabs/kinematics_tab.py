import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from src.utils.plotting import PlottingUtils
import numpy as np


class KinematicsTab:
    def __init__(self, parent_notebook, basic_data, pushrod_data, basic_members, pushrod_members):
        self.basic_data = basic_data
        self.pushrod_data = pushrod_data
        self.basic_members = basic_members
        self.pushrod_members = pushrod_members

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
                   command=self.calculate_roll_center, state=tk.DISABLED).pack(fill=tk.X, pady=2)

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
        # Create matplotlib figure for kinematics results
        self.kinematics_fig = Figure(figsize=(12, 6), dpi=100)
        self.kinematics_ax = self.kinematics_fig.add_subplot(111)

        # Embed in tkinter
        self.kinematics_canvas = FigureCanvasTkAgg(self.kinematics_fig, master=parent)
        self.kinematics_canvas.draw()
        self.kinematics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add toolbar
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        kinematics_toolbar = NavigationToolbar2Tk(self.kinematics_canvas, toolbar_frame)
        kinematics_toolbar.update()

        # Initial plot setup
        self.kinematics_ax.set_title("Kinematics Analysis Results")
        self.kinematics_ax.grid(True, alpha=0.3)
        self.kinematics_canvas.draw()

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
        # Use the existing plotting utility with checkbox states
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

    def calculate_motion_ratio(self):
        """Calculate motion ratio through suspension travel"""
        # 1) Read range and step size from user inputs
        travel_min = float(self.travel_min.get())
        travel_max = float(self.travel_max.get())
        step = float(self.travel_step.get())

        # 2) Pick which suspension dataset to use and then calculate

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


        # 4) Update results text box
        result_text = "Motion Ratio Results:\n"
        for t, m in zip(travel_vals, mr_vals):
            result_text += f"Travel {t:.1f} mm -> MR {m:.3f}\n"
        self.update_kinematics_results(result_text)

        # 5) Plot results in analysis graph
        self.kinematics_ax.clear()
        self.kinematics_ax.plot(travel_vals, mr_vals, marker="o")
        self.kinematics_ax.set_xlabel("Wheel Travel (mm)")
        self.kinematics_ax.set_ylabel("Motion Ratio (wheel/shock)")
        self.kinematics_ax.set_title("Motion Ratio Curve")
        self.kinematics_ax.grid(True, alpha=0.3)
        self.kinematics_canvas.draw()

    def calculate_camber_curve(self):
        """Calculate camber curve through suspension travel"""
        self.update_kinematics_results("Camber Curve calculation - feature coming soon!")

    def calculate_roll_center(self):
        """Calculate roll center height through suspension travel"""
        self.update_kinematics_results("Roll Center calculation - feature coming soon!")

    def update_kinematics_results(self, text):
        """Update the results text area"""
        self.kinematics_results.configure(state=tk.NORMAL)
        self.kinematics_results.delete(1.0, tk.END)
        self.kinematics_results.insert(tk.END, text)
        self.kinematics_results.configure(state=tk.DISABLED)
def calculate_motion_ratio_basic(data, travel_range=(-30, 30), step=1.0):
    """Motion ratio for basic suspension (shock directly on arm)."""
    shock_top = data[:, 4]  # (x,y,z)
    lca_out   = data[:, 6]  # (x,y,z)
    shock_bot = data[:, 7]  # (x,y,z)

    wheel_ref_z = lca_out[2]
    spring_ref_len = np.linalg.norm(shock_top - shock_bot)

    travel_vals = np.arange(travel_range[0], travel_range[1] + step, step)
    mr_vals = []

    for dz in travel_vals:
        # Move wheel/LCA outboard point
        lca_out_new = lca_out.copy()
        lca_out_new[2] = wheel_ref_z + dz

        # Approx shock bottom follows wheel vertical travel
        shock_bot_new = shock_bot.copy()
        shock_bot_new[2] += dz

        spring_len_new = np.linalg.norm(shock_top - shock_bot_new)
        dy = dz
        dx = spring_ref_len - spring_len_new
        mr = dy / dx if abs(dx) > 1e-6 else np.nan
        mr_vals.append(mr)

    return travel_vals, np.array(mr_vals)


def calculate_motion_ratio_pushrod(data, travel_range=(-30, 30), step=1.0):
    """
    Motion ratio for pushrod suspension using pushrod -> rocker -> shock.
    data: 3x11 array as defined in TableUtils
    """
    travel_vals = np.arange(travel_range[0], travel_range[1] + step, step)
    mr_vals = []

    # Reference vertical positions
    wheel_ref_z = data[2, 6]       # LCA_OUT z
    pushrod_bot_z = data[2, 7]     # PushRodOUT z
    shock_bot_z = data[2, 9]       # Shock_OUT z
    shock_top_z = data[2, 10]      # Shock_IN z

    shock_ref_len = shock_top_z - shock_bot_z

    for dz in travel_vals:
        # 1) Move wheel
        wheel_z_new = wheel_ref_z + dz

        # 2) Move pushrod bottom with wheel
        pushrod_bot_new_z = pushrod_bot_z + dz

        # 3) Approx rocker rotation → shock vertical displacement
        # For now, assume linear relation based on geometry:
        # shock moves less than wheel, typical pushrod MR < 1
        shock_disp = (pushrod_bot_new_z - pushrod_bot_z) * (shock_bot_z - shock_top_z) / (pushrod_bot_z - shock_top_z)

        # Avoid division by zero
        mr = dz / shock_disp if abs(shock_disp) > 1e-6 else np.nan
        mr_vals.append(mr)

    return travel_vals, np.array(mr_vals)


