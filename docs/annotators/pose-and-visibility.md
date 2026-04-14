# Pose And Visibility Rules

## Pose Formats

The app supports two named pose structures:

- `coco`
- `coco_with_thumbs`

Use `--pose-format` to override the config at runtime when needed.

Reference images:
- [COCO example](../../example_images/coco.png)
- [COCO with thumbs example](../../example_images/coco_with_thumbs.png)

## Visibility

Visibility is stored in the third value of each keypoint.

Depending on the configured `visibility_levels`, the app supports:

- `v = 2`: visible
- `v = 1`: occluded or not directly visible
- `v = 3`: guessed position

The `v` key cycles these values for the currently selected keypoint while dragging.

In the visualizer:
- visible keypoints are shown normally
- occluded keypoints appear greyed or more transparent
- guessed keypoints are shown with minimal marker emphasis

## Checked Versus Unchecked

Annotations that have already been reviewed are marked as `checked`. In bbox annotation, finished items are shown in a darker shade. In pose annotation, `u` skips directly to the next unfinished annotation.

## Working Carefully

The most common quality problems are:
- swapped left and right joints
- wrong visibility on nose or face points
- missing limbs or deleted points that should exist
- placing points on the wrong body part

See [examples.md](examples.md) for visual examples.
