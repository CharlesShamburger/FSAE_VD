import numpy as np


class DataLoader:
    def __init__(self):
        self.basic_data = None
        self.pushrod_data = None
        self.basic_members = []
        self.pushrod_members = []
        self.load_data()

    def load_data(self):
        """Load suspension data from hardcoded arrays"""

        # Basic suspension data (3 rows x 8 columns)
        # Columns: UCA_FrontIN, UCA_RearIN, LCA_FrontIN, LCA_RearIN, Shock_Top, UCA_OUT, LCA_OUT, Shock_Bottom
        self.basic_data = np.array([
            [-111, 120, -136, 138, -4, 4, -4, -4],  # X coordinates
            [-265, -265, -136, -220, -286, -544, -549, -509],  # Y coordinates
            [279, 279, 130, 146, 595, 318, 148, 177]  # Z coordinates
        ], dtype=float)

        # Pushrod suspension data (3 rows x 12 columns)
        # Columns: UCA_FrontIN, UCA_RearIN, LCA_FrontIN, LCA_RearIN, PushRodIN, UCA_OUT, LCA_OUT,
        #          PushRodOUT, Cam_Hinge, Shock_OUT, Shock_IN, Wheel_Center
        self.pushrod_data = np.array([
            [-4, -4, -4, -4, -4, 4, -4, -4, -4, -4, -4, -4],  # X coordinates
            [249.2, 249.2, 254, 254, 320.7, 482.6, 523.9, 381, 279.4, 241.3, 127, 609.6],  # Y coordinates
            [225.4, 225.4, 101.6, 101.6, 374.7, 301.6, 130.2, 114.3, 330.2, 381, 304.8, 215.9]  # Z coordinates
        ], dtype=float)

        print("Data loaded from hardcoded arrays:")
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