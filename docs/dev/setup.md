# Developer Setup

## Requirements

The project is developed for Linux and currently targets Python 3.10.

Core dependencies:
- `numpy`
- `opencv-python`
- `pre-commit`
- formatting helpers from [requirements.txt](../../requirements.txt)

Optional dependency:
- `PyDrive` for Google Drive upload

## Install

Using `pip`:

```bash
pip install -r requirements.txt
```

Using Conda:

```bash
conda env create -f environment.yml
conda activate PoseAnnotator
```

## Configure

The default config file is [annotator_config.ini](../../annotator_config.ini).

- Adjust it in place for local usage, or
- pass `--config <path>` to either entrypoint to use another INI file

The full setting reference is in [config.md](config.md).

## Run The App

Bounding boxes:

```bash
python annotate_bboxes.py <dataset-folder-or-sequence>
```

Pose annotation:

```bash
python annotate_pose.py <annotation-file-or-sequence>
```

Useful pose options:

```bash
python annotate_pose.py <input> --config <path>
python annotate_pose.py <input> --pose-format coco_with_thumbs
python annotate_pose.py <input> --no-save
```

## Development Workflow

Install the formatting hooks:

```bash
pre-commit install
```

Recommended checks before committing:

```bash
pre-commit run --all-files
python -m py_compile annotate_bboxes.py annotate_pose.py src/*.py tools/*.py
```

There are no full automated GUI tests in the repo, so manual smoke testing of the OpenCV flows is still important after behavior changes.
