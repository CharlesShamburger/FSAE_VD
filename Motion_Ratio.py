import numpy as np
import matplotlib.pyplot as plt


def link_geom(P1, P2):
    """Calculate link length and angle from horizontal."""
    dy = P2[0] - P1[0]
    dz = P2[1] - P1[1]
    L = np.sqrt(dy ** 2 + dz ** 2)
    theta = np.arctan2(dz, dy)
    return L, theta


def solve_loop1_general(L_Input, L_Known1, L_Known2, th_Known2, L_Known3, th_Known3, branch=1):
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


# --- Define 2D Suspension Coordinates (Y-Z Plane) ---
UCA_IN = np.array([9.812, 8.875])
LCA_IN = np.array([10, 4])
PushRodIN = np.array([8, 14.75])
UCA_OUT = np.array([19, 11.875])
LCA_OUT = np.array([20.625, 5.125])
PushRodOUT = np.array([20, 5])
Cam_Hinge = np.array([6.5, 13])
Shock_OUT = np.array([5, 15])
Shock_IN = np.array([1, 12])
Wheel_center = np.array([24, 8.5])

branch = 1

# --- Calculate initial geometry ---
print("=== INITIAL GEOMETRY ===")

# Loop 1: Shock system
L_Shock, th_Shock = link_geom(Shock_IN, Shock_OUT)
print(f"Original Shock: Length = {L_Shock:.3f} in, Angle = {np.rad2deg(th_Shock):.2f} deg")

L_Cam1, th_Cam1 = link_geom(Shock_OUT, Cam_Hinge)
print(f"Cam1: Length = {L_Cam1:.3f} in, Angle = {np.rad2deg(th_Cam1):.2f} deg")

L_Imag1, th_Imag1 = link_geom(Cam_Hinge, LCA_IN)
L_Imag2, th_Imag2 = link_geom(LCA_IN, Shock_IN)

# Solve Loop 1
th_Cam1_solved, th_Shock_solved = solve_loop1_general(
    L_Shock, L_Cam1, L_Imag1, th_Imag1, L_Imag2, th_Imag2, branch=-1
)
print(f"th_Cam1 (Cam angle)   = {np.rad2deg(th_Cam1_solved):.2f} deg")
print(f"th_Shock (Shock angle) = {np.rad2deg(th_Shock_solved):.2f} deg\n")

# Loop 2: Pushrod system
L_Cam2, th_Cam2 = link_geom(Cam_Hinge, PushRodIN)
L_Pushrod, th_Pushrod = link_geom(PushRodIN, PushRodOUT)
L_ChastoPush, th_ChastoPush = link_geom(PushRodOUT, LCA_IN)
L_Imag, th_Imag = link_geom(LCA_IN, Cam_Hinge)

delta_cam = th_Cam2 - th_Cam1_solved  # Fixed angle between cam links

# Solve Loop 2
th_Pushrod_solved, th_ChastoPush_solved = solve_loop1_general(
    L_ChastoPush, L_Pushrod, L_Cam2, th_Cam2, L_Imag, th_Imag, branch=1
)
print(f"th_Pushrod   = {np.rad2deg(th_Pushrod_solved):.2f} deg")
print(f"th_ChastoPush = {np.rad2deg(th_ChastoPush_solved):.2f} deg\n")

# Loop 3: Control arms
L_UCA, th_UCA = link_geom(UCA_IN, UCA_OUT)
L_upright, th_upright = link_geom(UCA_OUT, LCA_OUT)
L_LCA, th_LCA_geom = link_geom(LCA_OUT, LCA_IN)
L_chassis_cross, th_chassis_cross = link_geom(LCA_IN, UCA_IN)

# Calculate wheel center reference
upright_vector_static = Wheel_center - LCA_OUT
upright_length_wc = np.linalg.norm(upright_vector_static)
upright_angle_wc = np.arctan2(upright_vector_static[1], upright_vector_static[0])

print("=== SWEEPING SHOCK TRAVEL ===")

# Preallocate arrays
shock_displacements = []
wheel_displacements = []

shock_range = np.arange(L_Shock - 1.5, L_Shock + 1.5, 0.1)

for L_Shock_vary in shock_range:
    # Loop 1 Solutions
    th_Cam1_new, th_Shock_new = solve_loop1_general(
        L_Shock_vary, L_Cam1, L_Imag1, th_Imag1, L_Imag2, th_Imag2, branch=-1
    )

    # th_Cam2 rotates with th_Cam1
    th_Cam2_new = th_Cam1_new + delta_cam

    # Loop 2 Solutions
    th_Pushrod_new, th_ChastoPush_new = solve_loop1_general(
        L_ChastoPush, L_Pushrod, L_Cam2, th_Cam2_new, L_Imag, th_Imag, branch=1
    )

    # UPDATE: th_LCA from Loop 2 solution
    th_LCA = th_ChastoPush_new

    # Loop 3 Solutions
    th_UCA_new, th_upright_new = solve_loop1_general(
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

# --- CALCULATE MOTION RATIO ---
d_shock = np.diff(shock_displacements)
d_wheel = np.diff(wheel_displacements)
motion_ratio = d_shock / d_wheel

# Wheel travel at midpoints
wheel_travel_mid = wheel_displacements[:-1] + np.diff(wheel_displacements) / 2

# Calculate statistics
avg_motion_ratio = np.mean(motion_ratio)

print("\n=== MOTION RATIO ANALYSIS ===")
print(f"Average Motion Ratio = {avg_motion_ratio:.3f} (shock travel / wheel travel)")
print(f"Interpretation: Shock moves {avg_motion_ratio:.3f} inches for every 1 inch of wheel travel")
print("HIGHER number = MORE shock travel = stiffer feeling suspension")
print("LOWER number = LESS shock travel = softer feeling suspension")

print("\n=== DATA SUMMARY ===")
print(f"Shock travel range: {shock_displacements[0]:.3f} to {shock_displacements[-1]:.3f} in")
print(f"Wheel travel range: {wheel_displacements[0]:.3f} to {wheel_displacements[-1]:.3f} in")
print(f"Motion ratio range: {motion_ratio.min():.3f} to {motion_ratio.max():.3f}")

print("\n=== DETAILED COMPARISON DATA ===")
print(f"Number of points: {len(shock_displacements)}")
print(f"Step size: {shock_range[1] - shock_range[0]:.3f}")
print("\nFirst 5 shock displacements:")
print(shock_displacements[:5])
print("\nFirst 5 wheel displacements:")
print(wheel_displacements[:5])
print("\nFirst 5 d_shock (diff):")
print(d_shock[:5])
print("\nFirst 5 d_wheel (diff):")
print(d_wheel[:5])
print("\nFirst 5 motion ratios:")
print(motion_ratio[:5])
print("\nLast 5 motion ratios:")
print(motion_ratio[-5:])
print(f"\nSum of all motion ratios: {np.sum(motion_ratio):.6f}")
print(f"Number of motion ratio points: {len(motion_ratio)}")
print(f"Average (sum/count): {np.sum(motion_ratio) / len(motion_ratio):.6f}")

# --- PLOT MOTION RATIO VS WHEEL TRAVEL ---
plt.figure(figsize=(10, 6))
plt.plot(wheel_travel_mid, motion_ratio, 'b-', linewidth=2, label='Motion Ratio')
plt.axhline(y=avg_motion_ratio, color='r', linestyle='--', linewidth=1.5,
            label=f'Avg = {avg_motion_ratio:.3f}')
plt.grid(True)
plt.xlabel('Wheel Vertical Travel (in)')
plt.ylabel('Motion Ratio (shock travel / wheel travel)')
plt.title('Motion Ratio vs Wheel Travel')
plt.legend()

# Add text box
textstr = f'Avg MR = {avg_motion_ratio:.3f}\nHigher MR → More shock travel\nLower MR → Less shock travel'
props = dict(boxstyle='round', facecolor='white', edgecolor='black', alpha=0.8)
plt.text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=10,
         verticalalignment='top', bbox=props)

plt.tight_layout()
plt.show()

print("\n=== DATA SUMMARY ===")
print(f"Shock travel range: {shock_displacements[0]:.3f} to {shock_displacements[-1]:.3f} in")
print(f"Wheel travel range: {wheel_displacements[0]:.3f} to {wheel_displacements[-1]:.3f} in")
print(f"Motion ratio range: {motion_ratio.min():.3f} to {motion_ratio.max():.3f}")

print("\n=== DETAILED COMPARISON DATA ===")
print(f"Number of points: {len(shock_displacements)}")
print(f"Step size: {shock_range[1] - shock_range[0]:.3f}")
print("\nFirst 5 shock displacements:")
print(shock_displacements[:5])
print("\nFirst 5 wheel displacements:")
print(wheel_displacements[:5])
print("\nFirst 5 d_shock (diff):")
print(d_shock[:5])
print("\nFirst 5 d_wheel (diff):")
print(d_wheel[:5])
print("\nFirst 5 motion ratios:")
print(motion_ratio[:5])
print("\nLast 5 motion ratios:")
print(motion_ratio[-5:])
print(f"\nSum of all motion ratios: {np.sum(motion_ratio):.6f}")
print(f"Number of motion ratio points: {len(motion_ratio)}")
print(f"Average (sum/count): {np.sum(motion_ratio) / len(motion_ratio):.6f}")