import json
from pathlib import Path
from typing import Optional

# Resolve config.json relative to the project root (two levels up from this file)
_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.json"


class Config:
    def __init__(self):
        self.show_ai_analysis: bool = False
        self.detection_camera: int = 0
        self.showing_camera: Optional[int] = None
        self.mirror_camera: bool = True

    def _create_config_file(self):
        with open(_CONFIG_PATH, "w") as f:
            json.dump({
                "show_ai_analysis": self.show_ai_analysis,
                "detection_camera_index": self.detection_camera,
                "showing_camera_index": self.showing_camera,
                "mirror_camera": self.mirror_camera,
            }, f, indent=4)

    @staticmethod
    def load_config() -> "Config":
        try:
            with open(_CONFIG_PATH, "r") as f:
                data = json.load(f)
            config = Config()
            config.show_ai_analysis = data.get("show_ai_analysis", False)
            config.detection_camera = data.get("detection_camera_index", 0)
            config.showing_camera = data.get("showing_camera_index", None)
            config.mirror_camera = data.get("mirror_camera", True)
            return config
        except FileNotFoundError:
            config = Config()
            config._create_config_file()
            return config
