"""
src/calculations/camber_gain.py

Calculates camber angle vs wheel travel by pulling the camber_angles
column from the shared suspension sweep.

Sign convention (FSAE standard):
    Negative camber = top of tire leaning inboard (toward centreline).
    Camber gain in bump is typically negative (more negative camber as
    the wheel moves up) — desirable for cornering grip.

Camber gain (deg/in) is reported as d(camber)/d(wheel_travel), so a
negative number means the tire gains negative camber in bump.
"""

import numpy as np
from .suspension_sweep import run_sweep


class CamberGainCalculator:

    def calculate_camber_gain(self, shock_min, shock_max, shock_step,
                              points, static_camber=0.0):
        """
        Parameters
        ----------
        shock_min  : float  min shock displacement from static (in)
        shock_max  : float  max shock displacement from static (in)
        shock_step : float  step size (in)
        points     : dict   from DataLoader.get_2d_points()

        Returns
        -------
        dict
            camber_angles      : ndarray  camber angle at each step (deg)
            wheel_displacements: ndarray  wheel vertical travel at each step (in)
            camber_gain        : ndarray  d(camber)/d(wheel_travel) at midpoints (deg/in)
            wheel_travel_mid   : ndarray  wheel travel at each midpoint (in)
            avg_camber_gain    : float    mean camber gain over sweep (deg/in)
            static_camber      : float    static (nominal) camber angle (deg)
        """
        sweep = run_sweep(shock_min, shock_max, shock_step, points)

        camber = sweep['camber_angles'] + static_camber  # shift by known static
        wheel  = sweep['wheel_displacements']

        d_camber = np.diff(camber)
        d_wheel  = np.diff(wheel)

        with np.errstate(divide='ignore', invalid='ignore'):
            camber_gain = np.where(np.abs(d_wheel) > 1e-9,
                                   d_camber / d_wheel,
                                   np.nan)

        wheel_travel_mid = wheel[:-1] + d_wheel / 2
        avg_camber_gain  = float(np.nanmean(camber_gain))

        return {
            'camber_angles'     : camber,
            'wheel_displacements': wheel,
            'camber_gain'       : camber_gain,
            'wheel_travel_mid'  : wheel_travel_mid,
            'avg_camber_gain'   : avg_camber_gain,
            'static_camber'     : static_camber,
        }
