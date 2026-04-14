# Keyboard Shortcuts

This page collects the main shortcuts for both annotation stages.

## Bounding Box Annotation

Mouse:
- click empty space to create a box
- drag a box corner to resize it

Keyboard:

| Shortcut | Description |
| --- | --- |
| `m` | Save and move to the next image |
| `n` | Save and move to the previous image |
| `,` | Jump backward by the configured `jump_step` |
| `.` | Jump forward by the configured `jump_step` |
| `u` | Jump to the next unfinished image |
| `x` | Jump to a random image |
| `d` | Delete the selected bbox corner or active edit |
| `z` | Undo the previous action |
| `r` | Reset to the last saved state |
| `q` | Quit and save |

## Pose Annotation

Mouse:
- click a keypoint to select it
- drag to move it

Keyboard:

| Shortcut | Description |
| --- | --- |
| `u` | Jump to the next unfinished pose |
| `m` | Save and move to the next pose |
| `n` | Save and move to the previous pose |
| `,` | Jump backward by the configured `jump_step` |
| `.` | Jump forward by the configured `jump_step` |
| `x` | Jump to a random pose |
| `v` | Cycle visibility of the selected keypoint while dragging |
| `d` | Delete the selected keypoint while dragging |
| `a` | Add a missing keypoint |
| `z` | Undo the previous step |
| `r` | Reset to the last saved state |
| `g` | Generate a template pose |
| `l` | Flip left and right keypoints |
| `o` | Zoom out around the bbox |
| `p` | Zoom in around the bbox |
| `e` | Swap visible and occluded labels |
| `q` | Quit and save |

## Notes

- The exact jump size comes from `jump_step` in [the config](../dev/config.md).
- Undo history is kept only for the current opened item and is lost after save, navigation, or exit.
