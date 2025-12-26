"""Results viewer module - zero dependency web dashboard."""

from gcb_runner.viewer.report import generate_report
from gcb_runner.viewer.server import start_viewer

__all__ = ["start_viewer", "generate_report"]
