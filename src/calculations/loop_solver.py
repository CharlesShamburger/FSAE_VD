"""
src/calculations/loop_solver.py

Pure 2D loop-closure math used by all kinematics calculators.
No sweep logic lives here — just geometry primitives.

All inputs/outputs use [Y, Z] 2D coordinates (front-view projection).
"""

import numpy as np


def link_geom(P1, P2):
    """
    Return (length, angle_from_horizontal) for link P1 → P2.

    Parameters
    ----------
    P1, P2 : array-like, shape (2,)  [Y, Z]

    Returns
    -------
    L     : float  link length
    theta : float  angle from horizontal (radians)
    """
    dy = P2[0] - P1[0]
    dz = P2[1] - P1[1]
    L  = np.sqrt(dy**2 + dz**2)
    theta = np.arctan2(dz, dy)
    return L, theta


def solve_loop(L_input, L_known1, L_known2, th_known2,
               L_known3, th_known3, branch=1):
    """
    Canfield 2-unknown 4-bar loop solver (generalised).

    Solves the loop:
        L_input * e^(j*th_unknown2) + L_known1 * e^(j*th_unknown1)
            = L_known2 * e^(j*th_known2) + L_known3 * e^(j*th_known3)

    Parameters
    ----------
    L_input   : float  the driven/input link length (e.g. shock)
    L_known1  : float  the first unknown-angle link (e.g. rocker arm)
    L_known2  : float  first known link length
    th_known2 : float  first known link angle (rad)
    L_known3  : float  second known link length
    th_known3 : float  second known link angle (rad)
    branch    : +1 or -1  selects assembly branch

    Returns
    -------
    th_unknown1 : float  angle of L_known1 link (rad), or 5.0 on no-solution
    th_unknown2 : float  angle of L_input  link (rad), or 5.0 on no-solution

    Notes
    -----
    Returns the sentinel value 5.0 (≫ any physical angle) when the
    discriminant is negative, i.e. the requested configuration is
    geometrically unreachable.
    """
    rkx = L_known2 * np.cos(th_known2) + L_known3 * np.cos(th_known3)
    rky = L_known2 * np.sin(th_known2) + L_known3 * np.sin(th_known3)
    rk  = np.sqrt(rkx**2 + rky**2)

    a = L_known1**2 - L_input**2 - rk**2 + 2 * L_input * rkx
    b = -4 * L_input * rky
    c =  L_known1**2 - L_input**2 - rk**2 - 2 * L_input * rkx

    disc = b**2 - 4 * a * c
    if disc < 0:
        return 5.0, 5.0

    t           = (-b + branch * np.sqrt(disc)) / (2 * a)
    th_unknown2 = 2 * np.arctan(t)
    th_unknown1 = np.arctan2(
        (-L_input * np.sin(th_unknown2) - rky) / L_known1,
        (-L_input * np.cos(th_unknown2) - rkx) / L_known1,
    )
    return th_unknown1, th_unknown2


def line_intersect_2d(P1, d1, P2, d2):
    """
    Intersection of two 2D lines defined as point + direction.

    Line 1: P1 + t1 * d1
    Line 2: P2 + t2 * d2

    Parameters
    ----------
    P1, P2 : array-like (2,)  points on each line
    d1, d2 : array-like (2,)  direction vectors (need not be unit)

    Returns
    -------
    intersection : ndarray (2,)  [Y, Z] of intersection, or None if parallel
    """
    P1, d1, P2, d2 = (np.asarray(x, dtype=float) for x in (P1, d1, P2, d2))
    A = np.array([[d1[0], -d2[0]],
                  [d1[1], -d2[1]]])
    if abs(np.linalg.det(A)) < 1e-10:
        return None
    t = np.linalg.solve(A, P2 - P1)
    return P1 + t[0] * d1
