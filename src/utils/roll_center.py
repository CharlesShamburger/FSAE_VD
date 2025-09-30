import numpy as np
from typing import Tuple, Optional


class RollCenterCalculator:
    """
    Calculates roll center height for FSAE suspension systems.
    Uses instant center method based on control arm geometry.
    """

    def __init__(self, track_width: float = 1200.0, units: str = "mm"):
        """
        Initialize roll center calculator.

        Args:
            track_width: Distance between left and right contact patches (mm or inches)
            units: "mm" or "inches"
        """
        self.track_width = track_width
        self.units = units
        self.unit_label = "mm" if units == "mm" else "in"

    def calculate_roll_center(self, data: np.ndarray, suspension_type: str = "basic") -> dict:
        """
        Calculate roll center height and related parameters.

        Args:
            data: Suspension geometry data array (3 x N) where rows are X, Y, Z
            suspension_type: Either "basic" or "pushrod"

        Returns:
            Dictionary containing:
                - rc_height: Roll center height (mm)
                - ic_front: Front view instant center coordinates (x, y, z)
                - ic_side: Side view instant center coordinates (x, y, z)
                - swing_arm_length: Effective swing arm length (mm)
                - roll_axis_angle: Roll axis angle (degrees)
                - success: Boolean indicating if calculation was successful
                - message: Status or error message
        """
        try:
            # Extract control arm points based on suspension type
            if suspension_type == "basic":
                # Basic suspension: indices 0-3 are inboard, 5-6 are outboard
                uca_front_in = data[:, 0]  # UCA_FrontIN
                uca_rear_in = data[:, 1]  # UCA_RearIN
                lca_front_in = data[:, 2]  # LCA_FrontIN
                lca_rear_in = data[:, 3]  # LCA_RearIN
                uca_out = data[:, 5]  # UCA_OUT
                lca_out = data[:, 6]  # LCA_OUT
            else:  # pushrod
                # Pushrod suspension: same indices
                uca_front_in = data[:, 0]
                uca_rear_in = data[:, 1]
                lca_front_in = data[:, 2]
                lca_rear_in = data[:, 3]
                uca_out = data[:, 5]
                lca_out = data[:, 6]

            # Calculate instant center in front view (Y-Z plane)
            ic_front = self._calculate_instant_center_front_view(
                uca_front_in, uca_rear_in, uca_out,
                lca_front_in, lca_rear_in, lca_out
            )

            if ic_front is None:
                return {
                    'success': False,
                    'message': 'Could not calculate front view instant center (parallel control arms?)',
                    'rc_height': None,
                    'ic_front': None,
                    'ic_side': None,
                    'swing_arm_length': None,
                    'roll_axis_angle': None
                }

            # Calculate instant center in side view (X-Z plane)
            ic_side = self._calculate_instant_center_side_view(
                uca_front_in, uca_rear_in, uca_out,
                lca_front_in, lca_rear_in, lca_out
            )

            # Calculate roll center height using front view IC
            # RC is where line from IC to contact patch intersects vehicle centerline
            contact_patch_y = self.track_width / 2  # Assume right side
            contact_patch_z = 0  # Ground level

            # Line from IC to contact patch
            # RC is at Y=0 (centerline)
            if abs(ic_front[1] - contact_patch_y) < 1e-6:
                # Vertical instant center (very rare)
                rc_height = ic_front[2]
            else:
                # Linear interpolation to find Z at Y=0
                t = (0 - contact_patch_y) / (ic_front[1] - contact_patch_y)
                rc_height = contact_patch_z + t * (ic_front[2] - contact_patch_z)

            # Calculate swing arm length (distance from IC to contact patch)
            swing_arm_length = np.sqrt(
                (ic_front[1] - contact_patch_y) ** 2 +
                (ic_front[2] - contact_patch_z) ** 2
            )

            # Calculate roll axis angle (using side view IC if available)
            roll_axis_angle = 0.0
            if ic_side is not None:
                # Angle of line from ground contact to side view IC
                roll_axis_angle = np.degrees(np.arctan2(
                    ic_side[2] - contact_patch_z,
                    ic_side[0]
                ))

            return {
                'success': True,
                'message': 'Roll center calculated successfully',
                'rc_height': rc_height,
                'ic_front': ic_front,
                'ic_side': ic_side,
                'swing_arm_length': swing_arm_length,
                'roll_axis_angle': roll_axis_angle
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error calculating roll center: {str(e)}',
                'rc_height': None,
                'ic_front': None,
                'ic_side': None,
                'swing_arm_length': None,
                'roll_axis_angle': None
            }

    def _calculate_instant_center_front_view(
            self,
            uca_front_in: np.ndarray,
            uca_rear_in: np.ndarray,
            uca_out: np.ndarray,
            lca_front_in: np.ndarray,
            lca_rear_in: np.ndarray,
            lca_out: np.ndarray
    ) -> Optional[Tuple[float, float, float]]:
        """
        Calculate instant center in front view (Y-Z plane).
        This is where the upper and lower control arm axes intersect.
        """
        # Project to Y-Z plane (front view)
        # Upper control arm line
        uca_mid_in = (uca_front_in + uca_rear_in) / 2
        uca_y1, uca_z1 = uca_mid_in[1], uca_mid_in[2]
        uca_y2, uca_z2 = uca_out[1], uca_out[2]

        # Lower control arm line
        lca_mid_in = (lca_front_in + lca_rear_in) / 2
        lca_y1, lca_z1 = lca_mid_in[1], lca_mid_in[2]
        lca_y2, lca_z2 = lca_out[1], lca_out[2]

        # Find intersection of two lines in 2D
        ic_yz = self._line_intersection_2d(
            uca_y1, uca_z1, uca_y2, uca_z2,
            lca_y1, lca_z1, lca_y2, lca_z2
        )

        if ic_yz is None:
            return None

        # Use average X coordinate
        avg_x = (uca_mid_in[0] + lca_mid_in[0] + uca_out[0] + lca_out[0]) / 4

        return (avg_x, ic_yz[0], ic_yz[1])

    def _calculate_instant_center_side_view(
            self,
            uca_front_in: np.ndarray,
            uca_rear_in: np.ndarray,
            uca_out: np.ndarray,
            lca_front_in: np.ndarray,
            lca_rear_in: np.ndarray,
            lca_out: np.ndarray
    ) -> Optional[Tuple[float, float, float]]:
        """
        Calculate instant center in side view (X-Z plane).
        Used for roll axis calculation.
        """
        # Project to X-Z plane (side view)
        # Upper control arm line
        uca_mid_in = (uca_front_in + uca_rear_in) / 2
        uca_x1, uca_z1 = uca_mid_in[0], uca_mid_in[2]
        uca_x2, uca_z2 = uca_out[0], uca_out[2]

        # Lower control arm line
        lca_mid_in = (lca_front_in + lca_rear_in) / 2
        lca_x1, lca_z1 = lca_mid_in[0], lca_mid_in[2]
        lca_x2, lca_z2 = lca_out[0], lca_out[2]

        # Find intersection
        ic_xz = self._line_intersection_2d(
            uca_x1, uca_z1, uca_x2, uca_z2,
            lca_x1, lca_z1, lca_x2, lca_z2
        )

        if ic_xz is None:
            return None

        # Use average Y coordinate
        avg_y = (uca_mid_in[1] + lca_mid_in[1] + uca_out[1] + lca_out[1]) / 4

        return (ic_xz[0], avg_y, ic_xz[1])

    def _line_intersection_2d(
            self,
            x1: float, y1: float, x2: float, y2: float,
            x3: float, y3: float, x4: float, y4: float
    ) -> Optional[Tuple[float, float]]:
        """
        Find intersection point of two lines in 2D.
        Line 1: from (x1, y1) to (x2, y2)
        Line 2: from (x3, y3) to (x4, y4)

        Returns None if lines are parallel.
        """
        # Calculate denominators
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        # Check if lines are parallel
        if abs(denom) < 1e-6:
            return None

        # Calculate intersection using parametric form
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom

        # Calculate intersection point
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)

        return (x, y)

    def plot_roll_center(self, ax, data: np.ndarray, results: dict, suspension_type: str = "basic"):
        """
        Plot 2D front view of suspension with roll center visualization.

        Args:
            ax: Matplotlib axis to plot on
            data: Suspension geometry data array (3 x N)
            results: Dictionary from calculate_roll_center()
            suspension_type: Either "basic" or "pushrod"
        """
        ax.clear()

        if not results['success']:
            ax.text(0.5, 0.5, f"Error: {results['message']}",
                    ha='center', va='center', transform=ax.transAxes)
            return

        # Extract control arm points
        if suspension_type == "basic":
            uca_front_in = data[:, 0]
            uca_rear_in = data[:, 1]
            lca_front_in = data[:, 2]
            lca_rear_in = data[:, 3]
            uca_out = data[:, 5]
            lca_out = data[:, 6]
        else:  # pushrod
            uca_front_in = data[:, 0]
            uca_rear_in = data[:, 1]
            lca_front_in = data[:, 2]
            lca_rear_in = data[:, 3]
            uca_out = data[:, 5]
            lca_out = data[:, 6]

        # Calculate midpoints for inboard mounting points
        uca_mid_in = (uca_front_in + uca_rear_in) / 2
        lca_mid_in = (lca_front_in + lca_rear_in) / 2

        # Extract Y-Z coordinates (front view)
        # Upper control arm
        uca_in_y, uca_in_z = uca_mid_in[1], uca_mid_in[2]
        uca_out_y, uca_out_z = uca_out[1], uca_out[2]

        # Lower control arm
        lca_in_y, lca_in_z = lca_mid_in[1], lca_mid_in[2]
        lca_out_y, lca_out_z = lca_out[1], lca_out[2]

        # Plot control arms
        ax.plot([uca_in_y, uca_out_y], [uca_in_z, uca_out_z],
                'b-', linewidth=3, label='Upper Control Arm', marker='o', markersize=8)
        ax.plot([lca_in_y, lca_out_y], [lca_in_z, lca_out_z],
                'r-', linewidth=3, label='Lower Control Arm', marker='o', markersize=8)

        # Plot instant center if available
        if results['ic_front'] is not None:
            ic_y, ic_z = results['ic_front'][1], results['ic_front'][2]
            ax.plot(ic_y, ic_z, 'go', markersize=12, label='Instant Center', zorder=5)

            # Draw extended control arm lines to instant center
            ax.plot([uca_in_y, ic_y], [uca_in_z, ic_z],
                    'b--', linewidth=1, alpha=0.5)
            ax.plot([lca_in_y, ic_y], [lca_in_z, ic_z],
                    'r--', linewidth=1, alpha=0.5)

            # Contact patch (at tire)
            contact_y = self.track_width / 2
            contact_z = 0
            ax.plot(contact_y, contact_z, 'ks', markersize=10, label='Contact Patch')

            # Draw line from IC to contact patch
            ax.plot([ic_y, contact_y], [ic_z, contact_z],
                    'g--', linewidth=2, alpha=0.7, label='Swing Arm')

            # Plot roll center
            rc_height = results['rc_height']
            ax.plot(0, rc_height, 'r*', markersize=20, label='Roll Center', zorder=6)

            # Draw line from contact patch to roll center
            ax.plot([contact_y, 0], [contact_z, rc_height],
                    'm--', linewidth=2, alpha=0.7)

        # Draw ground line
        y_min = min(uca_in_y, lca_in_y, uca_out_y, lca_out_y) - 50
        y_max = max(uca_in_y, lca_in_y, uca_out_y, lca_out_y) + 50
        ax.plot([y_min, y_max], [0, 0], 'k-', linewidth=2, alpha=0.3, label='Ground')

        # Draw centerline
        z_min = min(lca_in_z, lca_out_z) - 50
        z_max = max(uca_in_z, uca_out_z) + 100
        ax.plot([0, 0], [z_min, z_max], 'k--', linewidth=1, alpha=0.3, label='Centerline')

        # Labels and formatting
        ax.set_xlabel(f'Y - Lateral Position ({self.unit_label})', fontsize=12)
        ax.set_ylabel(f'Z - Vertical Position ({self.unit_label})', fontsize=12)
        ax.set_title('Roll Center Analysis - Front View', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=9, framealpha=0.8)
        ax.set_aspect('equal', adjustable='box')

        # Add text annotation with key results
        if results['rc_height'] is not None:
            info_text = f"Roll Center Height: {results['rc_height']:.1f} {self.unit_label}\n"
            info_text += f"Swing Arm Length: {results['swing_arm_length']:.1f} {self.unit_label}"
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    def format_results(self, results: dict) -> str:
        """
        Format calculation results as readable text.

        Args:
            results: Dictionary from calculate_roll_center()

        Returns:
            Formatted string for display
        """
        if not results['success']:
            return f"ERROR: {results['message']}"

        output = "=" * 50 + "\n"
        output += "ROLL CENTER ANALYSIS RESULTS\n"
        output += "=" * 50 + "\n\n"

        output += f"Roll Center Height: {results['rc_height']:.2f} {self.unit_label}\n\n"

        if results['ic_front'] is not None:
            output += "Front View Instant Center:\n"
            output += f"  X: {results['ic_front'][0]:.2f} {self.unit_label}\n"
            output += f"  Y: {results['ic_front'][1]:.2f} {self.unit_label}\n"
            output += f"  Z: {results['ic_front'][2]:.2f} {self.unit_label}\n\n"

        if results['ic_side'] is not None:
            output += "Side View Instant Center:\n"
            output += f"  X: {results['ic_side'][0]:.2f} {self.unit_label}\n"
            output += f"  Y: {results['ic_side'][1]:.2f} {self.unit_label}\n"
            output += f"  Z: {results['ic_side'][2]:.2f} {self.unit_label}\n\n"

        output += f"Effective Swing Arm Length: {results['swing_arm_length']:.2f} {self.unit_label}\n"
        output += f"Roll Axis Angle: {results['roll_axis_angle']:.2f}°\n\n"

        output += "=" * 50 + "\n"
        output += "INTERPRETATION:\n"
        output += "=" * 50 + "\n"

        rc_h = results['rc_height']
        if rc_h < 0:
            output += "• Roll center is BELOW ground (may cause jacking)\n"
        elif rc_h < 50:
            output += "• Roll center is LOW (good for grip, higher roll)\n"
        elif rc_h < 150:
            output += "• Roll center is MODERATE (balanced setup)\n"
        else:
            output += "• Roll center is HIGH (less roll, potential jacking)\n"

        output += f"\n• Swing arm length affects roll stiffness\n"
        output += f"  - Longer = softer in roll\n"
        output += f"  - Current: {results['swing_arm_length']:.0f} {self.unit_label}\n"

        return output


# Example usage function
def example_usage():
    """
    Example of how to use the RollCenterCalculator with your suspension data.
    """
    # Create calculator (adjust track width to match your car)
    calculator = RollCenterCalculator(track_width=1200.0)

    # Example data (replace with your actual data from data_loader)
    # This should be your basic_data or pushrod_data array (3 x N)
    example_data = np.array([
        [0, 50, 0, 50, 100, 200, 200, 150],  # X coordinates
        [100, 80, 100, 80, 90, 300, 300, 90],  # Y coordinates
        [200, 200, 50, 50, 100, 180, 30, 50]  # Z coordinates
    ])

    # Calculate roll center
    results = calculator.calculate_roll_center(example_data, suspension_type="basic")

    # Format and print results
    output = calculator.format_results(results)
    print(output)

    # Access individual values
    if results['success']:
        print(f"\nRoll center height: {results['rc_height']:.2f} mm")


if __name__ == "__main__":
    example_usage()