import numpy as np
from scipy.optimize import minimize
from floris.tools import FlorisInterface

def objective_function(
    yaw_angles: np.ndarray,
    fi: FlorisInterface,
    omega: float,
    alpha: float
) -> float:
    fi_temp = fi.copy()
    
    n_turbines = len(yaw_angles)
    yaw_angles_floris = yaw_angles.reshape(1, 1, n_turbines)
    
    fi_temp.calculate_wake(yaw_angles=yaw_angles_floris)
    power = np.sum(fi_temp.get_turbine_powers())

    num_samples = 20
    samples = [yaw_angles + np.random.uniform(-2, 2, len(yaw_angles)) for _ in range(num_samples)]
    
    stress_samples = np.array([np.sum(np.abs(s)) for s in samples])
    
    threshold = np.quantile(stress_samples, alpha)
    cvar_penalty = np.mean(stress_samples[stress_samples > threshold]) if np.any(stress_samples > threshold) else 0.0

    return -power + omega * cvar_penalty


def cvar_mpc_controller(
    fi: FlorisInterface,
    current_yaws: np.ndarray,
    omega: float,
    alpha: float = 0.95
):
    n_turbines = len(current_yaws)
    
    bounds = [(-30.0, 30.0)] * n_turbines

    result = minimize(
        fun=objective_function,
        x0=current_yaws,
        args=(fi, omega, alpha),
        bounds=bounds,
        method='SLSQP'
    )

    optimal_yaws = result.x

    optimal_yaws_floris = optimal_yaws.reshape(1, 1, n_turbines)
    fi.calculate_wake(yaw_angles=optimal_yaws_floris)
    predicted_power = np.sum(fi.get_turbine_powers())
    stress_proxy = np.sum(np.abs(optimal_yaws))

    return optimal_yaws, predicted_power, stress_proxy