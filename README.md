# PoseAnnotator

PoseAnnotator is a local Python/OpenCV app for annotating person bounding boxes and 2D human poses in images. It is designed for COCO-style workflows and focuses on fast manual annotation with pose-aware visualization.

![PoseAnnotator demo](docs/images/correct.gif)

The repository serves two audiences:
- annotators who need to run the app and produce consistent labels
- developers who need to understand, extend, or maintain the codebase

## For Annotators

Start here if you want to use the app for labeling.

- [Annotator docs index](docs/README.md#annotator-docs)
- [Getting started](docs/annotators/getting-started.md)
- [Workflow](docs/annotators/workflow.md)
- [Keyboard shortcuts](docs/annotators/shortcuts.md)
- [Pose and visibility rules](docs/annotators/pose-and-visibility.md)

Minimal commands:

```bash
python annotate_bboxes.py <dataset-folder-or-sequence>
python annotate_pose.py <annotation-file-or-sequence>
```

## For Developers

Start here if you want to install the project locally, understand the structure, or contribute changes.

- [Developer docs index](docs/README.md#developer-docs)
- [Project overview](docs/dev/overview.md)
- [Setup](docs/dev/setup.md)
- [Codebase guide](docs/dev/codebase.md)
- [Contributing](docs/dev/contributing.md)
- [Configuration reference](docs/dev/config.md)

Minimal setup:

```bash
pip install -r requirements.txt
pre-commit install
```

## Quick Notes

- The app is configured through [annotator_config.ini](annotator_config.ini).
- You can pass full paths or shorthand sequence names resolved under `sequence_root`.
- Pose annotations are written to a suffixed file such as `*_manual.json` by default.
- Google Drive upload is supported as an optional feature.

## Contributing

Please read [docs/dev/contributing.md](docs/dev/contributing.md) before making code changes. The short version is: keep the current repo structure, use `pre-commit`, and update docs when behavior changes.

## Maintainers And Contributors

Maintainers:
- [Miroslav Purkrabek](https://github.com/MiraPurkrabek) - main author and maintainer

Contributors:
- [Adela Subrtova](https://github.com/subrtadel)
- [Fizza Rubab](https://github.com/Fizza-Rubab)

## Citation

If you use the tool for research, please consider citing:

```bibtex
@misc{PoseAnnotator2024,
    title={PoseAnnotator},
    author={PoseAnnotator contributors},
    howpublished = {\url{https://github.com/MiraPurkrabek/PoseAnnotator}},
    year={2024}
}
```
