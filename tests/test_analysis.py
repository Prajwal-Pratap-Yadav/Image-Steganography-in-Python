import json
import math

import numpy as np
import pytest

from stegolab.analysis import analyze_image, distortion, pair_test
from stegolab.errors import StegoError


def test_known_mse_psnr_and_json_finite():
    cover = np.zeros((8, 8, 3), dtype=np.uint8)
    different = np.ones_like(cover)
    measured = distortion(cover, different)
    assert measured["mse"] == 1
    assert measured["psnr_db"] == pytest.approx(20 * math.log10(255))
    identical = distortion(cover, cover)
    assert identical["psnr_db"] is None
    assert identical["ssim"] == pytest.approx(1)
    json.dumps(analyze_image(cover), allow_nan=False)
    assert distortion(cover[:4], cover[:4])["ssim"] is None
    with pytest.raises(StegoError):
        distortion(cover, cover[:4])


def test_equal_pairs_and_biased_pairs():
    paired = np.zeros((32, 32, 3), dtype=np.uint8)
    paired[::2] = 1
    balanced = pair_test(paired)
    biased = pair_test(np.zeros((32, 32, 3), dtype=np.uint8))
    assert balanced["statistic"] == 0
    assert balanced["p_value"] == 1
    assert biased["statistic"] == 32 * 32 * 3
    assert biased["p_value"] == 0
    tiny = pair_test(np.zeros((1, 1, 3), dtype=np.uint8))
    assert tiny["degrees_of_freedom"] == 0 and tiny["p_value"] is None
