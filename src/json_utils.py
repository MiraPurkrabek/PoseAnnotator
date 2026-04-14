import datetime
import json
import os

POSE_ANNOTATIONS_FILENAME = "person_keypoints_val2017.json"


def load_annotations(annotations_file):
    """
    Load annotations from a JSON file.

    Args:
        annotations_file (str): The path to the JSON file containing the annotations.

    Returns:
        tuple: A tuple containing the following:
            - coco_data (dict): The loaded JSON data.
            - id2name (dict): A dictionary mapping image IDs to file names.
            - name2id (dict): A dictionary mapping file names to image IDs.
            - ann_dict (dict): A dictionary mapping image IDs to a list of annotations.
    """
    with open(annotations_file, "r") as f:
        coco_data = json.load(f)

    id2name = {}
    name2id = {}
    ann_dict = {}
    for img in coco_data["images"]:
        id2name[img["id"]] = img["file_name"]
        name2id[img["file_name"]] = img["id"]
        ann_dict[img["id"]] = []

    for ann in coco_data["annotations"]:
        ann_dict[ann["image_id"]].append(ann)

    return coco_data, id2name, name2id, ann_dict


def save_annotations(annotations_file, annotations, update_date=False, save=True):
    """
    Save the annotations to a JSON file.

    Args:
        annotations_file (str): The path to the JSON file where the annotations will be saved.
        annotations (dict): The annotations to be saved.
        update_date (bool, optional): Whether to update the "date_created" field in the annotations. Defaults to False.
        save (bool, optional): Whether to save the annotations. If set to False, the function will return without saving. Defaults to True.
    """
    if not save:
        return
    if update_date:
        if "info" not in annotations:
            annotations["info"] = {}
        annotations["info"]["date_created"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    with open(annotations_file, "w") as f:
        json.dump(annotations, f, indent=2)


def save_annotations_by_image(annotations_file, annotations, ann_dict, update_date=False, save=True):
    """
    Save annotations stored in a per-image dictionary to a COCO annotations file.

    Args:
        annotations_file (str): Destination JSON file.
        annotations (dict): COCO annotations payload.
        ann_dict (dict): Mapping from image IDs to lists of annotations.
        update_date (bool, optional): Whether to update ``info.date_created``.
        save (bool, optional): Whether to write the file.
    """
    annotations["annotations"] = []
    for ann_list in ann_dict.values():
        annotations["annotations"].extend(ann_list)

    save_annotations(
        annotations_file,
        annotations,
        update_date=update_date,
        save=save,
    )


def increment_idx(idx, len_annotations, increment):
    """
    Increments the given index by the specified increment, taking into account the length of the annotations.

    Args:
        idx (int): The current index.
        len_annotations (int): The length of the annotations.
        increment (int): The amount by which to increment the index.

    Returns:
        int: The updated index value.
    """
    idx += increment
    if idx >= len_annotations:
        idx = 0
    elif idx < 0:
        idx = len_annotations - 1
    return idx


def has_output_suffix(filepath, output_suffix):
    """
    Check whether the given file stem already ends with the configured suffix.
    """
    stem, _ = os.path.splitext(filepath)
    return bool(output_suffix) and stem.endswith(output_suffix)


def build_pose_output_path(annotations_file, output_suffix):
    """
    Build the output path for pose annotations without double-appending the suffix.
    """
    stem, ext = os.path.splitext(annotations_file)
    if has_output_suffix(annotations_file, output_suffix):
        return annotations_file
    return "{:s}{:s}{:s}".format(stem, output_suffix, ext)


def _build_pose_annotations_path(dataset_root):
    return os.path.join(dataset_root, "annotations", POSE_ANNOTATIONS_FILENAME)


def _choose_existing_pose_annotations_path(annotations_file, output_suffix):
    output_file = build_pose_output_path(annotations_file, output_suffix)
    legacy_output_file = build_pose_output_path(annotations_file, "_kpts")
    for candidate in [output_file, legacy_output_file, annotations_file]:
        if os.path.exists(candidate):
            return candidate
    return annotations_file


def resolve_bbox_dataset_path(coco_folder, sequence_root):
    """
    Resolve a bbox dataset path from either an explicit path or a shorthand sequence name.
    """
    if os.path.exists(coco_folder):
        return os.path.abspath(coco_folder)
    return os.path.abspath(os.path.join(sequence_root, coco_folder))


def resolve_pose_annotations_path(coco_filepath, sequence_root, output_suffix):
    """
    Resolve a pose annotations path from an explicit path or a shorthand sequence name.
    """
    if os.path.exists(coco_filepath):
        resolved_path = os.path.abspath(coco_filepath)
        if os.path.isfile(resolved_path):
            return resolved_path
        if os.path.isdir(resolved_path):
            annotations_file = _build_pose_annotations_path(resolved_path)
            return _choose_existing_pose_annotations_path(annotations_file, output_suffix)

    dataset_root = os.path.join(sequence_root, coco_filepath)
    annotations_file = _build_pose_annotations_path(dataset_root)
    return _choose_existing_pose_annotations_path(annotations_file, output_suffix)


def infer_image_dir(annotations_file, output_suffix):
    """
    Infer the image directory from a pose annotations filename.
    """
    ann_filename = os.path.splitext(os.path.basename(annotations_file))[0]
    for suffix in [output_suffix, "_kpts"]:
        if suffix and ann_filename.endswith(suffix):
            ann_filename = ann_filename[: -len(suffix)]

    ann_type = ann_filename.split("_")[-1]
    if ann_type not in ["train2017", "val2017"]:
        print("Could not determine image directory from annotations file name. Using 'val2017' as default.")
        ann_type = "val2017"

    coco_ann_root = os.path.dirname(annotations_file)
    return os.path.join(os.path.dirname(coco_ann_root), ann_type)


def authenticate_drive():
    """
    Authenticates the user with Google Drive using OAuth2.
    Uses existing credentials if authenticated previously.
    Otherwise opens the browser for re-authenticaation and saves the credentials.
    Returns:
        GoogleAuth: Authenticated GoogleAuth object.
    """
    from pydrive.auth import GoogleAuth

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials.json")
    if not gauth.credentials:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("credentials.json")
    return gauth


def upload_annotations(drive, annotations, file_name, folder_id):
    """
    Uploads the given annotations to Google Drive. If the file already exists, it updates the file.
    Otherwise, it creates a new file.

    Args:
        drive (GoogleDrive): Authenticated GoogleDrive object.
        annotations (dict): Annotations to be uploaded.
        file_name (str): Name of the file uploaded.
        folder_id (str): Google Drive folder ID where the file will be uploaded.
    """
    query = f"'{folder_id}' in parents and title = '{file_name}' and trashed = false"
    file_list = drive.ListFile({"q": query}).GetList()
    if file_list:
        gfile = file_list[0]
        print(f"File '{file_name}' exists. It will be updated.")
    else:
        if folder_id is None:
            gfile = drive.CreateFile({"title": file_name})
        else:
            gfile = drive.CreateFile({"title": file_name, "parents": [{"id": folder_id}]})
        print(f"File '{file_name}' does not exist. It will be created.")

    annotations["info"]["date_created"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    gfile.SetContentString(json.dumps(annotations, indent=2))
    gfile.Upload()
    print(f"File '{file_name}' uploaded successfully to drive.")
