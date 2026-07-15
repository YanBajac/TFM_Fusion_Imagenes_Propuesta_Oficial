# fusion package
from .optimal_top_hat import fuse_optimal, OptimalTopHatFusion
from .comparatives import (
    average_fusion,
    laplacian_pyramid_fusion,
    ratio_pyramid_fusion,
    dwt_fusion,
    dtcwt_fusion,
    curvelet_fusion,
    tophat_classic_fusion,
)

__all__ = [
    "fuse_optimal",
    "OptimalTopHatFusion",
    "average_fusion",
    "laplacian_pyramid_fusion",
    "ratio_pyramid_fusion",
    "dwt_fusion",
    "dtcwt_fusion",
    "curvelet_fusion",
    "tophat_classic_fusion",
]
