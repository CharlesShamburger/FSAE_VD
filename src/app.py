import tkinter as tk
from tkinter import ttk
from src.data_loader import DataLoader
from src.tabs.geometry_tab import GeometryTab
from src.tabs.kinematics_tab import KinematicsTab
from src.tabs.analysis_tab import AnalysisTab
from src.tabs.load_conditions_tab import LoadConditionsTab


class SuspensionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FSAE Suspension Geometry Viewer")
        self.root.geometry("1200x800")

        # Load data
        self.data_loader = DataLoader()
        self.basic_data = self.data_loader.basic_data
        self.pushrod_data = self.data_loader.pushrod_data
        self.basic_members = self.data_loader.basic_members
        self.pushrod_members = self.data_loader.pushrod_members

        # Create the main notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create all tabs
        self.geometry_tab = GeometryTab(self.notebook, self.basic_data, self.pushrod_data, self.basic_members, self.pushrod_members)
        self.kinematics_tab = KinematicsTab(self.notebook, self.basic_data, self.pushrod_data, self.basic_members, self.pushrod_members)
        self.load_conditions_tab = LoadConditionsTab(self.notebook, self.data_loader)
        self.analysis_tab = AnalysisTab(self.notebook)

        # Initial plot
        self.geometry_tab.update_plot()