# Configuration Reference

The annotator reads task-specific behavior from [annotator_config.ini](../../annotator_config.ini). Both entrypoints use the repo-root config by default, and both accept `--config <path>` to load another INI file.

Relative `sequence_root` values are resolved relative to the config file location, not the current shell working directory.

## Basic Workflow

1. Edit [annotator_config.ini](../../annotator_config.ini) for your dataset and preferred behavior.
2. Run `python annotate_bboxes.py <dataset-or-sequence>`.
3. Run `python annotate_pose.py <annotation-file-or-sequence>`.
4. Override any config file with `--config <path>` when needed.

## Paths

### `sequence_root`

Base directory used when you pass a shorthand sequence name such as `BOTTOM`.

Examples:

```bash
python annotate_bboxes.py BOTTOM
python annotate_pose.py BOTTOM
```

## Display

### `show_example`

Show or hide the reference pose image next to the active crop.

### `crop_mode`

Use `single` for one crop view or `double` to show two scales side by side.

### `infinite_space_enabled`

Enable the infinite-space background around the bbox. This cannot be combined with `crop_mode = double`.

### `infinite_space_strength`

Control how much padding is added when infinite-space mode is enabled.

### `default_bbox_padding`

Control the initial crop padding shown by the pose annotator. The default is `0.0`.

## Interaction

### `click_radius_ratio`

Control how close the mouse must be to select a keypoint or bbox corner.

### `drag_redraw_fps`

Control how often the image is redrawn while dragging.

### `history_size`

Set how many undo states are remembered for the current annotation.

### `visibility_levels`

Control how many visibility states the `v` key cycles through:

- `1`: all non-deleted keypoints are stored as visible (`v = 2`)
- `2`: `v = 1` occluded, `v = 2` visible
- `3`: `v = 1` occluded, `v = 2` visible, `v = 3` guessed

## Annotation

### `pose_format`

Supported values are `coco` and `coco_with_thumbs`.

## Workflow

### `jump_step`

Set how many items `.` and `,` skip in both entrypoints.

### `mark_checked_interval_seconds`

Control how long an annotation must stay open before it is marked as `checked`.

Set `0` or a negative value to disable automatic checking.

## Saving

### `output_suffix`

Set the suffix appended to pose output files. For example, `_manual` changes:

- `person_keypoints_val2017.json` -> `person_keypoints_val2017_manual.json`

If the input file is already suffixed with the configured output suffix, the pose annotator saves back into that same file.

## Related Docs

- [Developer setup](setup.md)
- [Codebase guide](codebase.md)
- [Annotator workflow](../annotators/workflow.md)
