"""
src/calculations/tire_model.py

Pacejka tire model implementation for FSAE tire data analysis
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp2d


class PacejkaTireModel:
    """
    Pacejka 4-parameter tire model for lateral and longitudinal force prediction.
    Fits tire test data to the Magic Formula tire model.
    """

    def __init__(self):
        self.FY_params = None  # Lateral force parameters [D1, D2, B, C]
        self.FX_params = None  # Longitudinal force parameters [D1, D2, B, C]

    @staticmethod
    def pacejka4_model(X, D1, D2, B, C):
        """
        Pacejka 4-parameter Magic Formula model.

        Parameters:
        -----------
        X : array-like, shape (n, 2)
            Input data where:
            X[:, 0] = Slip Angle (SA) in degrees (or slip ratio for FX)
            X[:, 1] = Normal Load (FZ) in Newtons
        D1, D2 : float
            Peak value coefficients
        B : float
            Stiffness factor
        C : float
            Shape factor

        Returns:
        --------
        fy : array
            Lateral (or longitudinal) force in Newtons
        """
        SA = X[:, 0]  # Slip angle (or slip ratio)
        FZ = X[:, 1]  # Normal load

        # Peak value calculation
        D = (D1 + D2 / 1000 * FZ) * FZ

        # Magic Formula
        fy = D * np.sin(C * np.arctan(B * SA))

        return fy

    def fit_tire_data(self, SA, FZ, FY, FX=None, initial_guess=None):
        """
        Fit Pacejka model to tire test data.

        Parameters:
        -----------
        SA : array-like
            Slip angles in degrees
        FZ : array-like
            Normal loads in Newtons
        FY : array-like
            Lateral forces in Newtons
        FX : array-like, optional
            Longitudinal forces in Newtons
        initial_guess : list, optional
            Initial parameter guess [D1, D2, B, C]

        Returns:
        --------
        dict : Fitting results containing parameters and residuals
        """
        # Prepare data
        xdata = np.column_stack([SA, FZ])

        # Initial guess for parameters
        if initial_guess is None:
            initial_guess = [0.0817, -0.5734, -0.5681, -0.1447]

        # Fit lateral force (FY)
        print("Fitting lateral force (FY) model...")
        FY_params, FY_cov = curve_fit(
            lambda X, D1, D2, B, C: self.pacejka4_model(X, D1, D2, B, C),
            xdata, FY,
            p0=initial_guess,
            maxfev=100000  # Maximum function evaluations
        )

        # Calculate residuals
        FY_pred = self.pacejka4_model(xdata, *FY_params)
        FY_residual = FY - FY_pred
        FY_resnorm = np.sum(FY_residual ** 2)

        self.FY_params = FY_params

        results = {
            'FY_params': FY_params,
            'FY_resnorm': FY_resnorm,
            'FY_residual': FY_residual,
            'FY_pred': FY_pred
        }

        # Fit longitudinal force (FX) if provided
        if FX is not None:
            print("Fitting longitudinal force (FX) model...")
            FX_params, FX_cov = curve_fit(
                lambda X, D1, D2, B, C: self.pacejka4_model(X, D1, D2, B, C),
                xdata, FX,
                p0=initial_guess,
                maxfev=100000  # Maximum function evaluations
            )

            FX_pred = self.pacejka4_model(xdata, *FX_params)
            FX_residual = FX - FX_pred
            FX_resnorm = np.sum(FX_residual ** 2)

            self.FX_params = FX_params

            results['FX_params'] = FX_params
            results['FX_resnorm'] = FX_resnorm
            results['FX_residual'] = FX_residual
            results['FX_pred'] = FX_pred

        return results

    def generate_surface(self, sa_range=(-13, 13), fz_range=(-1600, -200), n_points=100):
        """
        Generate fitted surface data for visualization.

        Parameters:
        -----------
        sa_range : tuple
            (min, max) slip angle range in degrees
        fz_range : tuple
            (min, max) normal load range in Newtons
        n_points : int
            Number of points in each dimension

        Returns:
        --------
        dict : Contains SA, FZ grids and FY, FX surfaces
        """
        if self.FY_params is None:
            raise ValueError("Model not fitted yet. Call fit_tire_data first.")

        # Create grid
        sa = np.linspace(sa_range[0], sa_range[1], n_points)
        fz = np.linspace(fz_range[0], fz_range[1], n_points)
        SA_grid, FZ_grid = np.meshgrid(sa, fz)

        # Calculate FY surface
        FY_surface = np.zeros_like(SA_grid)
        for i in range(len(fz)):
            X = np.column_stack([sa, np.full(n_points, fz[i])])
            FY_surface[i, :] = self.pacejka4_model(X, *self.FY_params)

        results = {
            'sa': sa,
            'fz': fz,
            'SA_grid': SA_grid,
            'FZ_grid': FZ_grid,
            'FY_surface': FY_surface
        }

        # Calculate FX surface if parameters exist
        if self.FX_params is not None:
            FX_surface = np.zeros_like(SA_grid)
            for i in range(len(fz)):
                X = np.column_stack([sa, np.full(n_points, fz[i])])
                FX_surface[i, :] = self.pacejka4_model(X, *self.FX_params)
            results['FX_surface'] = FX_surface

        return results

    def find_max_lateral_force(self, target_vertical_load, sa_range=(-13, 13), n_points=100):
        """
        Find maximum lateral force at a specific vertical load.

        Parameters:
        -----------
        target_vertical_load : float
            Target normal load in Newtons (negative for compression)
        sa_range : tuple
            Slip angle range to search
        n_points : int
            Number of points to evaluate

        Returns:
        --------
        dict : Maximum lateral force and optimal slip angle
        """
        if self.FY_params is None:
            raise ValueError("Model not fitted yet. Call fit_tire_data first.")

        # Generate slip angle array
        sa = np.linspace(sa_range[0], sa_range[1], n_points)

        # Calculate lateral forces at target vertical load
        X = np.column_stack([sa, np.full(n_points, target_vertical_load)])
        fy = self.pacejka4_model(X, *self.FY_params)

        # Find maximum
        max_idx = np.argmax(np.abs(fy))
        max_lateral_force = fy[max_idx]
        optimal_slip_angle = sa[max_idx]

        return {
            'max_lateral_force': max_lateral_force,
            'optimal_slip_angle': optimal_slip_angle,
            'target_vertical_load': target_vertical_load,
            'sa_array': sa,
            'fy_array': fy
        }