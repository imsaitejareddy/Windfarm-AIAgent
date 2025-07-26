import argparse
import os
import numpy as np
import pandas as pd
from floris.tools import FlorisInterface
from cvar_mpc import cvar_mpc_controller
from attack import inject_attack
from cognitive_agent import get_risk_parameter

def run_simulation(args):
    fi = FlorisInterface(args.config)
    n_turbines = len(fi.layout_x)
    
    yaw_angles = np.zeros(n_turbines)
    log_data = []
    omega = args.omega_base
    power = 0.0
    stress_proxy = 0.0
    
    print(f"Running Trial for Scenario: '{args.scenario}'...")

    for t in range(args.timesteps):
        fi.reinitialize()

        optimal_yaws, _, _ = cvar_mpc_controller(
            fi, yaw_angles, omega, alpha=args.alpha
        )

        yaw_cmd = optimal_yaws.copy()
        is_attack_active = t >= args.attack_start
        
        if args.scenario != 'baseline' and is_attack_active:
            yaw_cmd = inject_attack(yaw_cmd, t, args.attack_start)

        detection = False
        if np.any(np.abs(yaw_cmd) > 45.0):
            detection = True
        
        if args.scenario == 'cares':
            omega = get_risk_parameter(
                detection=detection,
                power=power,
                stress=stress_proxy,
                omega_base=args.omega_base,
                omega_attack=args.omega_attack
            )
        else:
            omega = args.omega_base

        final_stress_proxy = np.sum(np.abs(yaw_cmd))
        
        yaw_cmd_floris = yaw_cmd.reshape(1, 1, n_turbines)
        fi.calculate_wake(yaw_angles=yaw_cmd_floris)
        power = np.sum(fi.get_turbine_powers())

        log_data.append({
            'trial': args.trial,
            'timestep': t,
            'scenario': args.scenario,
            'power': power,
            'stress': final_stress_proxy,
            'detection': detection,
            'is_attack': is_attack_active,
            **{f'yaw_{i}': yaw_cmd[i] for i in range(n_turbines)}
        })

        yaw_angles = yaw_cmd
        stress_proxy = final_stress_proxy

    return pd.DataFrame(log_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CARES Simplified Wind Farm Simulation")
    parser.add_argument('--trials', type=int, default=5, help='Number of simulation trials')
    parser.add_argument('--timesteps', type=int, default=400, help='Total timesteps per trial')
    parser.add_argument('--attack_start', type=int, default=200, help='Timestep to start attack')
    parser.add_argument('--config', type=str, default='input.json', help='FLORIS input file')
    parser.add_argument('--alpha', type=float, default=0.95, help='CVaR confidence level')
    parser.add_argument('--omega_base', type=float, default=1e5, help='Baseline risk penalty weight')
    parser.add_argument('--omega_attack', type=float, default=5e5, help='Risk penalty weight under attack')
    args = parser.parse_args()

    os.makedirs('logs', exist_ok=True)
    os.makedirs('plots', exist_ok=True)

    for scenario in ['baseline', 'static_ids', 'cares']:
        for i in range(args.trials):
            current_args = argparse.Namespace(**vars(args))
            current_args.scenario = scenario
            current_args.trial = i
            
            results_df = run_simulation(current_args)
            
            if not results_df.empty:
                log_file = f'logs/results_trial_{i}_{scenario}.csv'
                results_df.to_csv(log_file, index=False)
            
    print("\nSimulation complete. Logs saved in 'logs/' directory.")
    print("Now run 'python analyze.py' to process results.")
