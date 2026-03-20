"""
src/calculations/roll_center.py

Calculates roll-centre height vs wheel travel using the instant-centre
method (2D front-view projection).

Theory
------
The instant centre (IC) of the suspension is the intersection of the
upper and lower control arm lines extended to meet.  The roll centre is
the intersection of the line from IC to the tyre contact patch with the
vehicle centreline (Y = 0).

A roll centre above ground produces a jacking force component under
lateral load.  FSAE targets are typically 0–3 in above ground at static,
with modest migration through travel.
"""

import numpy as np
from .suspension_sweep import run_sweep


class RollCenterCalculator:

    def calculate_roll_center(self, shock_min: float, shock_max: float,
                              shock_step: float, points: dict) -> dict:
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
            roll_center_heights : ndarray  RC height at each step (in above ground)
            wheel_displacements : ndarray  wheel vertical travel at each step (in)
            rc_migration        : ndarray  change in RC height from static (in)
            static_rc_height    : float    static (nominal) RC height (in)
            avg_rc_height       : float    mean RC height over sweep (in)
        """
        sweep = run_sweep(shock_min, shock_max, shock_step, points)

        rc     = sweep['roll_center_heights']
        wheel  = sweep['wheel_displacements']
        static = sweep['static']['roll_center_height']

        rc_migration = rc - (static if static is not None else 0.0)

        return {
            'roll_center_heights': rc,
            'wheel_displacements': wheel,
            'rc_migration'       : rc_migration,
            'static_rc_height'   : static,
            'avg_rc_height'      : float(np.nanmean(rc)),
        }
