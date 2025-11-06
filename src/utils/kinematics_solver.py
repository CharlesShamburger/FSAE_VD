import numpy as np
from scipy.optimize import fsolve
from typing import Tuple, Optional, List


def link_geometry(P1: np.ndarray, P2: np.ndarray) -> Tuple[float, float]:
    """
    Calculate length and angle of a link between two points.

    Args:
        P1: First point [y, z] in mm
        P2: Second point [y, z] in mm

    Returns:
        L: Length of link (mm)
        theta: Angle from horizontal (radians)
    """
    dy = P2[0] - P1[0]
    dz = P2[1] - P1[1]

    L = np.sqrt(dy ** 2 + dz ** 2)
    theta = np.arctan2(dz, dy)

    return L, theta


def solve_2d_loop(r1: float, theta1: float,
                  r2: float, theta2: float,
                  uk1: float, uk2: float,
                  th0: Optional[Tuple[float, float]] = None) -> Tuple[float, float]:
    """
    Solve a 2D four-bar loop closure with two unknown angles.

    Loop equation: r1*exp(i*theta1) + r2*exp(i*theta2) + uk1*exp(i*theta_uk1) + uk2*exp(i*theta_uk2) = 0

    Args:
        r1, theta1: Known link 1 (length, angle)
        r2, theta2: Known link 2 (length, angle)
        uk1: Unknown link 1 length
        uk2: Unknown link 2 length
        th0: Initial guess for unknown angles [theta_uk1, theta_uk2]

    Returns:
        theta_uk1: Solved angle for unknown link 1 (radians)
        theta_uk2: Solved angle for unknown link 2 (radians)

    Raises:
        RuntimeError: If solver fails to converge
    """
    if th0 is None:
        th0 = [0.0, 0.0]

    # Define loop closure equations
    def loop_equations(x):
        theta_uk1, theta_uk2 = x

        # X component (horizontal)
        eq1 = (r1 * np.cos(theta1) +
               r2 * np.cos(theta2) +
               uk1 * np.cos(theta_uk1) +
               uk2 * np.cos(theta_uk2))

        # Y component (vertical)
        eq2 = (r1 * np.sin(theta1) +
               r2 * np.sin(theta2) +
               uk1 * np.sin(theta_uk1) +
               uk2 * np.sin(theta_uk2))

        return [eq1, eq2]

    # Solve using fsolve
    solution, info, ier, msg = fsolve(loop_equations, th0, full_output=True)

    if ier != 1:
        raise RuntimeError(f"Loop solver failed to converge: {msg}")

    theta_uk1, theta_uk2 = solution

    return theta_uk1, theta_uk2


class PushrodKinematics:
    """
    Solves pushrod suspension kinematics using sequential loop closure.
    """

    def __init__(self, pushrod_data: np.ndarray):
        """
        Initialize with pushrod suspension geometry data.

        Args:
            pushrod_data: 3xN array where rows are [X, Y, Z] and columns are points
        """
        self.data = pushrod_data

        # Extract Y-Z coordinates (2D front view)
        self.coords_2d = pushrod_data[1:3, :]  # Rows 1,2 = Y,Z

        # Calculate midpoints for dual chassis mounts
        self.UCA_IN = (self.coords_2d[:, 0] + self.coords_2d[:, 1]) / 2  # Avg of indices 0,1
        self.LCA_IN = (self.coords_2d[:, 2] + self.coords_2d[:, 3]) / 2  # Avg of indices 2,3

        # Single mounting points
        self.PushRodIN = self.coords_2d[:, 4]
        self.UCA_OUT = self.coords_2d[:, 5]
        self.LCA_OUT = self.coords_2d[:, 6]
        self.PushRodOUT = self.coords_2d[:, 7]
        self.Cam_Hinge = self.coords_2d[:, 8]
        self.Shock_OUT = self.coords_2d[:, 9]
        self.Shock_IN = self.coords_2d[:, 10]
        self.Wheel_Center = self.coords_2d[:, 11]  # INDEX 11 (column M in Excel)

        # Calculate reference geometry
        self._setup_reference_geometry()

    def _setup_reference_geometry(self):
        """Calculate all reference link lengths and angles."""
        # Shock
        self.L_Shock_ref, self.th_Shock = link_geometry(self.Shock_IN, self.Shock_OUT)

        # Loop 1 links
        self.L_Cam1, self.th_Cam1_ref = link_geometry(self.Shock_OUT, self.Cam_Hinge)
        self.L_Imag1, self.th_Imag1_ref = link_geometry(self.Cam_Hinge, self.LCA_IN)
        self.L_Imag2, self.th_Imag2 = link_geometry(self.Shock_IN, self.LCA_IN)

        # Loop 2 links
        self.L_Cam2, self.th_Cam2_ref = link_geometry(self.Cam_Hinge, self.PushRodIN)
        self.L_Pushrod, self.th_Pushrod_ref = link_geometry(self.PushRodIN, self.PushRodOUT)
        self.L_ChastoPush, self.th_ChastoPush_ref = link_geometry(self.PushRodOUT, self.LCA_IN)

        # Calculate angle between cam links
        v1 = self.Shock_OUT - self.Cam_Hinge
        v2 = self.PushRodIN - self.Cam_Hinge
        self.angle_between_cams = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

        # Loop 3 links
        self.L_LCA, _ = link_geometry(self.LCA_IN, self.LCA_OUT)
        self.L_UCA, self.th_UCA_ref = link_geometry(self.UCA_IN, self.UCA_OUT)
        self.L_upright, self.th_upright_ref = link_geometry(self.LCA_OUT, self.UCA_OUT)
        self.L_chassis_cross, self.th_chassis_cross = link_geometry(self.UCA_IN, self.LCA_IN)

        # Wheel center projection
        upright_vec = self.UCA_OUT - self.LCA_OUT
        upright_unit = upright_vec / np.linalg.norm(upright_vec)
        self.proj_len_ref = np.dot(self.Wheel_Center - self.LCA_OUT, upright_unit)

        print(f"Reference shock length: {self.L_Shock_ref:.2f} mm")

    def solve_position(self, shock_compression: float) -> dict:
        """
        Solve suspension position for a given shock compression.

        Args:
            shock_compression: Shock travel in mm (positive = compression)

        Returns:
            Dictionary containing solved angles and wheel position
        """
        # New shock length
        L_Shock_input = self.L_Shock_ref - shock_compression

        # Loop 1: Shock -> Cam -> LCA_IN
        try:
            th_Cam1, th_Imag1 = solve_2d_loop(
                L_Shock_input, self.th_Shock,
                self.L_Imag2, self.th_Imag2,
                self.L_Cam1, self.L_Imag1,
                th0=[self.th_Cam1_ref, self.th_Imag1_ref]
            )
        except RuntimeError as e:
            raise RuntimeError(f"Loop 1 failed: {e}")

        # Loop 2: Cam -> Pushrod -> LCA_IN
        th_Cam2 = np.pi - (th_Cam1 + self.angle_between_cams)

        try:
            th_Pushrod, th_ChastoPush = solve_2d_loop(
                self.L_Imag1, th_Imag1,
                self.L_Cam2, th_Cam2,
                self.L_Pushrod, self.L_ChastoPush,
                th0=[self.th_Pushrod_ref, self.th_ChastoPush_ref]
            )
        except RuntimeError as e:
            raise RuntimeError(f"Loop 2 failed: {e}")

        # Loop 3: LCA -> Upright -> UCA -> Chassis
        try:
            th_UCA, th_Spindle = solve_2d_loop(
                self.L_LCA, th_ChastoPush,
                self.L_chassis_cross, self.th_chassis_cross,
                self.L_UCA, self.L_upright,
                th0=[self.th_UCA_ref, self.th_upright_ref]
            )
        except RuntimeError as e:
            raise RuntimeError(f"Loop 3 failed: {e}")

        # Calculate NEW positions of LCA_OUT and UCA_OUT based on solved angles
        LCA_OUT_new = self.LCA_IN + self.L_LCA * np.array([
            np.cos(th_ChastoPush),
            np.sin(th_ChastoPush)
        ])

        UCA_OUT_new = self.UCA_IN + self.L_UCA * np.array([
            np.cos(th_UCA),
            np.sin(th_UCA)
        ])

        # Calculate wheel center using NEW LCA_OUT position and spindle angle
        Wheel_center_current = LCA_OUT_new + self.proj_len_ref * np.array([
            np.cos(th_Spindle),
            np.sin(th_Spindle)
        ])

        # Calculate vertical displacement
        vertical_disp = Wheel_center_current[1] - self.Wheel_Center[1]

        return {
            'shock_compression': shock_compression,
            'shock_length': L_Shock_input,
            'wheel_center': Wheel_center_current,
            'vertical_displacement': vertical_disp,
            'th_Cam1': th_Cam1,
            'th_Pushrod': th_Pushrod,
            'th_UCA': th_UCA,
            'th_Spindle': th_Spindle
        }

    def sweep_shock_travel(self, travel_range: Tuple[float, float], step: float = 5.0) -> dict:
        """
        Sweep through shock travel range and calculate wheel displacements.

        Args:
            travel_range: (min, max) shock travel in mm
            step: Step size in mm

        Returns:
            Dictionary with arrays of shock_travel and vertical_displacements
        """
        shock_travel = np.arange(travel_range[0], travel_range[1] + step, step)
        vertical_disps = []
        wheel_centers = []

        for compression in shock_travel:
            try:
                result = self.solve_position(compression)
                vertical_disps.append(result['vertical_displacement'])
                wheel_centers.append(result['wheel_center'])
            except RuntimeError as e:
                print(f"Failed at compression {compression:.1f} mm: {e}")
                # Stop if solver fails
                shock_travel = shock_travel[:len(vertical_disps)]
                break

        return {
            'shock_travel': shock_travel,
            'vertical_displacements': np.array(vertical_disps),
            'wheel_centers': np.array(wheel_centers)
        }