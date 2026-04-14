# Developer Overview

PoseAnnotator is a local desktop annotation tool for:
- drawing person bounding boxes on image datasets
- annotating 2D human keypoints inside those boxes

The project is intentionally lightweight. It uses Python, OpenCV windows, and JSON files instead of a web stack or database.

## Main Features

- bbox annotation through [annotate_bboxes.py](../../annotate_bboxes.py)
- pose annotation through [annotate_pose.py](../../annotate_pose.py)
- named pose formats: `coco` and `coco_with_thumbs`
- configurable behavior through [annotator_config.ini](../../annotator_config.ini)
- shorthand sequence names resolved through `sequence_root`
- configurable pose output suffixes such as `_manual`
- optional Google Drive upload for saved annotations

## Main Entry Points

- [annotate_bboxes.py](../../annotate_bboxes.py): create and edit person bounding boxes
- [annotate_pose.py](../../annotate_pose.py): annotate keypoints inside existing boxes

Both entrypoints load configuration first, resolve the input path, start an OpenCV event loop, and autosave when navigating between items.

## Where The Core Logic Lives

- [src/bbox_annotator.py](../../src/bbox_annotator.py): bbox editing behavior
- [src/interactive_annotator.py](../../src/interactive_annotator.py): pose editing behavior
- [src/visualization.py](../../src/visualization.py): skeleton definitions, drawing, crop rendering
- [src/json_utils.py](../../src/json_utils.py): JSON load/save, path helpers, Google Drive helpers
- [src/annotator_config.py](../../src/annotator_config.py): INI parsing and validation
- [tools/](../../tools): small annotation-processing utilities outside the runtime app

## Related Material

- [Setup](setup.md)
- [Codebase guide](codebase.md)
- [Contributing](contributing.md)
- [Configuration reference](config.md)
- [Annotator docs](../annotators/getting-started.md)
