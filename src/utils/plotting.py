import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D


class PlottingUtils:
    def __init__(self, parent, basic_data, pushrod_data, basic_members, pushrod_members):
        self.basic_data = basic_data
        self.pushrod_data = pushrod_data
        self.basic_members = basic_members
        self.pushrod_members = pushrod_members

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

    def update_plot(self, show_basic, show_pushrod):
        """Update the 3D plot based on checkbox states"""
        self.ax.clear()

        # Plot basic suspension if enabled
        if show_basic:
            for i in range(self.basic_data.shape[1]):
                self.ax.scatter([self.basic_data[0, i]], [self.basic_data[1, i]], [self.basic_data[2, i]],
                                color='red', s=100, alpha=0.8)

        # Plot pushrod suspension if enabled
        if show_pushrod:
            for i in range(self.pushrod_data.shape[1]):
                self.ax.scatter([self.pushrod_data[0, i]], [self.pushrod_data[1, i]], [self.pushrod_data[2, i]],
                                color='blue', s=100, alpha=0.8)

        # Draw basic suspension lines if enabled
        if show_basic:
            for i, j in self.basic_members:
                if i < self.basic_data.shape[1] and j < self.basic_data.shape[1]:
                    self.ax.plot([self.basic_data[0, i], self.basic_data[0, j]],
                                 [self.basic_data[1, i], self.basic_data[1, j]],
                                 [self.basic_data[2, i], self.basic_data[2, j]],
                                 'r-', linewidth=2, alpha=0.7)

        # Draw pushrod suspension lines if enabled
        if show_pushrod:
            for i, j in self.pushrod_members:
                if i < self.pushrod_data.shape[1] and j < self.pushrod_data.shape[1]:
                    self.ax.plot([self.pushrod_data[0, i], self.pushrod_data[0, j]],
                                 [self.pushrod_data[1, i], self.pushrod_data[1, j]],
                                 [self.pushrod_data[2, i], self.pushrod_data[2, j]],
                                 'b-', linewidth=2, alpha=0.7)
        # Set up plot
        self.ax.set_xlabel('X (forward)')
        self.ax.set_ylabel('Y (left)')
        self.ax.set_zlabel('Z (up)')
        self.ax.set_title('FSAE Suspension Geometry')
        self.ax.grid(True)

        # Refresh the canvas
        self.canvas.draw()