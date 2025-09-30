def linkage_angle_deg(x, L1, L2):
    """
    Compute the angle at the fixed pivot (bottom left) 
    given horizontal displacement x of the sliding joint.

    Parameters
    ----------
    x : float
        Horizontal displacement of the sliding joint
    L1 : float
        Length of the fixed bar (pivot to top joint)
    L2 : float
        Length of the other bar (top joint to sliding joint)

    Returns
    -------
    theta_deg : float
        Angle at the fixed pivot in degrees
    """
    num = L1**2 + x**2 - L2**2
    den = 2 * L1 * x
    
    # Clamp for numerical safety
    cos_theta = num / den
    cos_theta = max(-1.0, min(1.0, cos_theta))
    
    theta_rad = math.acos(cos_theta)
    theta_deg = math.degrees(theta_rad)
    return theta_deg


# Example usage
L1 = 5.0
L2 = 7.0
x = 6.0

theta = linkage_angle_deg(x, L1, L2)
print("Angle θ (degrees):", theta)
