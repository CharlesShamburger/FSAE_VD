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

        # Create mirrored data for right side
        self.basic_data_right = self.mirror_data(basic_data)
        self.pushrod_data_right = self.mirror_data(pushrod_data)

        # Zoom level
        self.zoom_level = 1.0

        self.geometry_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.geometry_frame, text="Geometry")

        # Create main paned window (horizontal split)
        main_paned = ttk.PanedWindow(self.geometry_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Controls
        control_frame = ttk.LabelFrame(main_paned, text="Controls", padding=10)
        main_paned.add(control_frame, weight=0)

        # Right side: Data and visualization (vertical split)
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=1)

        # Top half: Data tables
        table_frame = ttk.LabelFrame(right_paned, text="Geometry Data", padding=5)
        right_paned.add(table_frame, weight=0)

        # Track width display (between table and plot)
        self.track_width_frame = ttk.Frame(right_paned)
        right_paned.add(self.track_width_frame, weight=0)

        # Bottom half: 3D plot
        plot_frame = ttk.LabelFrame(right_paned, text="3D Visualization", padding=5)
        right_paned.add(plot_frame, weight=1)

        # Setup each section
        self.setup_geometry_controls(control_frame)
        self.table_utils = TableUtils(table_frame, self.basic_data, self.pushrod_data, self.update_plot)
        self.setup_track_width_display()
        self.plotting_utils = PlottingUtils(plot_frame, self.basic_data, self.pushrod_data,
                                            self.basic_members, self.pushrod_members,
                                            self.basic_data_right, self.pushrod_data_right)

        # Set references for view controls
        self.fig = self.plotting_utils.fig
        self.ax = self.plotting_utils.ax
        self.canvas = self.plotting_utils.canvas

        # Setup mouse wheel zoom
        self.setup_mouse_controls()

    def setup_mouse_controls(self):
        """Setup mouse wheel zoom and scroll controls"""
        # Mouse wheel zoom
        self.canvas.mpl_connect('scroll_event', self.on_scroll)

    def on_scroll(self, event):
        """Handle mouse wheel zoom"""
        if event.button == 'up':
            self.zoom_level *= 1.1
        elif event.button == 'down':
            self.zoom_level *= 0.9

        self.apply_zoom()

    def apply_zoom(self):
        """Apply current zoom level to the plot"""
        # Get current center
        x_limits = self.ax.get_xlim3d()
        y_limits = self.ax.get_ylim3d()
        z_limits = self.ax.get_zlim3d()

        x_center = (x_limits[0] + x_limits[1]) / 2
        y_center = (y_limits[0] + y_limits[1]) / 2
        z_center = (z_limits[0] + z_limits[1]) / 2

        # Calculate new ranges
        x_range = (x_limits[1] - x_limits[0]) / self.zoom_level
        y_range = (y_limits[1] - y_limits[0]) / self.zoom_level
        z_range = (z_limits[1] - z_limits[0]) / self.zoom_level

        # Apply new limits
        self.ax.set_xlim3d([x_center - x_range / 2, x_center + x_range / 2])
        self.ax.set_ylim3d([y_center - y_range / 2, y_center + y_range / 2])
        self.ax.set_zlim3d([z_center - z_range / 2, z_center + z_range / 2])

        self.canvas.draw()

    def mirror_data(self, data):
        """Mirror suspension data across Y=0 plane"""
        mirrored = data.copy()
        # Flip Y coordinate (left to right)
        mirrored[1, :] = -data[1, :]
        return mirrored

    def setup_track_width_display(self):
        """Setup track width information display"""
        # Create frame with border
        info_frame = ttk.LabelFrame(self.track_width_frame, text="Track Width", padding=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        # Calculate track widths
        basic_track_width = self.calculate_track_width(self.basic_data)
        pushrod_track_width = self.calculate_track_width(self.pushrod_data)

        # Create display labels
        basic_label = ttk.Label(info_frame,
                                text=f"Basic Suspension:    {basic_track_width:.2f} inches",
                                font=("Arial", 10, "bold"))
        basic_label.pack(anchor=tk.W, pady=2)

        pushrod_label = ttk.Label(info_frame,
                                  text=f"Pushrod Suspension:  {pushrod_track_width:.2f} inches",
                                  font=("Arial", 10, "bold"))
        pushrod_label.pack(anchor=tk.W, pady=2)

        # Store labels for updates
        self.basic_track_label = basic_label
        self.pushrod_track_label = pushrod_label

    def calculate_track_width(self, data):
        """Calculate track width from wheel center to mirrored wheel center"""
        # Wheel center is the last column
        wheel_center_y = data[1, -1]
        # Track width is 2 * |Y coordinate| (distance from centerline to wheel × 2)
        track_width = 2 * abs(wheel_center_y)
        return track_width

    def update_track_width_display(self):
        """Update track width display when geometry changes"""
        basic_track_width = self.calculate_track_width(self.basic_data)
        pushrod_track_width = self.calculate_track_width(self.pushrod_data)

        self.basic_track_label.config(text=f"Basic Suspension:    {basic_track_width:.2f} inches")
        self.pushrod_track_label.config(text=f"Pushrod Suspension:  {pushrod_track_width:.2f} inches")

    def setup_geometry_controls(self, parent):
        """Setup control widgets for geometry tab"""
        # Checkboxes for toggling suspension types
        self.basic_var = tk.BooleanVar(value=True)
        self.pushrod_var = tk.BooleanVar(value=True)
        self.mirror_var = tk.BooleanVar(value=True)

        basic_check = ttk.Checkbutton(parent, text="Basic Suspension",
                                      variable=self.basic_var, command=self.update_plot)
        basic_check.pack(anchor=tk.W, pady=5)

        pushrod_check = ttk.Checkbutton(parent, text="Pushrod Suspension",
                                        variable=self.pushrod_var, command=self.update_plot)
        pushrod_check.pack(anchor=tk.W, pady=5)

        mirror_check = ttk.Checkbutton(parent, text="Show Right Side (Mirrored)",
                                       variable=self.mirror_var, command=self.update_plot)
        mirror_check.pack(anchor=tk.W, pady=5)

        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)

        # Zoom controls
        ttk.Label(parent, text="Zoom Controls:").pack(anchor=tk.W)

        zoom_frame = ttk.Frame(parent)
        zoom_frame.pack(fill=tk.X, pady=5)

        ttk.Button(zoom_frame, text="Zoom In (+)", command=self.zoom_in).pack(fill=tk.X, pady=2)
        ttk.Button(zoom_frame, text="Zoom Out (-)", command=self.zoom_out).pack(fill=tk.X, pady=2)
        ttk.Button(zoom_frame, text="Reset Zoom", command=self.reset_zoom).pack(fill=tk.X, pady=2)

        ttk.Label(zoom_frame, text="(or use mouse wheel)",
                  font=("Arial", 8, "italic")).pack(anchor=tk.W, pady=(5, 0))

        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)

        # View controls
        ttk.Label(parent, text="View Controls:").pack(anchor=tk.W)

        view_frame = ttk.Frame(parent)
        view_frame.pack(fill=tk.X, pady=5)

        ttk.Button(view_frame, text="Top View", command=self.set_top_view).pack(fill=tk.X, pady=2)
        ttk.Button(view_frame, text="Side View", command=self.set_side_view).pack(fill=tk.X, pady=2)
        ttk.Button(view_frame, text="Front View", command=self.set_front_view).pack(fill=tk.X, pady=2)
        ttk.Button(view_frame, text="Isometric", command=self.set_iso_view).pack(fill=tk.X, pady=2)

        # Info display
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)

        info_frame = ttk.LabelFrame(parent, text="Info", padding=5)
        info_frame.pack(fill=tk.X, pady=5)

        info_text = f"""Basic Points: {self.basic_data.shape[1]}
Pushrod Points: {self.pushrod_data.shape[1]}

RED = Basic Suspension
BLUE = Pushrod Suspension

Mouse Controls:
• Drag to rotate
• Scroll wheel to zoom
• Right-click drag to pan

Mirrored view shows full
front suspension geometry."""

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)

    def zoom_in(self):
        """Zoom in on the plot"""
        self.zoom_level *= 1.2
        self.apply_zoom()

    def zoom_out(self):
        """Zoom out on the plot"""
        self.zoom_level *= 0.8
        self.apply_zoom()

    def reset_zoom(self):
        """Reset zoom to default"""
        self.zoom_level = 1.0
        self.update_plot()

    def update_plot(self):
        """Update the 3D plot based on checkbox states"""
        # Update mirrored data in case geometry changed
        self.basic_data_right = self.mirror_data(self.basic_data)
        self.pushrod_data_right = self.mirror_data(self.pushrod_data)

        # Update the plotting utils with new mirrored data
        self.plotting_utils.basic_data_right = self.basic_data_right
        self.plotting_utils.pushrod_data_right = self.pushrod_data_right

        # Update track width display
        self.update_track_width_display()

        # Update plot
        self.plotting_utils.update_plot(self.basic_var.get(), self.pushrod_var.get(), self.mirror_var.get())

        # Reapply zoom if not at default
        if self.zoom_level != 1.0:
            self.apply_zoom()

    def set_top_view(self):
        """Set top-down view"""
        self.ax.view_init(elev=90, azim=-90)
        self.canvas.draw()

    def set_side_view(self):
        """Set side view (looking from left side)"""
        self.ax.view_init(elev=0, azim=0)
        self.canvas.draw()

    def set_front_view(self):
        """Set front view (looking from front of car)"""
        self.ax.view_init(elev=0, azim=-90)
        self.canvas.draw()

    def set_iso_view(self):
        """Set isometric view"""
        self.ax.view_init(elev=20, azim=-60)
        self.canvas.draw()