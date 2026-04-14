# Annotation Workflow

## Recommended Order

1. Start with bounding boxes.
2. Save and review the generated COCO-style annotation file.
3. Open pose annotation and label one person annotation at a time.
4. Use random checks and unfinished-item navigation during review.

## Bounding Boxes

Run:

```bash
python annotate_bboxes.py <dataset-folder-or-sequence>
```

This stage creates or updates:

`annotations/person_keypoints_val2017.json`

Use bbox annotation when:
- starting a new dataset
- correcting person boxes
- preparing data for pose annotation

## Pose Annotation

Run:

```bash
python annotate_pose.py <annotation-file-or-sequence>
```

By default, pose annotation writes to a suffixed file such as:

`person_keypoints_val2017_manual.json`

If you open an already suffixed file, the app saves back into that same file.

## Saving Behavior

- switching to another item saves progress
- quitting saves progress
- bbox annotation saves in place
- pose annotation saves to the configured suffixed output file

If needed, you can inspect pose data without writing changes:

```bash
python annotate_pose.py <input> --no-save
```

## Shorthand Sequences

Both entrypoints can resolve a bare sequence name through `sequence_root` in [annotator_config.ini](../../annotator_config.ini).

Examples:

```bash
python annotate_bboxes.py BOTTOM
python annotate_pose.py BOTTOM
```

## Checked And Unfinished Items

The app marks annotations as `checked` after they stay open for a configured amount of time. The `u` shortcut skips to the next unfinished item.

That timing is controlled in [the config](../dev/config.md).

## Optional Google Drive Upload

Results can be uploaded to Google Drive for backup or shared progress tracking.

Example:

```bash
python annotate_pose.py <input> --cloud-upload
```

To save into a specific Drive folder:

```bash
python annotate_pose.py <input> --cloud-upload --cloud-folder <folder-id>
```

The same upload option is available for bbox annotation.

### Google Drive Setup

Google Drive upload uses OAuth2 and requires a local `client_secrets.json` file.

1. Create a project in Google APIs Console.
2. Enable Google Drive API for that project.
3. Open the credentials page and create an OAuth client ID.
4. Configure the consent screen if Google asks for it.
5. Create a Web application credential with `http://localhost:8080/` as an authorized redirect URI.
6. Download the credential JSON file.
7. Rename it to `client_secrets.json` and place it in your working directory before running the app with `--cloud-upload`.
