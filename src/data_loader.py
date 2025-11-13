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

    def get_2d_points(self, suspension_type='pushrod'):
        """
        Calculate 2D Y-Z projections for kinematics analysis.
        Returns a dictionary of 2D points (Y, Z) for the specified suspension.

        Args:
            suspension_type: 'basic' or 'pushrod'

        Returns:
            dict: Dictionary with point names as keys and [Y, Z] arrays as values
        """
        if suspension_type == 'basic':
            data = self.basic_data
            # Column indices for basic suspension
            points = {
                'UCA_IN': self._calculate_effective_point(data, [0, 1]),  # Average of front and rear UCA inboard
                'LCA_IN': self._calculate_effective_point(data, [2, 3]),  # Average of front and rear LCA inboard
                'PushRodIN': np.array([data[1, 4], data[2, 4]]),
                'UCA_OUT': np.array([data[1, 5], data[2, 5]]),
                'LCA_OUT': np.array([data[1, 6], data[2, 6]]),
                'PushRodOUT': np.array([data[1, 7], data[2, 7]]),
                'Wheel_center': np.array([data[1, 8], data[2, 8]])
            }
        else:  # pushrod
            data = self.pushrod_data
            # Column indices for pushrod suspension
            points = {
                'UCA_IN': self._calculate_effective_point(data, [0, 1]),  # Average of front and rear UCA inboard
                'LCA_IN': self._calculate_effective_point(data, [2, 3]),  # Average of front and rear LCA inboard
                'PushRodIN': np.array([data[1, 4], data[2, 4]]),
                'UCA_OUT': np.array([data[1, 5], data[2, 5]]),
                'LCA_OUT': np.array([data[1, 6], data[2, 6]]),
                'PushRodOUT': np.array([data[1, 7], data[2, 7]]),
                'Cam_Hinge': np.array([data[1, 8], data[2, 8]]),
                'Shock_OUT': np.array([data[1, 9], data[2, 9]]),
                'Shock_IN': np.array([data[1, 10], data[2, 10]]),
                'Wheel_center': np.array([data[1, 11], data[2, 11]])
            }

        return points

    def _calculate_effective_point(self, data, indices):
        """
        Calculate effective 2D point for control arms that have front and rear mounts.
        Uses centroid of the mounting points projected onto Y-Z plane.

        Args:
            data: 3D coordinate array (3 x N)
            indices: list of column indices to average (e.g., [0, 1] for front and rear UCA)

        Returns:
            np.array: [Y, Z] coordinates
        """
        # Average the Y and Z coordinates
        y_avg = np.mean([data[1, i] for i in indices])
        z_avg = np.mean([data[2, i] for i in indices])

        return np.array([y_avg, z_avg])