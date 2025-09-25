import tkinter as tk
from tkinter import ttk


class TableUtils:
    def __init__(self, parent, basic_data, pushrod_data, update_plot_callback=None):
        self.basic_data = basic_data
        self.pushrod_data = pushrod_data
        self.update_plot_callback = update_plot_callback

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
        if self.update_plot_callback:
            self.update_plot_callback()

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