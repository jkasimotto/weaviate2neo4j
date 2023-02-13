import math
import random


def weighted_probability_filter(weight: float):
    """Filter edges based on their weight.

    Args:
        weight (float between 0 and 1): The weight of the edge to filter.

    Returns:
        bool: True if the edge should be included, False otherwise.
    """
    assert 0 <= weight <= 1, "Weight must be between 0 and 1."

    # Return True with probability |weight|
    # Therefore we keep most 
    return random.random() > (1 - weight)


def threshold_filter(threshold: float, weight: float):
    """Filter edges based on their weight.

    Args:
        threshold (float between 0 and 1): The threshold of the edge to filter.
        weight (float between 0 and 1): The weight of the edge to filter.

    Returns:
        bool: True if the edge should be included, False otherwise.
    """
    assert 0 <= threshold <= 1, "Threshold must be between 0 and 1."
    assert 0 <= weight <= 1, "Weight must be between 0 and 1."

    # Return True if the weight is above the threshold
    return weight > threshold
