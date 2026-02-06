"""Configuration for the bulk tester.

Reuses the gcb-runner configuration file (~/.gcb-runner/config.json)
for API keys and backend settings. No separate config needed.
"""

from gcb_runner.config import Config


def load_config() -> Config:
    """Load the shared gcb-runner configuration.
    
    The bulk tester shares the same config file as gcb-runner,
    which stores platform API keys, backend API keys, and defaults.
    """
    return Config.load()
