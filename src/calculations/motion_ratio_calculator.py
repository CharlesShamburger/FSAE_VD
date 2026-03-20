"""
src/calculations/motion_ratio_calculator.py

Calculates motion ratio (shock travel / wheel travel) by pulling
the relevant columns from the shared suspension sweep.

Kept as a class to preserve the existing KinematicsTab interface.
"""

import numpy as np
from .suspension_sweep import run_sweep


class MotionRatioCalculator:

    def calculate_motion_ratio(self, shock_min: float, shock_max: float,
                               shock_step: float, points: dict) -> dict:
        """
        Parameters
        ----------
        shock_min  : float  min shock displacement from static (in), e.g. -1.5
        shock_max  : float  max shock displacement from static (in), e.g.  1.5
        shock_step : float  step size (in), e.g. 0.1
        points     : dict   from DataLoader.get_2d_points()

        Returns
        -------
        dict
            avg_motion_ratio   : float   mean MR over sweep
            shock_displacements: ndarray per-step shock displacement (in)
            wheel_displacements: ndarray per-step wheel vertical travel (in)
            motion_ratio       : ndarray MR at each interval midpoint
            wheel_travel_mid   : ndarray wheel travel at each interval midpoint (in)
            shock_step         : float   step size used
        """
        sweep = run_sweep(shock_min, shock_max, shock_step, points)

        shock_disp = sweep['shock_displacements']
        wheel_disp = sweep['wheel_displacements']

        d_shock = np.diff(shock_disp)
        d_wheel = np.diff(wheel_disp)

        with np.errstate(divide='ignore', invalid='ignore'):
            motion_ratio = np.where(np.abs(d_wheel) > 1e-9,
                                    d_shock / d_wheel,
                                    np.nan)

        wheel_travel_mid = wheel_disp[:-1] + d_wheel / 2
        avg_motion_ratio = float(np.nanmean(motion_ratio))

        return {
            'avg_motion_ratio'   : avg_motion_ratio,
            'shock_displacements': shock_disp,
            'wheel_displacements': wheel_disp,
            'motion_ratio'       : motion_ratio,
            'wheel_travel_mid'   : wheel_travel_mid,
            'shock_step'         : shock_step,
        }
