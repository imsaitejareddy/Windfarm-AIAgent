# analyze.py
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_metrics(df: pd.DataFrame, attack_start: int) -> dict:
    """
    Computes detection and performance metrics for a single simulation run.

    Args:
        df (pd.DataFrame): The dataframe from a single trial log.
        attack_start (int): The timestep when the attack began.

    Returns:
        dict: A dictionary of computed metrics.
    """
    attack_period_df = df[df['timestep'] >= attack_start]
    no_attack_period_df = df[df['timestep'] < attack_start]

    # Calculate detection metrics
    true_positives = attack_period_df['detection'].sum()
    false_negatives = len(attack_period_df) - true_positives
    false_positives = no_attack_period_df['detection'].sum()
    
    # Add small epsilon to avoid division by zero
    epsilon = 1e-9
    precision = true_positives / (true_positives + false_positives + epsilon)
    recall = true_positives / (true_positives + false_negatives + epsilon)
    f1 = 2 * (precision * recall) / (precision + recall + epsilon)

    # Calculate performance metrics
    detected_steps = df[df['detection']]['timestep']
    time_to_detect = (detected_steps.min() - attack_start) if not detected_steps.empty and detected_steps.min() >= attack_start else np.nan
    
    peak_stress_during_attack = attack_period_df['stress'].max() if not attack_period_df.empty else 0
    
    # Energy loss compared to the average power before the attack
    baseline_power = no_attack_period_df['power'].mean()
    total_expected_power = baseline_power * len(df)
    total_actual_power = df['power'].sum()
    energy_loss_percent = 100 * (total_expected_power - total_actual_power) / (total_expected_power + epsilon)

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'time_to_detect': time_to_detect,
        'peak_stress_attack': peak_stress_during_attack,
        'energy_loss_percent': energy_loss_percent
    }

def main():
    """Main function to analyze logs and generate outputs."""
    all_metrics = []
    
    # Find the attack start time from a log file (assuming it's constant)
    try:
        any_log = pd.read_csv(glob.glob('logs/*.csv')[0])
        attack_start = any_log[any_log['is_attack']].timestep.min()
    except IndexError:
        print("No log files found. Please run 'main.py' first.")
        return
        
    # Process each log file
# Process each log file
    for log_file in glob.glob('logs/results_trial_*.csv'):
        try:
            df = pd.read_csv(log_file)
            if df.empty:
                print(f"Warning: Log file is empty, skipping. -> {log_file}")
                continue
        except pd.errors.EmptyDataError:
            print(f"Warning: Could not parse log file, skipping. -> {log_file}")
            continue

        scenario = df['scenario'].iloc[0]
        trial = df['trial'].iloc[0]
        
        metrics = compute_metrics(df, attack_start)
        metrics['scenario'] = scenario
        metrics['trial'] = trial
        all_metrics.append(metrics)
        
        # Generate and save plots for the first trial of each scenario
        if trial == 0:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
            
            # Power plot
            ax1.plot(df['timestep'], df['power'] / 1e6, label='Farm Power')
            ax1.axvline(x=attack_start, color='r', linestyle='--', label='Attack Start')
            ax1.set_ylabel('Power (MW)')
            ax1.set_title(f'Performance and Stress for Scenario: {scenario.upper()}')
            ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
            
            # Detection markers
            detections = df[df['detection']]
            if not detections.empty:
                ax1.scatter(detections['timestep'], detections['power'] / 1e6, color='orange', zorder=5, label='Detection')
            ax1.legend()
            
            # Stress plot
            ax2.plot(df['timestep'], df['stress'], label='Stress Proxy', color='purple')
            ax2.axvline(x=attack_start, color='r', linestyle='--', label='Attack Start')
            ax2.set_xlabel('Timestep')
            ax2.set_ylabel('Stress Proxy (Sum of |Yaw|)')
            ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
            ax2.legend()
            
            plt.tight_layout()
            plot_name = f"plots/timeseries_{scenario}_trial_0.png"
            plt.savefig(plot_name)
            plt.close()

    # Create and print summary table
    if not all_metrics:
        print("No metrics were generated.")
        return
        
    metrics_df = pd.DataFrame(all_metrics)
    summary = metrics_df.groupby('scenario').agg(['mean', 'std'])
    
    # Format for readability
    pd.options.display.float_format = '{:,.2f}'.format
    
    print("\n--- Simulation Analysis Summary ---\n")
    print(summary)
    
    summary.to_csv('plots/summary_table.csv')
    print("\nSummary table and plots saved in 'plots/' directory.")

if __name__ == "__main__":
    main()