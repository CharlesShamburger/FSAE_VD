import numpy as np


class MotionRatioCalculator:
    """Class for calculating motion ratio of suspension system"""

    def __init__(self):
        pass

    def link_geom(self, P1, P2):
        """Calculate link length and angle from horizontal."""
        dy = P2[0] - P1[0]
        dz = P2[1] - P1[1]
        L = np.sqrt(dy ** 2 + dz ** 2)
        theta = np.arctan2(dz, dy)
        return L, theta

    def solve_loop1_general(self, L_Input, L_Known1, L_Known2, th_Known2, L_Known3, th_Known3, branch=1):
        """
        Generalized Canfield 2-unknown loop solver.

        Returns:
            th_Unknown1, th_Unknown2 (radians)
        """
        # Step 1: Resultant of known vectors
        rkx = L_Known2 * np.cos(th_Known2) + L_Known3 * np.cos(th_Known3)
        rky = L_Known2 * np.sin(th_Known2) + L_Known3 * np.sin(th_Known3)
        rk = np.sqrt(rkx ** 2 + rky ** 2)

        # Step 2: Compute a, b, c
        a = L_Known1 ** 2 - L_Input ** 2 - rk ** 2 + 2 * L_Input * rkx
        b = -4 * L_Input * rky
        c = L_Known1 ** 2 - L_Input ** 2 - rk ** 2 - 2 * L_Input * rkx

        disc = b ** 2 - 4 * a * c

        if disc >= 0:
            # Step 3: Solve for t and th_Unknown2
            t = (-b + branch * np.sqrt(disc)) / (2 * a)
            th_Unknown2 = 2 * np.arctan(t)

            # Step 4: Solve for th_Unknown1
            th_Unknown1 = np.arctan2(
                (-L_Input * np.sin(th_Unknown2) - rky) / L_Known1,
                (-L_Input * np.cos(th_Unknown2) - rkx) / L_Known1
            )
        else:
            th_Unknown2 = 5
            th_Unknown1 = 5

        return th_Unknown1, th_Unknown2

    def calculate_motion_ratio(self, shock_min, shock_max, shock_step, points):
        """Calculate motion ratio using 2D geometry"""
        # Extract points from the points dictionary
        UCA_IN = points['UCA_IN']
        LCA_IN = points['LCA_IN']
        PushRodIN = points['PushRodIN']
        UCA_OUT = points['UCA_OUT']
        LCA_OUT = points['LCA_OUT']
        PushRodOUT = points['PushRodOUT']
        Cam_Hinge = points['Cam_Hinge']
        Shock_OUT = points['Shock_OUT']
        Shock_IN = points['Shock_IN']
        Wheel_center = points['Wheel_center']

        branch = 1

        # Calculate initial geometry
        L_Shock, th_Shock = self.link_geom(Shock_IN, Shock_OUT)
        L_Cam1, th_Cam1 = self.link_geom(Shock_OUT, Cam_Hinge)
        L_Imag1, th_Imag1 = self.link_geom(Cam_Hinge, LCA_IN)
        L_Imag2, th_Imag2 = self.link_geom(LCA_IN, Shock_IN)

        # Solve Loop 1
        th_Cam1_solved, th_Shock_solved = self.solve_loop1_general(
            L_Shock, L_Cam1, L_Imag1, th_Imag1, L_Imag2, th_Imag2, branch=-1
        )

        # Loop 2: Pushrod system
        L_Cam2, th_Cam2 = self.link_geom(Cam_Hinge, PushRodIN)
        L_Pushrod, th_Pushrod = self.link_geom(PushRodIN, PushRodOUT)
        L_ChastoPush, th_ChastoPush = self.link_geom(PushRodOUT, LCA_IN)
        L_Imag, th_Imag = self.link_geom(LCA_IN, Cam_Hinge)

        delta_cam = th_Cam2 - th_Cam1_solved  # Fixed angle between cam links

        # Solve Loop 2
        th_Pushrod_solved, th_ChastoPush_solved = self.solve_loop1_general(
            L_ChastoPush, L_Pushrod, L_Cam2, th_Cam2, L_Imag, th_Imag, branch=1
        )

        # Loop 3: Control arms
        L_UCA, th_UCA = self.link_geom(UCA_IN, UCA_OUT)
        L_upright, th_upright = self.link_geom(UCA_OUT, LCA_OUT)
        L_LCA, th_LCA_geom = self.link_geom(LCA_OUT, LCA_IN)
        L_chassis_cross, th_chassis_cross = self.link_geom(LCA_IN, UCA_IN)

        # Calculate wheel center reference
        upright_vector_static = Wheel_center - LCA_OUT
        upright_length_wc = np.linalg.norm(upright_vector_static)
        upright_angle_wc = np.arctan2(upright_vector_static[1], upright_vector_static[0])

        # Sweeping shock travel
        shock_displacements = []
        wheel_displacements = []

        shock_range = np.arange(L_Shock + shock_min, L_Shock + shock_max + shock_step, shock_step)

        for L_Shock_vary in shock_range:
            # Loop 1 Solutions
            th_Cam1_new, th_Shock_new = self.solve_loop1_general(
                L_Shock_vary, L_Cam1, L_Imag1, th_Imag1, L_Imag2, th_Imag2, branch=-1
            )

            # th_Cam2 rotates with th_Cam1
            th_Cam2_new = th_Cam1_new + delta_cam

            # Loop 2 Solutions
            th_Pushrod_new, th_ChastoPush_new = self.solve_loop1_general(
                L_ChastoPush, L_Pushrod, L_Cam2, th_Cam2_new, L_Imag, th_Imag, branch=1
            )

            # UPDATE: th_LCA from Loop 2 solution
            th_LCA = th_ChastoPush_new

            # Loop 3 Solutions
            th_UCA_new, th_upright_new = self.solve_loop1_general(
                L_upright, L_UCA, L_chassis_cross, th_chassis_cross, L_LCA, th_LCA, branch=1
            )

            # Calculate new LCA_OUT position (P8)
            P6 = UCA_IN
            P7 = P6 + L_UCA * np.array([np.cos(th_UCA_new), np.sin(th_UCA_new)])
            P8 = P7 + L_upright * np.array([np.cos(th_upright_new), np.sin(th_upright_new)])

            # Wheel center calculation
            upright_angle_new = th_upright_new + (upright_angle_wc - th_upright)
            Wheel_center_new = P8 + upright_length_wc * np.array([
                np.cos(upright_angle_new), np.sin(upright_angle_new)
            ])

            # Calculate displacements
            shock_displacement = L_Shock_vary - L_Shock
            wheel_displacement_z = Wheel_center_new[1] - Wheel_center[1]

            # Store data
            shock_displacements.append(shock_displacement)
            wheel_displacements.append(wheel_displacement_z)

        # Convert to numpy arrays
        shock_displacements = np.array(shock_displacements)
        wheel_displacements = np.array(wheel_displacements)

        # Calculate motion ratio
        d_shock = np.diff(shock_displacements)
        d_wheel = np.diff(wheel_displacements)
        motion_ratio = d_shock / d_wheel

        # Wheel travel at midpoints
        wheel_travel_mid = wheel_displacements[:-1] + np.diff(wheel_displacements) / 2

        # Calculate statistics
        avg_motion_ratio = np.mean(motion_ratio)

        # Return results
        results = {
            'avg_motion_ratio': avg_motion_ratio,
            'shock_displacements': shock_displacements,
            'wheel_displacements': wheel_displacements,
            'motion_ratio': motion_ratio,
            'wheel_travel_mid': wheel_travel_mid,
            'shock_step': shock_step
        }

        return results