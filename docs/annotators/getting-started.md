# Getting Started

This guide is for annotators using the app to create labels.

## What You Need

The app works best with COCO-style dataset folders:

- `annotations/`
- `val2017/`
- optionally `train2017/`

Example datasets are available in [test_data](../../test_data/) when present in your checkout.

If you only want to annotate bounding boxes, you can start from images alone. The bbox entrypoint will create the annotation file for you.

## The Two-Step Workflow

1. Annotate person bounding boxes.
2. Annotate pose keypoints inside those boxes.

Use:

```bash
python annotate_bboxes.py <dataset-folder-or-sequence>
python annotate_pose.py <annotation-file-or-sequence>
```

You can pass either:
- a full path
- a shorthand sequence name resolved under `sequence_root` in [annotator_config.ini](../../annotator_config.ini)

## Typical Start

Bounding boxes first:

```bash
python annotate_bboxes.py test_data/RePoGen_bbox_test
```

Then pose:

```bash
python annotate_pose.py test_data/RePoGen_kpts_test/annotations/person_keypoints_val2017.json
```

If your team uses shorthand sequence names:

```bash
python annotate_bboxes.py MY_SEQUENCE
python annotate_pose.py MY_SEQUENCE
```

## Next Pages

- [Workflow](workflow.md)
- [Keyboard shortcuts](shortcuts.md)
- [Pose and visibility rules](pose-and-visibility.md)
- [Examples and common mistakes](examples.md)
