def find_air_delivery_rate_filtered(
    filtration_efficiency,
    c_ambient=None,
    c_mask=None,
    ff_n99=None,
    air_delivery_rate=6000,
):
    """
    Parameters:
        c_mask: float
            The concentration within the mask (# particles / cm3) using N99-mode.

        c_ambient: float
            The concentration outside the mask (# particles / cm3)

        filtration_efficiency: float
            The single pass filtration efficiency of the filter.

        air_delivery_rate: float
            The amount being breathed in (e.g. cm3/min). Defaults to 6000 cm3 / min.

    Returns: float
        The air delivery rate. The rate of volume of air that is going through the filter (cm3 / min)
    """
    if (ff_n99 is None and c_mask is None) or (ff_n99 is not None and c_mask is not None):
        raise ValueError("Please provide one of the following: ff_n99 or c_mask (mutually exclusive).")

    if ff_n99 is not None and c_mask is None:
        if c_ambient is None:
            c_ambient = 10000
        c_mask = c_ambient / ff_n99

    return air_delivery_rate * (c_ambient - c_mask) / (c_ambient * filtration_efficiency)

def estimate_n95_mode_ff(total_air_delivery_rate, clean_air_delivery_rate):
    """
    Estimate N95-mode Fit Factors

    Parameters:
        total_air_delivery_rate: float
            The amount of air that is being delivered. (cm3 / min)

        clean_air_delivery_rate: float
            The amount of clean air that is being delivered. (cm3 / min)


    Returns: float
        Between 1 and infinity
    """
    return total_air_delivery_rate / (total_air_delivery_rate - clean_air_delivery_rate)


def estimate_n95_mode_ff_from_n99_mode_results(
    filtration_efficiency,
    ff_n99,
    total_air_delivery_rate=6000
):
    """
    Paramters:
        filtration_efficiency: float
            Some float between 0 and 1.

        ff_n99: float
            N99-mode Fit Factor. Between 1 and infinity
    """

    if filtration_efficiency < 0 or filtration_efficiency > 1:
        raise ValueError(f"Filtration efficiency {filtration_efficiency} should be between 0 and 1")

    if ff_n99 < 1:
        raise ValueError(f"N99-mode fit factor {ff_n99} should be at least 1 or greater.")

    clean_air_delivery_rate = find_air_delivery_rate_filtered(
        filtration_efficiency=filtration_efficiency,
        ff_n99=ff_n99,
        air_delivery_rate=total_air_delivery_rate
    )

    return estimate_n95_mode_ff(
        total_air_delivery_rate=total_air_delivery_rate,
        clean_air_delivery_rate=clean_air_delivery_rate
    )
