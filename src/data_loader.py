import pandas as pd
import numpy as np


class DataLoader:
    def __init__(self, excel_file=r"C:\Users\charl\OneDrive - Tennessee Tech University\Fall 2025\FSAE\Geo.xlsx"):
        self.excel_file = excel_file
        self.basic_data = None
        self.pushrod_data = None
        self.basic_members = []
        self.pushrod_members = []
        self.load_data()

    def load_data(self):
        """Load suspension data from Excel"""
        df = pd.read_excel(self.excel_file, sheet_name=0, header=None)

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