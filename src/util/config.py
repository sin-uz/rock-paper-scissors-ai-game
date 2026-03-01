import json
from typing import Optional


class Config:
    def __init__(self):
        self.show_ai_analysis: bool = False
        self.detection_camera: int = 0
        self.showing_camera: Optional[int] = None

    def __create_config_file(self):
        with open("config.json", "w") as f:
            json.dump({
                "show_ai_analysis": self.show_ai_analysis,
                "detection_camera_index": self.detection_camera,
                "showing_camera_index": self.showing_camera,
            }, f, indent=4)

    @staticmethod
    def load_config():
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                config = Config()
                config.show_ai_analysis = data.get("show_ai_analysis", False)
                config.detection_camera = data.get("detection_camera_index", 0)
                config.showing_camera = data.get("showing_camera_index", None)
                return config
        except FileNotFoundError:
            config = Config()
            config.__create_config_file()
            return config
