import numpy as np


class DataLoader:
    def __init__(self):
        self.basic_data = None
        self.pushrod_data = None
        self.basic_members = []
        self.pushrod_members = []
        self.load_data()

    def load_data(self):
        """Load suspension data from hardcoded arrays (all dimensions in inches)"""

        # Basic suspension data (3 rows x 9 columns) - ALL IN INCHES
        # Columns: UCA_FrontIN, UCA_RearIN, LCA_FrontIN, LCA_RearIN, PushRodIN, UCA_OUT, LCA_OUT, PushRodOUT, Wheel_Center
        self.basic_data = np.array([
            [22, 28.75, 20.5, 28.75, 25.01, 25.125, 25.095, 25.01, 25],  # X coordinates
            [9.812, 9.12, 10, 9.31, 12.625, 19, 20.625, 15.8125, 24],  # Y coordinates
            [8.875, 9.125, 4, 4, 14.75, 11.875, 5.125, 5.75, 8.5]  # Z coordinates
        ], dtype=float)

        # Pushrod suspension data (3 rows x 12 columns) - IN INCHES
        # Uses same control arms and wheel center as basic, adds rocker mechanism with shock on top
        # Columns: UCA_FrontIN, UCA_RearIN, LCA_FrontIN, LCA_RearIN, PushRodIN, UCA_OUT, LCA_OUT,
        #          PushRodOUT, Cam_Hinge, Shock_OUT, Shock_IN, Wheel_Center
        self.pushrod_data = np.array([
            [22, 28.75, 20.5, 28.75, 25.01, 25.125, 25.095, 25, 25, 25, 25, 25],
            # X coordinates (rocker/shock aligned with wheel center)
            [9.812, 9.12, 10, 9.31, 12.625, 19, 20.625, 15.8125, 11.0, 9.5, 5.0, 24],  # Y coordinates
            [8.875, 9.125, 4, 4, 14.75, 11.875, 5.125, 5.75, 13.0, 15.0, 12.0, 8.5]  # Z coordinates
        ], dtype=float)

        print("Data loaded from hardcoded arrays (inches):")
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
            (8, 9),  # Cam_Hinge → Shock_OUT
            (5, 11),  # UCA_OUT → Wheel_Center
            (6, 11),  # LCA_OUT → Wheel_Center
        ]