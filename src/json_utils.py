import datetime
import json

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
    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        gfile = file_list[0]
        print(f"File '{file_name}' exists. It will be updated.")
    else:
        if folder_id is None:
            gfile = drive.CreateFile({'title': file_name})
        else:
            gfile = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
        print(f"File '{file_name}' does not exist. It will be created.")
        
    annotations["info"]["date_created"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    gfile.SetContentString(json.dumps(annotations, indent=2))
    gfile.Upload()
    print(f"File '{file_name}' uploaded successfully to drive.")
