import numpy as np

def _theta_rel_modeB_mirrored(l1: float, l2: float, x: float) -> float:
    """
    Mode B (along-rail length x fixed): constant angle between rail and link l1.
    This is the internal triangle angle at the joint between sides (l1, x).
    Returns radians.
    """

    # Triangle existence: sides (l1, l2, x)
    if not (abs(l1 - l2) <= x <= (l1 + l2)):
        raise ValueError(
            f"Unreachable: need |l1 - l2| ≤ x ≤ (l1 + l2). Got l1={l1}, l2={l2}, x={x}."
        )

    # Law of cosines for angle at the joint between l1 and x
    cos_rel = (l1*l1 + x*x - l2*l2) / (2.0 * l1 * x)
    cos_rel = float(np.clip(cos_rel, -1.0, 1.0))
    return float(np.arccos(cos_rel))  # radians


def motor_theta_abs_from_alpha_mirrored(
    l1: float, l2: float, x: float, alpha, degrees: bool = False
):
    """
    MIRRORED assembly, Mode B (along-rail length x fixed).

    Single motor command (absolute link angle to horizontal):
        θ_abs(α) = α + θ_rel
    where θ_rel is constant from the triangle (l1, l2, x).

    Args:
        l1, l2 : link lengths (>0)
        x      : along-rail length (initial reach; >0)
        alpha  : float or array-like (radians) – rail tilt
        degrees: return θ_abs in degrees if True

    Returns:
        θ_abs : float or ndarray (same shape as alpha)
    """
    theta_rel = _theta_rel_modeB_mirrored(l1, l2, x)  # constant (rad)
    alpha = np.asarray(alpha, dtype=float)
    theta_abs = alpha + theta_rel
    return np.degrees(theta_abs) if degrees else theta_abs


def motor_theta_abs_from_height_mirrored(
    l1: float, l2: float, x: float, h, degrees: bool = False
):
    """
    Same as above but you specify lift height h instead of tilt α.
    In Mode B: h = x * sin(α)  =>  α = arcsin(h/x), with |h| ≤ x.
    """
    h = np.asarray(h, dtype=float)
    if np.any(np.abs(h) > x + 1e-12):
        raise ValueError("For Mode B, |h| must be ≤ x (since h = x * sin(alpha)).")

    alpha = np.arcsin(np.clip(h / x, -1.0, 1.0))
    return motor_theta_abs_from_alpha_mirrored(l1, l2, x, alpha, degrees=degrees)


# --- Examples ---
if __name__ == "__main__":
    l1, l2 = 0.9, 0.7
    x = 1.0  # along-rail length = initial horizontal reach

    # Example 1: give rail tilt angles (0°, 10°, 20°, 30°)
    alphas = np.deg2rad([0, 10, 20, 30])
    theta_abs = motor_theta_abs_from_alpha_mirrored(l1, l2, x, alphas, degrees=True)
    print("θ_abs (mirrored) from α [deg]:", np.round(theta_abs, 3))

    # Example 2: give lift heights directly
    h_vals = np.linspace(0.0, 0.5, 6)  # meters, for instance
    theta_abs_h = motor_theta_abs_from_height_mirrored(l1, l2, x, h_vals, degrees=True)
    for h, th in zip(h_vals, theta_abs_h):
        print(f"h={h:0.3f} -> θ_abs (mirrored) = {th:7.3f}°")
