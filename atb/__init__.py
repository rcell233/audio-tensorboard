"""
AudioTensorBoard - 现代化的TensorBoard日志可视化工具

一个美观、易用的TensorBoard事件文件可视化工具，支持标量、图像和音频数据的展示。
"""

__version__ = "0.1.0"
__author__ = "AudioTensorBoard Contributors"
__license__ = "MIT"

from .app import create_app

__all__ = ["create_app"]

