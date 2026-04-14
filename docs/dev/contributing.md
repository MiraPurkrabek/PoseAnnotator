# Contributing

## General Expectations

Keep the current project shape:
- top-level entrypoints remain [annotate_bboxes.py](../../annotate_bboxes.py) and [annotate_pose.py](../../annotate_pose.py)
- shared runtime code stays in [src/](../../src)
- one-off experiments and temporary scripts should not be added to the main app surface

When you change behavior, update the relevant docs in `README.md` and `docs/`.

## Code Style

- use `pre-commit`
- keep edits small and readable
- prefer existing naming and module boundaries over introducing new abstractions
- keep dependencies lightweight unless there is a strong reason to add one

Install hooks with:

```bash
pre-commit install
```

Run them manually with:

```bash
pre-commit run --all-files
```

## Validation

Before submitting changes, do the lightweight checks available in this repo:

```bash
python -m py_compile annotate_bboxes.py annotate_pose.py src/*.py tools/*.py
```

If you changed runtime behavior, also do a short manual smoke test:
- open bbox annotation on a small dataset
- open pose annotation on a small annotation file
- verify save paths and navigation behavior

## Docs Expectations

This repo has separate docs for developers and annotators. Keep that distinction clear:
- developer docs explain code, setup, structure, and contribution
- annotator docs explain operation, workflow, and labeling rules

If you add a new visible feature, document:
- how to enable or configure it
- how it changes the annotator workflow, if applicable
- any new keyboard shortcut or saved-file behavior

## Useful References

- [Project overview](overview.md)
- [Setup](setup.md)
- [Codebase guide](codebase.md)
- [Configuration reference](config.md)
