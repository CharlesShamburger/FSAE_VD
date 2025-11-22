import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D


class PlottingUtils:
    def __init__(self, parent, basic_data, pushrod_data, basic_members, pushrod_members,
                 basic_data_right=None, pushrod_data_right=None):
        self.basic_data = basic_data
        self.pushrod_data = pushrod_data
        self.basic_members = basic_members
        self.pushrod_members = pushrod_members
        self.basic_data_right = basic_data_right
        self.pushrod_data_right = pushrod_data_right

        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Embed plot in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add matplotlib toolbar
        toolbar_frame = tk.Frame(parent)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()

    def plot_suspension_side(self, data, members, color, alpha=0.8, linewidth=2):
        """Plot one side of suspension"""
        # Plot points
        for i in range(data.shape[1]):
            self.ax.scatter([data[0, i]], [data[1, i]], [data[2, i]],
                            color=color, s=100, alpha=alpha)

        # Draw lines
        for i, j in members:
            if i < data.shape[1] and j < data.shape[1]:
                self.ax.plot([data[0, i], data[0, j]],
                             [data[1, i], data[1, j]],
                             [data[2, i], data[2, j]],
                             color=color, linewidth=linewidth, alpha=alpha * 0.875)

    def update_plot(self, show_basic, show_pushrod, show_mirror=False):
        """Update the 3D plot based on checkbox states"""
        self.ax.clear()

        # Plot LEFT side (original data)
        if show_basic:
            self.plot_suspension_side(self.basic_data, self.basic_members, 'red')

        if show_pushrod:
            self.plot_suspension_side(self.pushrod_data, self.pushrod_members, 'blue')

        # Plot RIGHT side (mirrored data) if enabled
        if show_mirror:
            if show_basic and self.basic_data_right is not None:
                self.plot_suspension_side(self.basic_data_right, self.basic_members,
                                          'red', alpha=0.6, linewidth=2)

            if show_pushrod and self.pushrod_data_right is not None:
                self.plot_suspension_side(self.pushrod_data_right, self.pushrod_members,
                                          'blue', alpha=0.6, linewidth=2)

            # Draw centerline (Y=0 plane indicator)
            x_limits = self.ax.get_xlim()
            z_limits = self.ax.get_zlim()
            self.ax.plot([x_limits[0], x_limits[1]], [0, 0],
                         [z_limits[0], z_limits[0]],
                         'k--', linewidth=1, alpha=0.3, label='Centerline')

        # Set up plot
        self.ax.set_xlabel('X (forward)')
        self.ax.set_ylabel('Y (left ← | → right)')
        self.ax.set_zlabel('Z (up)')

        title = 'FSAE Front Suspension Geometry' if show_mirror else 'FSAE Suspension Geometry'
        self.ax.set_title(title)

        self.ax.grid(True)

        # Make axes equal for better visualization
        self.set_axes_equal()

        # Refresh the canvas
        self.canvas.draw()

    def set_axes_equal(self):
        """Set equal aspect ratio for 3D plot"""
        # Get current limits
        x_limits = self.ax.get_xlim3d()
        y_limits = self.ax.get_ylim3d()
        z_limits = self.ax.get_zlim3d()

        # Calculate ranges
        x_range = abs(x_limits[1] - x_limits[0])
        y_range = abs(y_limits[1] - y_limits[0])
        z_range = abs(z_limits[1] - z_limits[0])

        # Find the maximum range
        max_range = max(x_range, y_range, z_range)

        # Calculate midpoints
        x_mid = (x_limits[0] + x_limits[1]) * 0.5
        y_mid = (y_limits[0] + y_limits[1]) * 0.5
        z_mid = (z_limits[0] + z_limits[1]) * 0.5

        # Set new limits
        self.ax.set_xlim3d([x_mid - max_range * 0.5, x_mid + max_range * 0.5])
        self.ax.set_ylim3d([y_mid - max_range * 0.5, y_mid + max_range * 0.5])
        self.ax.set_zlim3d([z_mid - max_range * 0.5, z_mid + max_range * 0.5])