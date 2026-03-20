"""
src/vehicle_params.py

Central repository for all vehicle parameters used across the app.
Edit this file to update vehicle configuration — changes propagate to all tabs.

Units are noted in comments. All linear dimensions in INCHES unless noted.
"""


class VehicleParams:

    # ── DIMENSIONS ────────────────────────────────────────────────────────────
    WHEELBASE           = 0        # in  | front axle to rear axle center
    FRONT_TRACK_WIDTH   = 0        # in  | center-to-center of front tires
    REAR_TRACK_WIDTH    = 0        # in  | center-to-center of rear tires
    FRONT_RIDE_HEIGHT   = 0        # in  | chassis to ground at front
    REAR_RIDE_HEIGHT    = 0        # in  | chassis to ground at rear

    # ── CENTER OF GRAVITY ─────────────────────────────────────────────────────
    CG_HEIGHT           = 0        # in  | CG height above ground (estimated)
    CG_DIST_FROM_FRONT  = 0        # in  | longitudinal CG position from front axle
    # Derived: CG_DIST_FROM_REAR = WHEELBASE - CG_DIST_FROM_FRONT

    # ── WEIGHT ────────────────────────────────────────────────────────────────
    TOTAL_WEIGHT        = 0        # lbf | car + driver, fully fueled
    DRIVER_WEIGHT       = 0        # lbf | driver only
    FRONT_WEIGHT_DIST   = 0        # %   | e.g. 0.45 = 45% front (as a decimal)
    # Derived corner weights (all lbf):
    # FRONT_CORNER = TOTAL_WEIGHT * FRONT_WEIGHT_DIST / 2
    # REAR_CORNER  = TOTAL_WEIGHT * (1 - FRONT_WEIGHT_DIST) / 2

    FRONT_UNSPRUNG_MASS = 0        # lbf | per corner: upright, hub, brake, wheel, tire
    REAR_UNSPRUNG_MASS  = 0        # lbf | per corner: same as above (higher with live axle)

    # ── TIRE ──────────────────────────────────────────────────────────────────
    TIRE_MODEL          = ""       # str | e.g. "Hoosier 43075 16x7.5-10 LCO"
    TIRE_DIAMETER       = 0        # in  | outer diameter (unloaded)
    TIRE_WIDTH          = 0        # in  | section width
    TIRE_LOADED_RADIUS  = 0        # in  | center to ground under load
                                   #     | used as moment arm in load conditions tab
                                   #     | currently hardcoded as 8.0 in force_calculator.py
    TIRE_PRESSURE_MIN   = 0        # psi | minimum operating pressure
    TIRE_PRESSURE_MAX   = 0        # psi | maximum operating pressure
    TIRE_PRESSURE_TARGET= 0        # psi | nominal race pressure

    # Pacejka fit results (update after running tire analysis tab)
    TIRE_PACEJKA_D1     = 0        # --  | peak force coefficient (load independent)
    TIRE_PACEJKA_D2     = 0        # --  | peak force coefficient (load dependent)
    TIRE_PACEJKA_B      = 0        # --  | stiffness factor
    TIRE_PACEJKA_C      = 0        # --  | shape factor
    TIRE_PEAK_SLIP_ANGLE= 0        # deg | optimal slip angle at nominal corner load
    TIRE_FRICTION_COEFF = 0        # --  | peak FY/FZ at nominal corner load

    # ── SUSPENSION TARGETS — FRONT ────────────────────────────────────────────
    FRONT_MOTION_RATIO_TARGET   = 0    # --  | target shock travel / wheel travel
    FRONT_ROLL_CENTER_TARGET    = 0    # in  | target RC height above ground
    FRONT_CAMBER_GAIN_TARGET    = 0    # deg/in | target negative camber gain in bump
    FRONT_STATIC_CAMBER         = 0    # deg | static camber setting (negative = top in)
    FRONT_STATIC_TOE            = 0    # deg | static toe (positive = toe in)
    FRONT_ANTI_DIVE_TARGET      = 0    # %   | e.g. 0.30 = 30% anti-dive

    # ── SUSPENSION TARGETS — REAR ─────────────────────────────────────────────
    REAR_MOTION_RATIO_TARGET    = 0    # --  | target shock travel / wheel travel
    REAR_ROLL_CENTER_TARGET     = 0    # in  | target RC height above ground
    REAR_CAMBER_GAIN_TARGET     = 0    # deg/in | target negative camber gain in bump
    REAR_STATIC_CAMBER          = 0    # deg | static camber (negative = top in)
    REAR_STATIC_TOE             = 0    # deg | static toe (positive = toe in, recommended for IRS)
    REAR_ANTI_SQUAT_TARGET      = 0    # %   | e.g. 0.65 = 65% anti-squat under acceleration

    # ── SPRINGS & DAMPERS ─────────────────────────────────────────────────────
    FRONT_SPRING_RATE   = 0        # lb/in | spring rate at the coilover
    REAR_SPRING_RATE    = 0        # lb/in | spring rate at the coilover
    FRONT_DAMPER_STROKE = 0        # in    | total available damper travel
    REAR_DAMPER_STROKE  = 0        # in    | total available damper travel

    # Derived wheel rates (lb/in) — calculated from spring rate and motion ratio:
    # FRONT_WHEEL_RATE = FRONT_SPRING_RATE * FRONT_MOTION_RATIO_TARGET**2
    # REAR_WHEEL_RATE  = REAR_SPRING_RATE  * REAR_MOTION_RATIO_TARGET**2

    # ── BRAKES ────────────────────────────────────────────────────────────────
    BRAKE_BIAS          = 0        # %   | front brake bias e.g. 0.60 = 60% front
    ROTOR_DIAMETER_FRONT= 0        # in  | front rotor outer diameter
    ROTOR_DIAMETER_REAR = 0        # in  | rear rotor outer diameter

    # ── AERODYNAMICS (if applicable) ──────────────────────────────────────────
    AERO_ENABLED        = False    # bool | set True if running aero package
    DOWNFORCE_AT_60MPH  = 0        # lbf | total downforce at 60 mph (if known)
    AERO_BALANCE        = 0        # %   | front aero balance e.g. 0.45 = 45% front

    # ── DRIVETRAIN ────────────────────────────────────────────────────────────
    DRIVETRAIN          = "RWD"       # str | e.g. "RWD", "AWD"
    FINAL_DRIVE_RATIO   = 0        # --  | overall final drive ratio
    ENGINE_MAX_TORQUE   = 0        # lb·ft | peak engine torque

    # ── HELPER METHODS ────────────────────────────────────────────────────────
    @classmethod
    def front_corner_weight(cls):
        """Calculate front corner weight in lbf"""
        return cls.TOTAL_WEIGHT * cls.FRONT_WEIGHT_DIST / 2

    @classmethod
    def rear_corner_weight(cls):
        """Calculate rear corner weight in lbf"""
        return cls.TOTAL_WEIGHT * (1 - cls.FRONT_WEIGHT_DIST) / 2

    @classmethod
    def front_wheel_rate(cls):
        """Calculate front wheel rate in lb/in"""
        return cls.FRONT_SPRING_RATE * cls.FRONT_MOTION_RATIO_TARGET ** 2

    @classmethod
    def rear_wheel_rate(cls):
        """Calculate rear wheel rate in lb/in"""
        return cls.REAR_SPRING_RATE * cls.REAR_MOTION_RATIO_TARGET ** 2

    @classmethod
    def cg_dist_from_rear(cls):
        """Calculate longitudinal CG distance from rear axle in inches"""
        return cls.WHEELBASE - cls.CG_DIST_FROM_FRONT

    @classmethod
    def print_summary(cls):
        """Print a summary of key vehicle parameters to console"""
        print("=" * 50)
        print("VEHICLE PARAMETERS SUMMARY")
        print("=" * 50)
        print(f"  Wheelbase:            {cls.WHEELBASE} in")
        print(f"  Front track:          {cls.FRONT_TRACK_WIDTH} in")
        print(f"  Rear track:           {cls.REAR_TRACK_WIDTH} in")
        print(f"  Total weight:         {cls.TOTAL_WEIGHT} lbf")
        print(f"  CG height:            {cls.CG_HEIGHT} in")
        print(f"  Front corner weight:  {cls.front_corner_weight()} lbf")
        print(f"  Rear corner weight:   {cls.rear_corner_weight()} lbf")
        print(f"  Front wheel rate:     {cls.front_wheel_rate()} lb/in")
        print(f"  Rear wheel rate:      {cls.rear_wheel_rate()} lb/in")
        print(f"  Tire:                 {cls.TIRE_MODEL}")
        print(f"  Tire pressure target: {cls.TIRE_PRESSURE_TARGET} psi")
        print("=" * 50)