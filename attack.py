# attack.py
import numpy as np

def inject_attack(
    yaw_commands: np.ndarray,
    timestep: int,
    attack_start: int
) -> np.ndarray:
    """
    Simulates an attack by forcing yaw angles of front turbines to an extreme value.

    Args:
        yaw_commands (np.ndarray): The yaw angles decided by the controller.
        timestep (int): The current simulation timestep.
        attack_start (int): The timestep at which the attack begins.

    Returns:
        np.ndarray: The potentially modified yaw commands after the attack.
    """
    # At the exact start time of the attack, overwrite the controller's commands
    if timestep >= attack_start:
        # Forcing the first two turbines to an extreme, damaging yaw angle
        yaw_commands[0] = 60.0
        yaw_commands[1] = 60.0
    return yaw_commands