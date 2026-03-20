"""
src/tabs/kinematics_tab.py

Kinematics analysis tab.  Each calculator has its own button and
produces its own plot + results text.  All three share the same
shock-travel sweep under the hood via suspension_sweep.py.
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import logging
import numpy as np

from ..calculations.motion_ratio_calculator import MotionRatioCalculator
from ..calculations.camber_gain import CamberGainCalculator
from ..calculations.roll_center import RollCenterCalculator


class KinematicsTab:
    def __init__(self, parent_notebook, basic_data, pushrod_data,
                 basic_members, pushrod_members):
        self.basic_data     = basic_data
        self.pushrod_data   = pushrod_data
        self.basic_members  = basic_members
        self.pushrod_members = pushrod_members
        self.logger = logging.getLogger(__name__)

        self.kinematics_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.kinematics_frame, text="Kinematics")

        kinematics_paned = ttk.PanedWindow(self.kinematics_frame, orient=tk.VERTICAL)
        kinematics_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        top_frame  = ttk.Frame(kinematics_paned)
        kinematics_paned.add(top_frame, weight=0)

        plot_frame = ttk.LabelFrame(kinematics_paned, text="Analysis Results", padding=5)
        kinematics_paned.add(plot_frame, weight=1)

        self.setup_controls(top_frame)
        self.setup_analysis_plot(plot_frame)

    # ── Controls ──────────────────────────────────────────────────────────────

    def setup_controls(self, parent):
        main_control_frame = ttk.Frame(parent)
        main_control_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ── Left: parameter inputs ────────────────────────────────────────────
        input_frame = ttk.LabelFrame(main_control_frame,
                                     text="Analysis Parameters", padding=10)
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        # Suspension type
        ttk.Label(input_frame, text="Suspension Type:").pack(anchor=tk.W, pady=5)
        self.suspension_type = tk.StringVar(value="pushrod")
        ttk.Radiobutton(input_frame, text="Basic Suspension",
                        variable=self.suspension_type, value="basic").pack(anchor=tk.W)
        ttk.Radiobutton(input_frame, text="Pushrod Suspension",
                        variable=self.suspension_type, value="pushrod").pack(anchor=tk.W)

        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Shock travel inputs (motion ratio / camber / RC all use these)
        ttk.Label(input_frame, text="Shock Travel Range (in):").pack(anchor=tk.W, pady=5)
        shock_frame = ttk.Frame(input_frame)
        shock_frame.pack(fill=tk.X, pady=5)

        ttk.Label(shock_frame, text="From:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.shock_min = ttk.Entry(shock_frame, width=8)
        self.shock_min.grid(row=0, column=1, padx=(0, 10))
        self.shock_min.insert(0, "-1.5")

        ttk.Label(shock_frame, text="To:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.shock_max = ttk.Entry(shock_frame, width=8)
        self.shock_max.grid(row=0, column=3)
        self.shock_max.insert(0, "1.5")

        ttk.Label(input_frame, text="Shock step size (in):").pack(anchor=tk.W, pady=(10, 5))
        self.shock_step = ttk.Entry(input_frame, width=8)
        self.shock_step.pack(anchor=tk.W)
        self.shock_step.insert(0, "0.1")

        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        #Static Camber
        ttk.Label(input_frame, text="Static Camber (deg):").pack(anchor=tk.W, pady=(10, 5))
        self.static_camber = ttk.Entry(input_frame, width=8)
        self.static_camber.pack(anchor=tk.W)
        self.static_camber.insert(0, "0.0")

        # ── Calculation buttons ───────────────────────────────────────────────
        ttk.Label(input_frame, text="Calculations:").pack(anchor=tk.W, pady=(0, 5))

        self.motion_ratio_btn = ttk.Button(
            input_frame, text="Motion Ratio",
            command=self.calculate_motion_ratio)
        self.motion_ratio_btn.pack(fill=tk.X, pady=3)

        self.camber_gain_btn = ttk.Button(
            input_frame, text="Camber Gain",
            command=self.calculate_camber_gain)
        self.camber_gain_btn.pack(fill=tk.X, pady=3)

        self.roll_center_btn = ttk.Button(
            input_frame, text="Roll Center Height",
            command=self.calculate_roll_center)
        self.roll_center_btn.pack(fill=tk.X, pady=3)

        ttk.Separator(input_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        self.run_all_btn = ttk.Button(
            input_frame, text="▶  Run All",
            command=self.run_all)
        self.run_all_btn.pack(fill=tk.X, pady=3)

        # ── Right: results text ───────────────────────────────────────────────
        results_frame = ttk.LabelFrame(main_control_frame, text="Results", padding=10)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        result_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text = tk.Text(results_frame, height=15, wrap=tk.WORD,
                                    yscrollcommand=result_scroll.set,
                                    font=("Courier", 9))
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scroll.config(command=self.results_text.yview)

        self.results_text.insert(tk.END,
            "FSAE Kinematics Analysis\n\n"
            "Select suspension type and adjust shock travel range,\n"
            "then click a calculation button.\n\n"
            "All three calculations share the same sweep loop —\n"
            "'Run All' computes everything in one pass.\n"
        )
        self.results_text.configure(state=tk.DISABLED)

    # ── Plot area ─────────────────────────────────────────────────────────────

    def setup_analysis_plot(self, parent):
        # Notebook so we can have separate tabs per result type
        self.plot_notebook = ttk.Notebook(parent)
        self.plot_notebook.pack(fill=tk.BOTH, expand=True)

        # Motion ratio plot
        mr_frame = ttk.Frame(self.plot_notebook)
        self.plot_notebook.add(mr_frame, text="Motion Ratio")
        self.mr_fig = Figure(figsize=(10, 4), dpi=100)
        self.mr_ax  = self.mr_fig.add_subplot(111)
        self.mr_canvas = FigureCanvasTkAgg(self.mr_fig, master=mr_frame)
        self.mr_canvas.draw()
        self.mr_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        tb_frame = ttk.Frame(mr_frame)
        tb_frame.pack(side=tk.BOTTOM, fill=tk.X)
        NavigationToolbar2Tk(self.mr_canvas, tb_frame).update()

        # Camber gain plot
        cg_frame = ttk.Frame(self.plot_notebook)
        self.plot_notebook.add(cg_frame, text="Camber Gain")
        self.cg_fig = Figure(figsize=(10, 4), dpi=100)
        self.cg_ax  = self.cg_fig.add_subplot(111)
        self.cg_canvas = FigureCanvasTkAgg(self.cg_fig, master=cg_frame)
        self.cg_canvas.draw()
        self.cg_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        tb_frame2 = ttk.Frame(cg_frame)
        tb_frame2.pack(side=tk.BOTTOM, fill=tk.X)
        NavigationToolbar2Tk(self.cg_canvas, tb_frame2).update()

        # Roll center plot
        rc_frame = ttk.Frame(self.plot_notebook)
        self.plot_notebook.add(rc_frame, text="Roll Center")
        self.rc_fig = Figure(figsize=(10, 4), dpi=100)
        self.rc_ax  = self.rc_fig.add_subplot(111)
        self.rc_canvas = FigureCanvasTkAgg(self.rc_fig, master=rc_frame)
        self.rc_canvas.draw()
        self.rc_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        tb_frame3 = ttk.Frame(rc_frame)
        tb_frame3.pack(side=tk.BOTTOM, fill=tk.X)
        NavigationToolbar2Tk(self.rc_canvas, tb_frame3).update()

        self._init_empty_plots()

    # ── Public calculation methods ────────────────────────────────────────────

    def calculate_motion_ratio(self):
        try:
            shock_min, shock_max, shock_step = self._get_shock_params()
            points = self._get_points()

            calc    = MotionRatioCalculator()
            results = calc.calculate_motion_ratio(shock_min, shock_max, shock_step, points)

            avg_mr       = results['avg_motion_ratio']
            shock_disp   = results['shock_displacements']
            wheel_disp   = results['wheel_displacements']
            motion_ratio = results['motion_ratio']
            wt_mid       = results['wheel_travel_mid']

            # Results text
            self.update_results(
                f"Motion Ratio Analysis\n"
                f"{'─'*40}\n"
                f"Average MR:   {avg_mr:.4f}  (shock in / wheel in)\n"
                f"  → shock moves {avg_mr:.4f} in per 1 in of wheel travel\n\n"
                f"Shock range:  {shock_disp[0]:.3f} → {shock_disp[-1]:.3f} in\n"
                f"Wheel range:  {wheel_disp[0]:.3f} → {wheel_disp[-1]:.3f} in\n"
                f"MR range:     {np.nanmin(motion_ratio):.4f} → {np.nanmax(motion_ratio):.4f}\n"
                f"Steps:        {len(shock_disp)}\n\n"
                f"Higher MR → more shock travel → stiffer feel\n"
                f"Lower  MR → less shock travel → softer feel\n"
            )

            # Plot
            self.mr_ax.clear()
            self.mr_ax.plot(wt_mid, motion_ratio, 'b-', linewidth=2, label='Motion Ratio')
            self.mr_ax.axhline(avg_mr, color='r', linestyle='--', linewidth=1.5,
                               label=f'Avg = {avg_mr:.4f}')
            self.mr_ax.set_xlabel('Wheel Vertical Travel (in)')
            self.mr_ax.set_ylabel('Motion Ratio (shock / wheel)')
            self.mr_ax.set_title('Motion Ratio vs Wheel Travel')
            self.mr_ax.legend()
            self.mr_ax.grid(True, alpha=0.3)
            self._add_textbox(self.mr_ax,
                              f'Avg MR = {avg_mr:.4f}\n'
                              f'Higher → more shock travel\n'
                              f'Lower  → less shock travel')
            self.mr_fig.tight_layout()
            self.mr_canvas.draw()

            # Switch to this plot tab
            self.plot_notebook.select(0)

        except Exception as e:
            self.logger.error(f"Motion ratio error: {e}", exc_info=True)
            self.update_results(f"Error in motion ratio:\n{e}")

    def calculate_camber_gain(self):
        try:
            shock_min, shock_max, shock_step = self._get_shock_params()
            points = self._get_points()

            calc    = CamberGainCalculator()
            static_cam = float(self.static_camber.get())
            results = calc.calculate_camber_gain(shock_min, shock_max, shock_step, points, static_camber=static_cam)

            camber      = results['camber_angles']
            wheel       = results['wheel_displacements']
            cg          = results['camber_gain']
            wt_mid      = results['wheel_travel_mid']
            avg_cg      = results['avg_camber_gain']
            static_cam  = results['static_camber']

            self.update_results(
                f"Camber Gain Analysis\n"
                f"{'─'*40}\n"
                f"Static camber:   {static_cam:+.4f} deg\n"
                f"  (neg = top inboard, FSAE convention)\n\n"
                f"Average gain:    {avg_cg:+.4f} deg/in\n"
                f"  (neg gain = more negative camber in bump — desirable)\n\n"
                f"Camber range:    {camber.min():+.4f} → {camber.max():+.4f} deg\n"
                f"Wheel range:     {wheel.min():.3f} → {wheel.max():.3f} in\n"
                f"Gain range:      {np.nanmin(cg):+.4f} → {np.nanmax(cg):+.4f} deg/in\n"
            )

            # Plot 1: camber angle vs wheel travel
            self.cg_ax.clear()
            self.cg_ax.plot(wheel, camber, 'g-', linewidth=2, label='Camber Angle')
            self.cg_ax.axhline(static_cam, color='k', linestyle=':', linewidth=1,
                               label=f'Static = {static_cam:+.3f}°')
            self.cg_ax.axvline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
            self.cg_ax.set_xlabel('Wheel Vertical Travel (in)')
            self.cg_ax.set_ylabel('Camber Angle (deg)')
            self.cg_ax.set_title('Camber Angle vs Wheel Travel')
            self.cg_ax.legend()
            self.cg_ax.grid(True, alpha=0.3)
            self._add_textbox(self.cg_ax,
                              f'Static = {static_cam:+.3f}°\n'
                              f'Avg gain = {avg_cg:+.4f} deg/in\n'
                              f'Neg gain in bump = ✓')
            self.cg_fig.tight_layout()
            self.cg_canvas.draw()

            self.plot_notebook.select(1)

        except Exception as e:
            self.logger.error(f"Camber gain error: {e}", exc_info=True)
            self.update_results(f"Error in camber gain:\n{e}")

    def calculate_roll_center(self):
        try:
            shock_min, shock_max, shock_step = self._get_shock_params()
            points = self._get_points()

            calc    = RollCenterCalculator()
            results = calc.calculate_roll_center(shock_min, shock_max, shock_step, points)

            rc_heights  = results['roll_center_heights']
            wheel       = results['wheel_displacements']
            migration   = results['rc_migration']
            static_rc   = results['static_rc_height']
            avg_rc      = results['avg_rc_height']

            static_str = f"{static_rc:.3f}" if static_rc is not None else "N/A"

            self.update_results(
                f"Roll Center Height Analysis\n"
                f"{'─'*40}\n"
                f"Static RC height:  {static_str} in above ground\n"
                f"Average RC height: {avg_rc:.3f} in\n\n"
                f"RC range:          {np.nanmin(rc_heights):.3f} → {np.nanmax(rc_heights):.3f} in\n"
                f"Migration:         {np.nanmin(migration):+.3f} → {np.nanmax(migration):+.3f} in\n"
                f"Wheel range:       {wheel.min():.3f} → {wheel.max():.3f} in\n\n"
                f"FSAE target: RC typically 0–3 in above ground at static.\n"
                f"Less RC migration through travel is generally preferred.\n"
            )

            self.rc_ax.clear()
            self.rc_ax.plot(wheel, rc_heights, 'm-', linewidth=2, label='RC Height')
            if static_rc is not None:
                self.rc_ax.axhline(static_rc, color='k', linestyle=':', linewidth=1,
                                   label=f'Static = {static_rc:.3f} in')
            self.rc_ax.axvline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
            self.rc_ax.axhline(0, color='gray', linestyle='-', linewidth=0.8, alpha=0.3)
            self.rc_ax.set_xlabel('Wheel Vertical Travel (in)')
            self.rc_ax.set_ylabel('Roll Center Height (in above ground)')
            self.rc_ax.set_title('Roll Center Height vs Wheel Travel')
            self.rc_ax.legend()
            self.rc_ax.grid(True, alpha=0.3)
            self._add_textbox(self.rc_ax,
                              f'Static RC = {static_str} in\n'
                              f'Avg RC    = {avg_rc:.3f} in\n'
                              f'FSAE target: 0–3 in')
            self.rc_fig.tight_layout()
            self.rc_canvas.draw()

            self.plot_notebook.select(2)

        except Exception as e:
            self.logger.error(f"Roll center error: {e}", exc_info=True)
            self.update_results(f"Error in roll center:\n{e}")

    def run_all(self):
        """Run all three calculations sequentially (each calls sweep once)."""
        self.calculate_motion_ratio()
        self.calculate_camber_gain()
        self.calculate_roll_center()
        self.update_results(
            "▶  Run All complete.\n\n"
            "Check the Motion Ratio, Camber Gain, and Roll Center plot tabs.\n"
            "Results from the last individual calculation are shown above.\n"
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_shock_params(self):
        return (float(self.shock_min.get()),
                float(self.shock_max.get()),
                float(self.shock_step.get()))

    def _get_points(self):
        from ..data_loader import DataLoader
        # Build a temporary loader to reuse get_2d_points logic,
        # but use the live data arrays (may have been edited in the table).
        loader = DataLoader.__new__(DataLoader)
        loader.basic_data   = self.basic_data
        loader.pushrod_data = self.pushrod_data
        return loader.get_2d_points(self.suspension_type.get())

    def update_results(self, text: str):
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.configure(state=tk.DISABLED)

    @staticmethod
    def _add_textbox(ax, text: str):
        props = dict(boxstyle='round', facecolor='white', edgecolor='black', alpha=0.8)
        ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=props)

    def _init_empty_plots(self):
        for ax, canvas, label in [
            (self.mr_ax,  self.mr_canvas,  'Motion Ratio'),
            (self.cg_ax,  self.cg_canvas,  'Camber Gain'),
            (self.rc_ax,  self.rc_canvas,  'Roll Center Height'),
        ]:
            ax.text(0.5, 0.5, f'{label} results will appear here',
                    ha='center', va='center', transform=ax.transAxes,
                    fontsize=13, color='gray')
            ax.set_axis_off()
            canvas.draw()

    # ── Legacy helpers kept for any external callers ──────────────────────────

    def get_2d_points(self, suspension_type='pushrod'):
        from ..data_loader import DataLoader
        loader = DataLoader.__new__(DataLoader)
        loader.basic_data   = self.basic_data
        loader.pushrod_data = self.pushrod_data
        return loader.get_2d_points(suspension_type)

    def plot_analysis(self, x_data, y_data, xlabel, ylabel, title):
        self.mr_ax.clear()
        self.mr_ax.set_axis_on()
        self.mr_ax.plot(x_data, y_data, 'bo-', linewidth=2, markersize=6)
        self.mr_ax.set_xlabel(xlabel)
        self.mr_ax.set_ylabel(ylabel)
        self.mr_ax.set_title(title)
        self.mr_ax.grid(True, alpha=0.3)
        self.mr_fig.tight_layout()
        self.mr_canvas.draw()

    def clear_plot(self):
        self._init_empty_plots()
