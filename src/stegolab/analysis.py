"""Distortion and an exploratory even/odd pair-equality test, not a detector."""

import math

import numpy as np
from scipy.stats import chi2
from skimage.metrics import structural_similarity

from .codec import ImageArray, validate_image
from .errors import StegoError


def distortion(cover: ImageArray, stego: ImageArray) -> dict[str, object]:
    validate_image(cover)
    validate_image(stego)
    if cover.shape != stego.shape:
        raise StegoError("Cover and stego shapes must match")
    left, right = cover[:, :, :3], stego[:, :, :3]
    mse = float(np.mean((left.astype(np.float64) - right.astype(np.float64)) ** 2))
    ssim = None
    if min(left.shape[:2]) >= 7:
        ssim = float(structural_similarity(left, right, data_range=255, channel_axis=2, win_size=7))
    return {
        "mse": mse,
        "psnr_db": None if mse == 0 else 10 * math.log10(255**2 / mse),
        "psnr_note": "infinite for identical RGB" if mse == 0 else None,
        "ssim": ssim,
    }


def pair_test(image: ImageArray) -> dict[str, object]:
    histogram = np.bincount(image[:, :, :3].reshape(-1), minlength=256)
    even, odd = histogram[0::2], histogram[1::2]
    total = even + odd
    active = total >= 10  # expected counts at least five in each half
    degrees = int(active.sum())
    statistic = float(np.sum((even[active] - odd[active]) ** 2 / total[active]))
    return {
        "histogram": histogram.tolist(),
        "statistic": statistic,
        "degrees_of_freedom": degrees,
        "normalized_statistic": statistic / degrees if degrees else None,
        "p_value": float(chi2.sf(statistic, degrees)) if degrees else None,
    }


def analyze_image(image: ImageArray) -> dict[str, object]:
    validate_image(image)
    return {
        "global": pair_test(image),
        "row_blocks": [
            {"start_row": start, **pair_test(image[start : start + 16])}
            for start in range(0, image.shape[0], 16)
        ],
        "interpretation": "Null: even/odd histogram pairs are equal. Not a calibrated detector.",
    }
