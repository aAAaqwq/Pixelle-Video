"""
Pixelle-Video Pipelines

Video generation pipelines with different strategies and workflows.
Each pipeline implements a specific video generation approach.
"""

from pixelle_video.pipelines.base import BasePipeline
from pixelle_video.pipelines.standard import StandardPipeline
from pixelle_video.pipelines.custom import CustomPipeline

__all__ = [
    "BasePipeline",
    "StandardPipeline",
    "CustomPipeline",
]

