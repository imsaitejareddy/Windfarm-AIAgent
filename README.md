# Simplified CARES Wind Farm Simulation

This project provides a simplified, lightweight simulation of the **CARES (Cyber-resilient and Risk-aware Energy Systems)** framework. It demonstrates how a risk-aware control system, coupled with a cognitive agent, can detect and respond to a cyber-attack on a wind farm's control system.

The entire simulation is self-contained, runs on a standard laptop, and uses the **FLORIS** analytical wake model for all physics calculations.

## Core Concepts

* **Wake Steering:** Modern wind farm control involves actively steering ("yawing") upstream turbines to direct their turbulent wakes away from downstream turbines, increasing the total power output of the farm.
* **CVaR-MPC Controller:** The "brains" of the farm is a **Model Predictive Controller (MPC)** that is risk-aware. Instead of only maximizing power, it also minimizes the **Conditional Value-at-Risk (CVaR)** of a stress proxy, preventing actions that could cause excessive structural load.
* **Cyber-Attack Scenario:** We simulate a direct command-override attack where a malicious actor forces the turbines into damaging and inefficient yaw angles.
* **Adaptive Defense:** The defense mechanism has two layers:
    1.  **Static IDS:** A simple rule-based Intrusion Detection System that flags anomalous commands.
    2.  **Cognitive Agent:** A simulated reasoning layer that, upon receiving an IDS alert, instructs the MPC controller to become highly risk-averse, prioritizing turbine safety over power generation.

## Project Structure

* `README.md`: This documentation file.
* `requirements.txt`: A list of required Python packages.
* `input.json`: The configuration file defining the wind farm layout and physics models for FLORIS.
* `main.py`: The main script that orchestrates the entire simulation.
* `cvar_mpc.py`: Implements the risk-aware MPC controller logic.
* `attack.py`: Defines the cyber-attack injection function.
* `cognitive_agent.py`: Simulates the reasoning agent that adapts the system's risk profile.
* `analyze.py`: A script to process the simulation logs and generate final performance metrics and plots.

## How to Run

### 1. Setup

Ensure you have Python 3.9+ installed. Place all project files in a single directory.

### 2. Create Virtual Environment

It is highly recommended to use a virtual environment. Open a terminal in the project directory and run:

```bash
# Create the virtual environment
python -m venv venv

# Activate the environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate
