import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from src.utils.plotting import PlottingUtils
from src.utils.tables import TableUtils


class GeometryTab:
    def __init__(self, parent_notebook, basic_data, pushrod_data, basic_members, pushrod_members):
        self.basic_data = basic_data
        self.pushrod_data = pushrod_data
        self.basic_members = basic_members
        self.pushrod_members = pushrod_members

        self.geometry_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.geometry_frame, text="Geometry")

        # Create main paned window (horizontal split)
        main_paned = ttk.PanedWindow(self.geometry_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Controls (same as before)
        control_frame = ttk.LabelFrame(main_paned, text="Controls", padding=10)
        main_paned.add(control_frame, weight=0)

        # Right side: Data and visualization (vertical split)
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=1)

        # Top half: Data tables
        table_frame = ttk.LabelFrame(right_paned, text="Geometry Data", padding=5)
        right_paned.add(table_frame, weight=0)

        # Bottom half: 3D plot
        plot_frame = ttk.LabelFrame(right_paned, text="3D Visualization", padding=5)
        right_paned.add(plot_frame, weight=1)  # ← Fixed!

        # Setup each section
        self.setup_geometry_controls(control_frame)
        self.table_utils = TableUtils(table_frame, self.basic_data, self.pushrod_data, self.update_plot)
        self.plotting_utils = PlottingUtils(plot_frame, self.basic_data, self.pushrod_data, self.basic_members, self.pushrod_members)

        # Set references for view controls
        self.fig = self.plotting_utils.fig
        self.ax = self.plotting_utils.ax
        self.canvas = self.plotting_utils.canvas

    def setup_geometry_controls(self, parent):
        """Setup control widgets for geometry tab"""
        # Checkboxes for toggling suspension types
        self.basic_var = tk.BooleanVar(value=True)
        self.pushrod_var = tk.BooleanVar(value=True)

        basic_check = ttk.Checkbutton(parent, text="Basic Suspension",
                                      variable=self.basic_var, command=self.update_plot)
        basic_check.pack(anchor=tk.W, pady=5)

        pushrod_check = ttk.Checkbutton(parent, text="Pushrod Suspension",
                                        variable=self.pushrod_var, command=self.update_plot)
        pushrod_check.pack(anchor=tk.W, pady=5)

        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)

        # View controls
        ttk.Label(parent, text="View Controls:").pack(anchor=tk.W)

        view_frame = ttk.Frame(parent)
        view_frame.pack(fill=tk.X, pady=5)

        ttk.Button(view_frame, text="Top View", command=self.set_top_view).pack(fill=tk.X, pady=2)
        ttk.Button(view_frame, text="Side View", command=self.set_side_view).pack(fill=tk.X, pady=2)
        ttk.Button(view_frame, text="Isometric", command=self.set_iso_view).pack(fill=tk.X, pady=2)

        # Info display
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)

        info_frame = ttk.LabelFrame(parent, text="Info", padding=5)
        info_frame.pack(fill=tk.X, pady=5)

        info_text = f"""Basic Points: {self.basic_data.shape[1]}
Pushrod Points: {self.pushrod_data.shape[1]}

RED = Basic Suspension
BLUE = Pushrod Suspension

Click and drag to rotate!"""

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)

    def update_plot(self):
        """Update the 3D plot based on checkbox states"""
        self.plotting_utils.update_plot(self.basic_var.get(), self.pushrod_var.get())

    def set_top_view(self):
        """Set top-down view"""
        self.ax.view_init(elev=90, azim=0)
        self.canvas.draw()

    def set_side_view(self):
        """Set side view"""
        self.ax.view_init(elev=0, azim=0)
        self.canvas.draw()

    def set_iso_view(self):
        """Set isometric view"""
        self.ax.view_init(elev=20, azim=45)
        self.canvas.draw()