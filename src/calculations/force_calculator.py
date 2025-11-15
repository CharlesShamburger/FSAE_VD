import numpy as np


class SuspensionForceCalculator:
    """
    Calculates suspension member forces based on 3D geometry and external loads.
    Converted from MATLAB suspension force analysis script.
    """

    def __init__(self):
        self.force_names = ['Ftr', 'Flcaf', 'Flcar', 'Fucaf', 'Fucar', 'Fprod']

    def calculate_forces(self, coordinates, external_force, R=None):
        """
        Calculate forces in suspension members.

        Parameters:
        -----------
        coordinates : dict
            Dictionary containing 3D coordinates (in inches) for each point:
            - uca_front, uca_rear, lca_front, lca_rear
            - prod_inner, uca_outer, lca_outer, prod_outer
            - wheel_center, tie_inner, tie_outer
        external_force : array-like
            External force vector [Fx, Fy, Fz] in lbf
        R : array-like, optional
            Moment arm from wheel center to contact patch [Rx, Ry, Rz] in inches
            Default is [0, 0, 8]

        Returns:
        --------
        dict : Dictionary containing:
            - 'forces': array of member forces in lbf
            - 'force_names': list of force names
            - 'B': right-hand side vector (force/moment balance)
            - 'A': coefficient matrix
        """
        # Extract coordinates
        uca_front = np.array(coordinates['uca_front'])
        uca_rear = np.array(coordinates['uca_rear'])
        lca_front = np.array(coordinates['lca_front'])
        lca_rear = np.array(coordinates['lca_rear'])
        prod_inner = np.array(coordinates['prod_inner'])
        uca_outer = np.array(coordinates['uca_outer'])
        lca_outer = np.array(coordinates['lca_outer'])
        prod_outer = np.array(coordinates['prod_outer'])
        wheel_center = np.array(coordinates['wheel_center'])
        tie_inner = np.array(coordinates['tie_inner'])
        tie_outer = np.array(coordinates['tie_outer'])

        # Default moment arm if not provided
        if R is None:
            R = np.array([0, 0, 8])
        else:
            R = np.array(R)

        F = np.array(external_force)

        # Calculate member vectors
        vFucaf = uca_outer - uca_front
        vFucar = uca_outer - uca_rear
        vFlcaf = lca_outer - lca_front
        vFlcar = lca_outer - lca_rear
        vFprod = prod_outer - prod_inner
        vFtr = tie_outer - tie_inner

        # Calculate magnitudes
        oi1 = np.linalg.norm(vFucaf)
        oi2 = np.linalg.norm(vFucar)
        oi3 = np.linalg.norm(vFlcaf)
        oi4 = np.linalg.norm(vFlcar)
        oi5 = np.linalg.norm(vFprod)
        oi6 = np.linalg.norm(vFtr)

        # Calculate unit vectors
        uFucaf = vFucaf / oi1
        uFucar = vFucar / oi2
        uFlcaf = vFlcaf / oi3
        uFlcar = vFlcar / oi4
        uFprod = vFprod / oi5
        uFtr = vFtr / oi6

        # Moment arm vectors
        rTie = tie_outer - wheel_center
        rLCAF = lca_outer - wheel_center
        rLCAR = lca_outer - wheel_center
        rUCAF = uca_outer - wheel_center
        rUCAR = uca_outer - wheel_center
        rProd = prod_outer - wheel_center

        # Calculate cross products (u x r) for moments
        u_x_r_Tie = self._cross_product_components(uFtr, rTie)
        u_x_r_LCAF = self._cross_product_components(uFlcaf, rLCAF)
        u_x_r_LCAR = self._cross_product_components(uFlcar, rLCAR)
        u_x_r_UCAF = self._cross_product_components(uFucaf, rUCAF)
        u_x_r_UCAR = self._cross_product_components(uFucar, rUCAR)
        u_x_r_Prod = self._cross_product_components(uFprod, rProd)

        # Calculate F x R (external moment)
        FxR = self._cross_product_components(F, R)

        # Build coefficient matrix A
        A = np.array([
            # Force balance equations (first 3 rows)
            [uFtr[0], uFlcaf[0], uFlcar[0], uFucaf[0], uFucar[0], uFprod[0]],
            [uFtr[1], uFlcaf[1], uFlcar[1], uFucaf[1], uFucar[1], uFprod[1]],
            [uFtr[2], uFlcaf[2], uFlcar[2], uFucaf[2], uFucar[2], uFprod[2]],
            # Moment balance equations (last 3 rows)
            [u_x_r_Tie[0], u_x_r_LCAF[0], u_x_r_LCAR[0], u_x_r_UCAF[0], u_x_r_UCAR[0], u_x_r_Prod[0]],
            [u_x_r_Tie[1], u_x_r_LCAF[1], u_x_r_LCAR[1], u_x_r_UCAF[1], u_x_r_UCAR[1], u_x_r_Prod[1]],
            [u_x_r_Tie[2], u_x_r_LCAF[2], u_x_r_LCAR[2], u_x_r_UCAF[2], u_x_r_UCAR[2], u_x_r_Prod[2]]
        ])

        # Build right-hand side vector B
        B = np.array([F[0], F[1], F[2], FxR[0], FxR[1], FxR[2]])

        # Solve A * X = B for member forces
        X = np.linalg.solve(A, B)

        return {
            'forces': X,
            'force_names': self.force_names,
            'B': B,
            'A': A,
            'magnitudes': [oi6, oi3, oi4, oi1, oi2, oi5]
        }

    def _cross_product_components(self, u, r):
        """Calculate cross product u x r component by component"""
        return np.array([
            u[2] * r[1] - u[1] * r[2],
            u[0] * r[2] - u[2] * r[0],
            u[1] * r[0] - u[0] * r[1]
        ])

    def get_formatted_results(self, results):
        """Get formatted results as a string for display"""
        output_lines = []

        output_lines.append("=" * 70)
        output_lines.append("SUSPENSION FORCE ANALYSIS RESULTS")
        output_lines.append("=" * 70)

        output_lines.append("\nINPUT: External Forces at Tire Contact Patch")
        output_lines.append("-" * 70)
        output_lines.append("These are the forces applied to the tire from the road surface:")
        output_lines.append(f"  Fx (Longitudinal): {results['B'][0]:8.3f} lbf  [Braking/Acceleration]")
        output_lines.append(f"  Fy (Lateral):      {results['B'][1]:8.3f} lbf  [Cornering force]")
        output_lines.append(f"  Fz (Vertical):     {results['B'][2]:8.3f} lbf  [Normal/Weight load]")

        output_lines.append("\nINPUT: Applied Moments at Wheel Center")
        output_lines.append("-" * 70)
        output_lines.append("These moments arise from the offset between tire contact patch")
        output_lines.append("and wheel center (typically 8 inches vertical offset):")
        output_lines.append(f"  Mx (Roll):  {results['B'][3]:10.3f} lbf·in  [About longitudinal axis]")
        output_lines.append(f"  My (Pitch): {results['B'][4]:10.3f} lbf·in  [About lateral axis]")
        output_lines.append(f"  Mz (Yaw):   {results['B'][5]:10.3f} lbf·in  [About vertical axis]")

        output_lines.append("\n" + "=" * 70)
        output_lines.append("OUTPUT: Suspension Member Axial Loads")
        output_lines.append("=" * 70)
        output_lines.append("These are the tension (+) or compression (-) forces along each")
        output_lines.append("suspension member required to maintain equilibrium:")
        output_lines.append("-" * 70)

        member_descriptions = {
            'Ftr': 'Tie Rod',
            'Flcaf': 'Lower Control Arm (Front)',
            'Flcar': 'Lower Control Arm (Rear)',
            'Fucaf': 'Upper Control Arm (Front)',
            'Fucar': 'Upper Control Arm (Rear)',
            'Fprod': 'Push Rod'
        }

        for name, force in zip(results['force_names'], results['forces']):
            description = member_descriptions[name]
            force_type = "TENSION" if force > 0 else "COMPRESSION"
            output_lines.append(f"  {name:8s} ({description:28s}): {force:10.0f} lbf  [{force_type}]")

        output_lines.append("\n" + "=" * 70)
        output_lines.append("NOTES:")
        output_lines.append("  • Positive values = Tension (member is being pulled)")
        output_lines.append("  • Negative values = Compression (member is being pushed)")
        output_lines.append("  • These axial loads determine structural requirements for each member")
        output_lines.append("=" * 70 + "\n")

        return "\n".join(output_lines)

    def convert_data_loader_to_coordinates(self, data_loader, suspension_type='pushrod'):
        """
        Convert DataLoader format to coordinates dictionary expected by calculate_forces.

        Parameters:
        -----------
        data_loader : DataLoader
            The data loader instance
        suspension_type : str
            'basic' or 'pushrod'

        Returns:
        --------
        dict : Coordinates dictionary
        """
        if suspension_type == 'basic':
            data = data_loader.basic_data
            # Map indices to coordinate names
            # basic_data columns: UCA_FrontIN, UCA_RearIN, LCA_FrontIN, LCA_RearIN, PushRodIN, UCA_OUT, LCA_OUT, PushRodOUT, Wheel_Center
            coordinates = {
                'uca_front': np.array([data[0, 0], data[1, 0], data[2, 0]]),  # UCA_FrontIN
                'uca_rear': np.array([data[0, 1], data[1, 1], data[2, 1]]),   # UCA_RearIN
                'lca_front': np.array([data[0, 2], data[1, 2], data[2, 2]]), # LCA_FrontIN
                'lca_rear': np.array([data[0, 3], data[1, 3], data[2, 3]]),   # LCA_RearIN
                'prod_inner': np.array([data[0, 4], data[1, 4], data[2, 4]]), # PushRodIN
                'uca_outer': np.array([data[0, 5], data[1, 5], data[2, 5]]),  # UCA_OUT
                'lca_outer': np.array([data[0, 6], data[1, 6], data[2, 6]]),  # LCA_OUT
                'prod_outer': np.array([data[0, 7], data[1, 7], data[2, 7]]), # PushRodOUT
                'wheel_center': np.array([data[0, 8], data[1, 8], data[2, 8]]), # Wheel_Center
                # For tie rod, we need to add defaults or calculate from available data
                # Using some reasonable defaults based on the sample data
                'tie_inner': np.array([data[0, 8] + 4, data[1, 8] - 14, data[2, 8] - 2.4]),  # Offset from wheel center
                'tie_outer': np.array([data[0, 8] + 4, data[1, 8] - 3.625, data[2, 8] - 0.625])  # Offset from wheel center
            }
        else:  # pushrod
            data = data_loader.pushrod_data
            # pushrod_data columns: UCA_FrontIN, UCA_RearIN, LCA_FrontIN, LCA_RearIN, PushRodIN, UCA_OUT, LCA_OUT,
            #                       PushRodOUT, Cam_Hinge, Shock_OUT, Shock_IN, Wheel_Center
            coordinates = {
                'uca_front': np.array([data[0, 0], data[1, 0], data[2, 0]]),  # UCA_FrontIN
                'uca_rear': np.array([data[0, 1], data[1, 1], data[2, 1]]),   # UCA_RearIN
                'lca_front': np.array([data[0, 2], data[1, 2], data[2, 2]]), # LCA_FrontIN
                'lca_rear': np.array([data[0, 3], data[1, 3], data[2, 3]]),   # LCA_RearIN
                'prod_inner': np.array([data[0, 4], data[1, 4], data[2, 4]]), # PushRodIN
                'uca_outer': np.array([data[0, 5], data[1, 5], data[2, 5]]),  # UCA_OUT
                'lca_outer': np.array([data[0, 6], data[1, 6], data[2, 6]]),  # LCA_OUT
                'prod_outer': np.array([data[0, 7], data[1, 7], data[2, 7]]), # PushRodOUT
                'wheel_center': np.array([data[0, 11], data[1, 11], data[2, 11]]), # Wheel_Center
                # For tie rod, using offsets from wheel center
                'tie_inner': np.array([data[0, 11] + 4, data[1, 11] - 14, data[2, 11] - 2.4]),
                'tie_outer': np.array([data[0, 11] + 4, data[1, 11] - 3.625, data[2, 11] - 0.625])
            }

        return coordinates