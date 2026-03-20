"""
src/calculations/suspension_sweep.py

Runs the 3-loop closure sweep ONCE over a shock-travel range and returns
every raw kinematics quantity needed by downstream calculators:

    motion_ratio_calculator.py   →  uses shock/wheel displacement arrays
    camber_gain.py               →  uses camber_angle array
    roll_center.py               →  uses roll_center_height array

Never import this module directly from the UI — use the individual
calculator wrappers so each tab stays decoupled from sweep internals.

2D coordinate convention: all points are [Y, Z] (front-view projection).
Y positive = outboard, Z positive = up.
"""

import numpy as np
from .loop_solver import link_geom, solve_loop, line_intersect_2d


def run_sweep(shock_min: float, shock_max: float, shock_step: float,
              points: dict) -> dict:
    """
    Sweep shock travel from (nominal + shock_min) to (nominal + shock_max).

    Parameters
    ----------
    shock_min  : float  minimum shock displacement from static (inches, negative = droop)
    shock_max  : float  maximum shock displacement from static (inches, positive = bump)
    shock_step : float  step size (inches)
    points     : dict   2D [Y, Z] suspension hard-points from DataLoader.get_2d_points()
                        Required keys:
                            UCA_IN, LCA_IN, PushRodIN,
                            UCA_OUT, LCA_OUT, PushRodOUT,
                            Cam_Hinge, Shock_OUT, Shock_IN, Wheel_center

    Returns
    -------
    dict with keys:
        shock_displacements  : ndarray  shock travel at each step (in)
        wheel_displacements  : ndarray  wheel vertical travel at each step (in)
        camber_angles        : ndarray  camber angle at each step (degrees)
                                        sign convention: negative = top of tire leaning in
        roll_center_heights  : ndarray  RC height above ground at each step (in)
        uca_out_positions    : ndarray  shape (N, 2)  UCA outer position [Y, Z] at each step
        lca_out_positions    : ndarray  shape (N, 2)  LCA outer position [Y, Z] at each step
        wheel_center_positions: ndarray shape (N, 2)  wheel-centre [Y, Z] at each step
        static               : dict    static (nominal) values for reference
            shock_length         : float  nominal shock length (in)
            camber_angle         : float  static camber angle (deg)
            roll_center_height   : float  static RC height (in)
            upright_angle        : float  static upright angle (rad)
    """

    # ── Unpack hard-points ────────────────────────────────────────────────────
    UCA_IN       = np.asarray(points['UCA_IN'],       dtype=float)
    LCA_IN       = np.asarray(points['LCA_IN'],       dtype=float)
    PushRodIN    = np.asarray(points['PushRodIN'],    dtype=float)
    UCA_OUT      = np.asarray(points['UCA_OUT'],      dtype=float)
    LCA_OUT      = np.asarray(points['LCA_OUT'],      dtype=float)
    PushRodOUT   = np.asarray(points['PushRodOUT'],   dtype=float)
    Cam_Hinge    = np.asarray(points['Cam_Hinge'],    dtype=float)
    Shock_OUT    = np.asarray(points['Shock_OUT'],    dtype=float)
    Shock_IN     = np.asarray(points['Shock_IN'],     dtype=float)
    Wheel_center = np.asarray(points['Wheel_center'], dtype=float)

    # ── Static (nominal) geometry ─────────────────────────────────────────────

    # Loop 1: Shock → Cam rocker → chassis (LCA_IN as ground pivot)
    L_Shock,  th_Shock  = link_geom(Shock_IN,  Shock_OUT)
    L_Cam1,   th_Cam1   = link_geom(Shock_OUT, Cam_Hinge)
    L_Imag1,  th_Imag1  = link_geom(Cam_Hinge, LCA_IN)
    L_Imag2,  th_Imag2  = link_geom(LCA_IN,    Shock_IN)

    th_Cam1_solved, _ = solve_loop(
        L_Shock, L_Cam1, L_Imag1, th_Imag1, L_Imag2, th_Imag2, branch=-1
    )

    # Loop 2: Pushrod → Cam → chassis
    L_Cam2,       th_Cam2       = link_geom(Cam_Hinge,  PushRodIN)
    L_Pushrod,    th_Pushrod    = link_geom(PushRodIN,  PushRodOUT)
    L_ChastoPush, th_ChastoPush = link_geom(PushRodOUT, LCA_IN)
    L_Imag,       th_Imag       = link_geom(LCA_IN,     Cam_Hinge)

    delta_cam = th_Cam2 - th_Cam1_solved   # fixed angle in rocker body

    th_Pushrod_solved, th_ChastoPush_solved = solve_loop(
        L_ChastoPush, L_Pushrod, L_Cam2, th_Cam2, L_Imag, th_Imag, branch=1
    )

    # Loop 3: Control arms + upright (4-bar)
    L_UCA,           th_UCA           = link_geom(UCA_IN,  UCA_OUT)
    L_upright,       th_upright       = link_geom(UCA_OUT, LCA_OUT)
    L_LCA,           th_LCA_geom     = link_geom(LCA_OUT, LCA_IN)
    L_chassis_cross, th_chassis_cross = link_geom(LCA_IN,  UCA_IN)

    # Wheel-centre offset vector, fixed in the upright body frame
    upright_vec_static     = Wheel_center - LCA_OUT
    upright_length_wc      = np.linalg.norm(upright_vec_static)
    upright_angle_wc_static = np.arctan2(upright_vec_static[1], upright_vec_static[0])

    # Static camber: angle of upright from vertical (π/2 from horizontal)
    # Negative = top leaning inboard (conventional FSAE sign)
    static_camber_deg = np.degrees(th_upright - np.pi / 2)

    # Static roll centre
    static_rc = _compute_roll_center(UCA_IN, LCA_IN, UCA_OUT, LCA_OUT)

    # ── Sweep ─────────────────────────────────────────────────────────────────
    shock_range = np.arange(
        L_Shock + shock_min,
        L_Shock + shock_max + shock_step,
        shock_step,
    )

    shock_displacements   = []
    wheel_displacements   = []
    camber_angles         = []
    roll_center_heights   = []
    uca_out_positions     = []
    lca_out_positions     = []
    wheel_center_positions = []

    for L_Shock_vary in shock_range:

        # Loop 1 at new shock length
        th_Cam1_new, _ = solve_loop(
            L_Shock_vary, L_Cam1, L_Imag1, th_Imag1, L_Imag2, th_Imag2, branch=-1
        )

        # Cam arm rotates rigidly — update th_Cam2
        th_Cam2_new = th_Cam1_new + delta_cam

        # Loop 2 at new cam angle
        th_Pushrod_new, th_ChastoPush_new = solve_loop(
            L_ChastoPush, L_Pushrod, L_Cam2, th_Cam2_new, L_Imag, th_Imag, branch=1
        )

        # LCA angle is now determined by Loop 2 output
        th_LCA = th_ChastoPush_new

        # Loop 3: find new UCA angle and upright angle
        th_UCA_new, th_upright_new = solve_loop(
            L_upright, L_UCA, L_chassis_cross, th_chassis_cross, L_LCA, th_LCA, branch=1
        )

        # Reconstruct joint positions from UCA_IN outward
        P_UCA_OUT_new = UCA_IN + L_UCA * np.array([
            np.cos(th_UCA_new), np.sin(th_UCA_new)
        ])
        P_LCA_OUT_new = P_UCA_OUT_new + L_upright * np.array([
            np.cos(th_upright_new), np.sin(th_upright_new)
        ])

        # Wheel centre: upright-frame offset rotated to new upright angle
        upright_angle_new = th_upright_new + (upright_angle_wc_static - th_upright)
        WC_new = P_LCA_OUT_new + upright_length_wc * np.array([
            np.cos(upright_angle_new), np.sin(upright_angle_new)
        ])

        # ── Store quantities ─────────────────────────────────────────────────
        shock_displacements.append(L_Shock_vary - L_Shock)
        wheel_displacements.append(WC_new[1] - Wheel_center[1])

        # Camber: upright deviation from vertical (negative = top inboard)
        camber_deg = np.degrees(th_upright_new - th_upright)  # change from static only
        camber_angles.append(camber_deg)

        # Roll centre at this configuration
        rc = _compute_roll_center(UCA_IN, LCA_IN, P_UCA_OUT_new, P_LCA_OUT_new)
        roll_center_heights.append(rc if rc is not None else float('nan'))

        uca_out_positions.append(P_UCA_OUT_new.copy())
        lca_out_positions.append(P_LCA_OUT_new.copy())
        wheel_center_positions.append(WC_new.copy())

    # ── Package results ───────────────────────────────────────────────────────
    return {
        'shock_displacements'   : np.array(shock_displacements),
        'wheel_displacements'   : np.array(wheel_displacements),
        'camber_angles'         : np.array(camber_angles),
        'roll_center_heights'   : np.array(roll_center_heights),
        'uca_out_positions'     : np.array(uca_out_positions),
        'lca_out_positions'     : np.array(lca_out_positions),
        'wheel_center_positions': np.array(wheel_center_positions),
        'static': {
            'shock_length'       : L_Shock,
            'camber_angle'       : static_camber_deg,
            'roll_center_height' : static_rc,
            'upright_angle'      : th_upright,
        },
    }


# ── Private geometry helper ───────────────────────────────────────────────────

def _compute_roll_center(UCA_IN, LCA_IN, UCA_OUT_pos, LCA_OUT_pos):
    """
    Instant-centre roll-centre calculation (2D front view).

    1. Find IC = intersection of UCA and LCA extended lines.
    2. RC = intersection of IC → contact-patch line with vehicle centreline (Y=0).

    Returns RC height (Z) or None for degenerate geometry.
    """
    d_uca = UCA_OUT_pos - UCA_IN
    d_lca = LCA_OUT_pos - LCA_IN

    IC = line_intersect_2d(UCA_IN, d_uca, LCA_IN, d_lca)
    if IC is None:
        return None

    # Contact patch is directly below the wheel (Z = 0).
    # Lateral position approximated as LCA_OUT Y coordinate.
    contact_patch = np.array([LCA_OUT_pos[0], 0.0])
    d_ic_cp = contact_patch - IC

    if abs(d_ic_cp[0]) < 1e-10:
        return 0.0   # IC directly above contact patch → RC at ground

    # Intersect IC→CP line with centreline Y = 0
    t = (0.0 - IC[0]) / d_ic_cp[0]
    return float(IC[1] + t * d_ic_cp[1])
