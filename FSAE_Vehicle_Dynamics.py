import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class SuspensionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FSAE Suspension Geometry Viewer")
        self.root.geometry("1200x800")

        # Load data
        self.load_data()

        # Create the main notebook (tabs)
        self.create_notebook()

        # Create all tabs
        self.create_geometry_tab()
        self.create_kinematics_tab()
        self.create_analysis_tab()

        # Initial plot
        self.update_plot()

    def load_data(self):
        """Load suspension data from Excel"""
        excel_file = r"C:\Users\charl\OneDrive - Tennessee Tech University\Fall 2025\FSAE\Geo.xlsx"
        df = pd.read_excel(excel_file, sheet_name=0, header=None)

        # Extract data
        self.basic_data = np.nan_to_num(df.iloc[1:4, 1:9].values, nan=0.0)
        self.pushrod_data = np.nan_to_num(df.iloc[5:8, 1:12].values, nan=0.0)

        print("Data loaded:")
        print(f"Basic: {self.basic_data.shape}, Pushrod: {self.pushrod_data.shape}")


        # Basic suspension connections (point index pairs)
        self.basic_members = [
            (0, 5),  # UCA_FrontIN → UCA_OUT
            (1, 5),  # UCA_RearIN → UCA_OUT
            (2, 6),  # LCA_FrontIN → LCA_OUT
            (3, 6),  # LCA_RearIN → LCA_OUT
            (4, 7),  # Shock_Top → Shock_Bottom
        ]

        # Pushrod suspension connections
        self.pushrod_members = [
            (0, 5),  # UCA_FrontIN → UCA_OUT
            (1, 5),  # UCA_RearIN → UCA_OUT
            (2, 6),  # LCA_FrontIN → LCA_OUT
            (3, 6),  # LCA_RearIN → LCA_OUT
            (4, 7),  # PushRodIN → PushRodOUT
            (4, 8),  # PushRodIN → Cam_Hinge
            (4, 9),  # PushRodIN → Shock_OUT
            (9, 10),  # Shock_OUT → Shock_IN
            (8, 9)  # Cam_Hinge → Shock_OUT
        ]


    def create_notebook(self):
        """Create the main notebook widget for tabs"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    #Tab Creation----------------

    def create_geometry_tab(self):
        """Create the geometry visualization tab"""
        self.geometry_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.geometry_frame, text="Geometry")

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
        self.setup_data_tables(table_frame)
        self.setup_3d_plot(plot_frame)

    def create_kinematics_tab(self):
        """Create the kinematics analysis tab"""
        self.kinematics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.kinematics_frame, text="Kinematics")

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

    def create_analysis_tab(self):
        """Create the analysis tab"""
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Analysis")

        # Just a simple placeholder for now
        placeholder_label = ttk.Label(self.analysis_frame,
                                      text="Analysis tab - coming soon!",
                                      font=("Arial", 16))
        placeholder_label.pack(expand=True)



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

    def setup_3d_plot(self, parent):
        """Setup 3D plotting area"""
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Embed plot in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add matplotlib toolbar
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()


    def update_plot(self):
        """Update the 3D plot based on checkbox states"""
        self.ax.clear()

        # Plot basic suspension if enabled
        if self.basic_var.get():
            for i in range(self.basic_data.shape[1]):
                self.ax.scatter([self.basic_data[0, i]], [self.basic_data[1, i]], [self.basic_data[2, i]],
                                color='red', s=100, alpha=0.8)

        # Plot pushrod suspension if enabled
        if self.pushrod_var.get():
            for i in range(self.pushrod_data.shape[1]):
                self.ax.scatter([self.pushrod_data[0, i]], [self.pushrod_data[1, i]], [self.pushrod_data[2, i]],
                                color='blue', s=100, alpha=0.8)

        # Draw basic suspension lines if enabled
        if self.basic_var.get():
            for i, j in self.basic_members:
                if i < self.basic_data.shape[1] and j < self.basic_data.shape[1]:
                    self.ax.plot([self.basic_data[0, i], self.basic_data[0, j]],
                                 [self.basic_data[1, i], self.basic_data[1, j]],
                                 [self.basic_data[2, i], self.basic_data[2, j]],
                                 'r-', linewidth=2, alpha=0.7)

        # Draw pushrod suspension lines if enabled
        if self.pushrod_var.get():
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

    def setup_data_tables(self, parent):
        """Setup interactive data tables for geometry display"""
        # Create notebook for tables (tabs within the table area)
        table_notebook = ttk.Notebook(parent)
        table_notebook.pack(fill=tk.BOTH, expand=True)

        # Create column names (matching your Excel)
        basic_columns = ['UCA_FrontIN', 'UCA_RearIN', 'LCA_FrontIN', 'LCA_RearIN',
                         'Shock_Top', 'UCA_OUT', 'LCA_OUT', 'Shock_Bottom']
        pushrod_columns = ['UCA_FrontIN', 'UCA_RearIN', 'LCA_FrontIN', 'LCA_RearIN',
                           'PushRodIN', 'UCA_OUT', 'LCA_OUT', 'PushRodOUT',
                           'Cam_Hinge', 'Shock_OUT', 'Shock_IN']

        # Setup Basic Suspension Table
        self.setup_basic_table(table_notebook, basic_columns)

        # Setup Pushrod Suspension Table
        self.setup_pushrod_table(table_notebook, pushrod_columns)

    def setup_basic_table(self, parent_notebook, columns):
        """Setup the basic suspension data table"""
        # Create frame for basic table
        basic_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(basic_frame, text="Basic Suspension")

        # Create treeview (this is tkinter's table widget)
        self.basic_tree = ttk.Treeview(basic_frame)
        self.basic_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Add scrollbar
        basic_scroll = ttk.Scrollbar(basic_frame, orient=tk.VERTICAL, command=self.basic_tree.yview)
        basic_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.basic_tree.configure(yscrollcommand=basic_scroll.set)

        # Setup columns - add "Coord" column first, then the point names
        all_columns = ["Coord"] + columns[:self.basic_data.shape[1]]
        self.basic_tree["columns"] = all_columns
        self.basic_tree["show"] = "headings"  # Hide the default first column

        # Configure column headers and widths
        for col in all_columns:
            self.basic_tree.heading(col, text=col)
            width = 60 if col == "Coord" else 80
            self.basic_tree.column(col, width=width, anchor=tk.CENTER)

        # Populate with data (X, Y, Z rows)
        coord_labels = ['X', 'Y', 'Z']
        for i, coord in enumerate(coord_labels):
            # Create row data: coordinate label + values for each point
            row_data = [coord]
            for j in range(self.basic_data.shape[1]):
                row_data.append(f"{self.basic_data[i, j]:.1f}")

            # Insert row into table
            item_id = self.basic_tree.insert("", tk.END, values=row_data)

        # Make table editable
        self.basic_tree.bind('<Double-1>', lambda event: self.edit_basic_cell(event))

    def setup_pushrod_table(self, parent_notebook, columns):
        """Setup the pushrod suspension data table"""
        # Create frame for pushrod table
        pushrod_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(pushrod_frame, text="Pushrod Suspension")

        # Create treeview
        self.pushrod_tree = ttk.Treeview(pushrod_frame)
        self.pushrod_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Add scrollbar
        pushrod_scroll = ttk.Scrollbar(pushrod_frame, orient=tk.VERTICAL, command=self.pushrod_tree.yview)
        pushrod_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.pushrod_tree.configure(yscrollcommand=pushrod_scroll.set)

        # Setup columns
        all_columns = ["Coord"] + columns[:self.pushrod_data.shape[1]]
        self.pushrod_tree["columns"] = all_columns
        self.pushrod_tree["show"] = "headings"

        # Configure columns
        for col in all_columns:
            self.pushrod_tree.heading(col, text=col)
            width = 60 if col == "Coord" else 80
            self.pushrod_tree.column(col, width=width, anchor=tk.CENTER)

        # Populate with data
        coord_labels = ['X', 'Y', 'Z']
        for i, coord in enumerate(coord_labels):
            row_data = [coord]
            for j in range(self.pushrod_data.shape[1]):
                row_data.append(f"{self.pushrod_data[i, j]:.1f}")

            item_id = self.pushrod_tree.insert("", tk.END, values=row_data)

        # Make table editable
        self.pushrod_tree.bind('<Double-1>', lambda event: self.edit_pushrod_cell(event))

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

        # Setup geometry viewer (duplicate of main geometry view)
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

        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        kinematics_toolbar = NavigationToolbar2Tk(self.kinematics_canvas, toolbar_frame)
        kinematics_toolbar.update()

        # Initial plot setup
        self.kinematics_ax.set_title("Kinematics Analysis Results")
        self.kinematics_ax.grid(True, alpha=0.3)
        self.kinematics_canvas.draw()

    def setup_kinematics_geometry(self, parent):
        """Setup 3D geometry viewer for kinematics tab"""
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

        # Right side: 3D plot
        geo_plot_frame = ttk.Frame(geo_main_frame)
        geo_plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create matplotlib figure for kinematics geometry
        self.kinematics_geo_fig = Figure(figsize=(10, 6), dpi=100)
        self.kinematics_geo_ax = self.kinematics_geo_fig.add_subplot(111, projection='3d')

        # Embed in tkinter
        self.kinematics_geo_canvas = FigureCanvasTkAgg(self.kinematics_geo_fig, master=geo_plot_frame)
        self.kinematics_geo_canvas.draw()
        self.kinematics_geo_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add toolbar
        geo_toolbar_frame = ttk.Frame(geo_plot_frame)
        geo_toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        geo_toolbar = NavigationToolbar2Tk(self.kinematics_geo_canvas, geo_toolbar_frame)
        geo_toolbar.update()

        # Initial plot
        self.kinematics_geo_ax.set_title('Suspension Geometry - Kinematics View')
        self.kinematics_geo_ax.grid(True)
        self.kinematics_geo_canvas.draw()

    def update_kinematics_geometry(self):
        """Update the kinematics 3D geometry plot"""
        self.kinematics_geo_ax.clear()


        # Plot basic suspension if enabled
        if self.kin_show_basic.get():
            self.kinematics_geo_ax.scatter(self.basic_data[0, :], self.basic_data[1, :], self.basic_data[2, :],
                                           color='red', s=100, alpha=0.8, label='Basic')

            # Draw basic suspension lines
            for i, j in self.basic_members:
                if i < self.basic_data.shape[1] and j < self.basic_data.shape[1]:
                    self.kinematics_geo_ax.plot([self.basic_data[0, i], self.basic_data[0, j]],
                                                [self.basic_data[1, i], self.basic_data[1, j]],
                                                [self.basic_data[2, i], self.basic_data[2, j]],
                                                'r-', linewidth=2, alpha=0.7)

        # Plot pushrod suspension if enabled
        if self.kin_show_pushrod.get():
            self.kinematics_geo_ax.scatter(self.pushrod_data[0, :], self.pushrod_data[1, :], self.pushrod_data[2, :],
                                           color='blue', s=100, alpha=0.8, label='Pushrod')

            # Draw pushrod suspension lines
            for i, j in self.pushrod_members:
                if i < self.pushrod_data.shape[1] and j < self.pushrod_data.shape[1]:
                    self.kinematics_geo_ax.plot([self.pushrod_data[0, i], self.pushrod_data[0, j]],
                                                [self.pushrod_data[1, i], self.pushrod_data[1, j]],
                                                [self.pushrod_data[2, i], self.pushrod_data[2, j]],
                                                'b-', linewidth=2, alpha=0.7)

        # Set up plot
        self.kinematics_geo_ax.set_xlabel('X (forward)')
        self.kinematics_geo_ax.set_ylabel('Y (left)')
        self.kinematics_geo_ax.set_zlabel('Z (up)')
        self.kinematics_geo_ax.set_title('Suspension Geometry - Kinematics View')
        self.kinematics_geo_ax.grid(True)

        # Add legend if both are shown
        if self.kin_show_basic.get() and self.kin_show_pushrod.get():
            self.kinematics_geo_ax.legend()

        # Refresh canvas
        self.kinematics_geo_canvas.draw()

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


    def edit_basic_cell(self, event):
        """Handle double-click editing of basic suspension table cells"""
        item = self.basic_tree.selection()[0]
        column = self.basic_tree.identify_column(event.x)

        # Don't allow editing the "Coord" column (column #1)
        if column == '#1':
            return

        # Get current value
        current_values = self.basic_tree.item(item, 'values')
        col_index = int(column[1:]) - 1  # Convert '#2' to 1, '#3' to 2, etc.
        current_value = current_values[col_index]

        # Create entry widget for editing
        self.create_edit_entry(self.basic_tree, item, column, current_value, 'basic')

    def edit_pushrod_cell(self, event):
        """Handle double-click editing of pushrod suspension table cells"""
        item = self.pushrod_tree.selection()[0]
        column = self.pushrod_tree.identify_column(event.x)

        # Don't allow editing the "Coord" column
        if column == '#1':
            return

        # Get current value
        current_values = self.pushrod_tree.item(item, 'values')
        col_index = int(column[1:]) - 1
        current_value = current_values[col_index]

        # Create entry widget for editing
        self.create_edit_entry(self.pushrod_tree, item, column, current_value, 'pushrod')

    def create_edit_entry(self, tree, item, column, current_value, table_type):
        """Create an entry widget for editing table cells"""
        # Get the bounding box of the cell
        x, y, width, height = tree.bbox(item, column)

        # Create entry widget
        self.edit_entry = tk.Entry(tree, justify='center')
        self.edit_entry.place(x=x, y=y, width=width, height=height)

        # Set current value
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()

        # Store information needed for saving
        self.edit_entry.item = item
        self.edit_entry.column = column
        self.edit_entry.tree = tree
        self.edit_entry.table_type = table_type

        # Bind events for saving/canceling
        self.edit_entry.bind('<Return>', self.save_cell_edit)
        self.edit_entry.bind('<Escape>', self.cancel_cell_edit)
        self.edit_entry.bind('<FocusOut>', self.save_cell_edit)

    def save_cell_edit(self, event):
        """Save the edited cell value and update data matrices"""
        entry = event.widget
        new_value = entry.get()

        # Validate input (must be a number)
        try:
            float_value = float(new_value)
        except ValueError:
            # Invalid input, cancel edit
            self.cancel_cell_edit(event)
            return

        # Get the row and column information
        item = entry.item
        column = entry.column
        tree = entry.tree
        table_type = entry.table_type

        # Update the table display
        current_values = list(tree.item(item, 'values'))
        col_index = int(column[1:]) - 1
        current_values[col_index] = f"{float_value:.1f}"
        tree.item(item, values=current_values)

        # Update the corresponding data matrix
        self.update_data_matrix(item, col_index, float_value, table_type)

        # Remove the entry widget
        entry.destroy()

        # Update the plot with new data
        self.update_plot()

    def cancel_cell_edit(self, event):
        """Cancel cell editing without saving"""
        event.widget.destroy()

    def update_data_matrix(self, item, col_index, new_value, table_type):
        """Update the underlying data matrices when table values change"""
        # Figure out which row (X, Y, or Z) we're editing
        if table_type == 'basic':
            tree = self.basic_tree
            data_matrix = self.basic_data
        else:
            tree = self.pushrod_tree
            data_matrix = self.pushrod_data

        # Find which row this item represents
        all_items = tree.get_children()
        row_index = all_items.index(item)  # 0=X, 1=Y, 2=Z

        # Update the data matrix (subtract 1 from col_index because column 0 is "Coord")
        point_index = col_index - 1
        if point_index >= 0:  # Make sure we're not trying to edit the "Coord" column
            data_matrix[row_index, point_index] = new_value

            print(f"Updated {table_type} data: Row {row_index}, Point {point_index} = {new_value}")

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


# Create and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = SuspensionApp(root)
    root.mainloop()