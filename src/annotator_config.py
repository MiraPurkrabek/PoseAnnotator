import configparser
import os
from dataclasses import dataclass

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "annotator_config.ini",
)


@dataclass(frozen=True)
class AnnotatorConfig:
    config_path: str
    sequence_root: str
    show_example: bool = True
    crop_mode: str = "single"
    infinite_space_enabled: bool = False
    infinite_space_strength: float = 0.5
    default_bbox_padding: float = 0.0
    click_radius_ratio: float = 0.05
    drag_redraw_fps: int = 20
    history_size: int = 100
    visibility_levels: int = 3
    pose_format: str = "coco"
    jump_step: int = 10
    mark_checked_interval_seconds: float = 3.0
    output_suffix: str = "_manual"

    @property
    def config_dir(self):
        return os.path.dirname(self.config_path)

    @property
    def two_scales(self):
        return self.crop_mode == "double"

    @property
    def inf_size(self):
        if not self.infinite_space_enabled:
            return None
        return self.infinite_space_strength


class ConfigError(ValueError):
    pass


_BOOLEAN_STATES = {
    "1": True,
    "yes": True,
    "true": True,
    "on": True,
    "0": False,
    "no": False,
    "false": False,
    "off": False,
}


def _get_string(parser, section, option, fallback):
    if parser.has_option(section, option):
        return parser.get(section, option).strip()
    return fallback


def _get_bool(parser, section, option, fallback):
    if not parser.has_option(section, option):
        return fallback

    raw_value = parser.get(section, option).strip().lower()
    if raw_value not in _BOOLEAN_STATES:
        raise ConfigError("Invalid value for '{:s}.{:s}': expected true/false".format(section, option))
    return _BOOLEAN_STATES[raw_value]


def _get_int(parser, section, option, fallback):
    if not parser.has_option(section, option):
        return fallback

    raw_value = parser.get(section, option).strip()
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ConfigError("Invalid value for '{:s}.{:s}': expected integer".format(section, option)) from exc


def _get_float(parser, section, option, fallback):
    if not parser.has_option(section, option):
        return fallback

    raw_value = parser.get(section, option).strip()
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ConfigError("Invalid value for '{:s}.{:s}': expected number".format(section, option)) from exc


def _resolve_path(base_dir, path_value):
    path_value = os.path.expanduser(path_value)
    if os.path.isabs(path_value):
        return os.path.abspath(path_value)
    return os.path.abspath(os.path.join(base_dir, path_value))


def _validate_config(config):
    if config.crop_mode not in {"single", "double"}:
        raise ConfigError("Invalid value for 'display.crop_mode': expected 'single' or 'double'")

    if config.pose_format not in {"coco", "coco_with_thumbs"}:
        raise ConfigError("Invalid value for 'annotation.pose_format': expected 'coco' or 'coco_with_thumbs'")

    if config.visibility_levels not in {1, 2, 3}:
        raise ConfigError("Invalid value for 'interaction.visibility_levels': expected 1, 2, or 3")

    if config.default_bbox_padding < 0:
        raise ConfigError("Invalid value for 'display.default_bbox_padding': expected non-negative number")

    if config.infinite_space_strength < 0:
        raise ConfigError("Invalid value for 'display.infinite_space_strength': expected non-negative number")

    if config.click_radius_ratio <= 0:
        raise ConfigError("Invalid value for 'interaction.click_radius_ratio': expected positive number")

    if config.drag_redraw_fps <= 0:
        raise ConfigError("Invalid value for 'interaction.drag_redraw_fps': expected positive integer")

    if config.history_size <= 0:
        raise ConfigError("Invalid value for 'interaction.history_size': expected positive integer")

    if config.jump_step <= 0:
        raise ConfigError("Invalid value for 'workflow.jump_step': expected positive integer")

    if config.crop_mode == "double" and config.infinite_space_enabled:
        raise ConfigError(
            "Invalid config: 'display.crop_mode=double' cannot be combined with "
            "'display.infinite_space_enabled=true'"
        )

    if not config.output_suffix.strip():
        raise ConfigError("Invalid value for 'saving.output_suffix': expected a non-empty suffix")

    invalid_separators = {os.sep}
    if os.altsep:
        invalid_separators.add(os.altsep)
    if any(separator in config.output_suffix for separator in invalid_separators):
        raise ConfigError(
            "Invalid value for 'saving.output_suffix': expected filename suffix without " "path separators"
        )


def load_annotator_config(config_path):
    config_path = os.path.abspath(os.path.expanduser(config_path))
    if not os.path.exists(config_path):
        raise ConfigError("Config file not found: {:s}".format(config_path))
    if not os.path.isfile(config_path):
        raise ConfigError("Config path is not a file: {:s}".format(config_path))

    parser = configparser.ConfigParser(interpolation=None, inline_comment_prefixes=("#", ";"))
    read_paths = parser.read(config_path)
    if not read_paths:
        raise ConfigError("Failed to read config file: {:s}".format(config_path))

    base_dir = os.path.dirname(config_path)
    config = AnnotatorConfig(
        config_path=config_path,
        sequence_root=_resolve_path(base_dir, _get_string(parser, "paths", "sequence_root", "data")),
        show_example=_get_bool(parser, "display", "show_example", True),
        crop_mode=_get_string(parser, "display", "crop_mode", "single").lower(),
        infinite_space_enabled=_get_bool(parser, "display", "infinite_space_enabled", False),
        infinite_space_strength=_get_float(parser, "display", "infinite_space_strength", 0.5),
        default_bbox_padding=_get_float(parser, "display", "default_bbox_padding", 0.0),
        click_radius_ratio=_get_float(parser, "interaction", "click_radius_ratio", 0.05),
        drag_redraw_fps=_get_int(parser, "interaction", "drag_redraw_fps", 20),
        history_size=_get_int(parser, "interaction", "history_size", 100),
        visibility_levels=_get_int(parser, "interaction", "visibility_levels", 3),
        pose_format=_get_string(parser, "annotation", "pose_format", "coco").lower(),
        jump_step=_get_int(parser, "workflow", "jump_step", 10),
        mark_checked_interval_seconds=_get_float(
            parser,
            "workflow",
            "mark_checked_interval_seconds",
            3.0,
        ),
        output_suffix=_get_string(parser, "saving", "output_suffix", "_manual"),
    )
    _validate_config(config)
    return config
