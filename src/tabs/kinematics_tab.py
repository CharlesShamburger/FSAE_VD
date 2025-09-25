import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from src.utils.plotting import PlottingUtils


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
        self.update_kinematics_results("Motion Ratio calculation - coming next!")

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