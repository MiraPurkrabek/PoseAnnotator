# Codebase Guide

## Structure

The repository keeps a simple top-level layout:

- [annotate_bboxes.py](../../annotate_bboxes.py): bbox app entrypoint
- [annotate_pose.py](../../annotate_pose.py): pose app entrypoint
- [src/](../../src): shared runtime code
- [tools/](../../tools): annotation-processing utilities
- [docs/](../README.md): user and developer documentation
- [example_images/](../../example_images): pose format reference images

## Bbox Flow

The bbox workflow starts in [annotate_bboxes.py](../../annotate_bboxes.py).

It:
- loads config through `src.annotator_config`
- resolves either a dataset path or a shorthand sequence name
- creates the COCO-like annotation file if it does not exist yet
- loads the current image and its annotations
- delegates editing to `BboxAnnotator`
- saves when the user navigates, jumps, or quits

`BboxAnnotator` keeps bbox state in memory, supports undo/reset, and converts edited corner coordinates back to COCO `bbox` values.

## Pose Flow

The pose workflow starts in [annotate_pose.py](../../annotate_pose.py).

It:
- loads config and resolves the pose format
- resolves either a JSON path or a shorthand sequence name
- infers the image directory when `--img-path` is not provided
- computes the output path using the configured suffix
- iterates through `coco_data["annotations"]`
- delegates editing to `InteractiveAnnotator`
- autosaves during navigation and on exit

`InteractiveAnnotator` operates on one person annotation at a time and is responsible for:
- keypoint selection and dragging
- visibility cycling
- undo/reset/generate/flip/add actions
- crop padding and zoom
- automatic `checked` marking after a configurable interval

## Visualization And Pose Definitions

[src/visualization.py](../../src/visualization.py) contains the pose-specific rendering logic:
- keypoint names and order
- skeleton edges
- side-aware coloring
- crop rendering
- mapping screen positions back to keypoints

The public pose formats in the app are:
- `coco`
- `coco_with_thumbs`

## Data And Saving

[src/json_utils.py](../../src/json_utils.py) centralizes:
- JSON loading and writing
- path resolution for shorthand sequences
- pose output filename generation
- image-directory inference
- Google Drive authentication and upload helpers

Pose annotation saves to a suffixed file such as `person_keypoints_val2017_manual.json` by default. Bbox annotation saves in place to `annotations/person_keypoints_val2017.json`.

## Configuration

[src/annotator_config.py](../../src/annotator_config.py) validates the INI file and exposes a typed config object consumed by both entrypoints. For the full setting reference, see [config.md](config.md).
