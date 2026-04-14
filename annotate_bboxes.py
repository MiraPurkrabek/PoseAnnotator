import argparse
import datetime
import json
import os

import cv2
import numpy as np

from src.annotator_config import DEFAULT_CONFIG_PATH, load_annotator_config
from src.bbox_annotator import BboxAnnotator
from src.json_utils import (
    authenticate_drive,
    increment_idx,
    load_annotations,
    resolve_bbox_dataset_path,
    save_annotations_by_image,
    upload_annotations,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "coco_folder",
        type=str,
        help="Folder containing the dataset for annotation or a shorthand sequence name",
    )
    parser.add_argument("--img-path", type=str, help="Path to the folder with images", default=None)
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the annotator configuration file",
    )
    parser.add_argument("--cloud-upload", default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--cloud-folder",
        type=str,
        help="Google Drive folder ID for uploading annotations",
        default="root",
    )

    args = parser.parse_args()
    return args


def prepare_filestructure(args):
    if args.coco_folder == args.img_path:
        # Create a new folder for the images and annotations
        new_img_path = os.path.join(args.coco_folder, "val2017")
        os.makedirs(new_img_path, exist_ok=True)

        # Move all images to the new folder
        for img in os.listdir(args.img_path):
            os.rename(os.path.join(args.img_path, img), os.path.join(new_img_path, img))
        args.img_path = new_img_path

    # Create a new folder for the annotations
    new_ann_path = os.path.join(args.coco_folder, "annotations")
    os.makedirs(new_ann_path, exist_ok=True)
    return args


def get_ann_filepath(args):
    ann_filename = os.path.join(args.coco_folder, "annotations", "person_keypoints_val2017.json")
    if not (os.path.exists(ann_filename) and os.path.isfile(ann_filename)):
        create_ann_file(ann_filename, args.img_path)

    return ann_filename


def create_ann_file(ann_filename, img_path):
    ann_dict = {
        "info": {
            "year": datetime.datetime.now().strftime("%Y"),
            "version": 1.0,
            "description": "COCO-like dataset created at the CTU in Prague",
            "author": "Miroslav Purkrabek",
            "date_created": datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
        },
        "images": [],
        "categories": [
            {
                "supercategory": "person",
                "id": 1,
                "name": "person",
                "keypoints": [
                    "nose",
                    "left_eye",
                    "right_eye",
                    "left_ear",
                    "right_ear",
                    "left_shoulder",
                    "right_shoulder",
                    "left_elbow",
                    "right_elbow",
                    "left_wrist",
                    "right_wrist",
                    "left_hip",
                    "right_hip",
                    "left_knee",
                    "right_knee",
                    "left_ankle",
                    "right_ankle",
                ],
                "skeleton": [
                    [16, 14],
                    [14, 12],
                    [17, 15],
                    [15, 13],
                    [12, 13],
                    [6, 12],
                    [7, 13],
                    [6, 7],
                    [6, 8],
                    [7, 9],
                    [8, 10],
                    [9, 11],
                    [2, 3],
                    [1, 2],
                    [1, 3],
                    [2, 4],
                    [3, 5],
                    [4, 6],
                    [5, 7],
                ],
            }
        ],
    }

    for img_i, img_name in enumerate(os.listdir(img_path)):
        img = cv2.imread(os.path.join(img_path, img_name))
        ann_dict["images"].append(
            {
                "id": img_i,
                "file_name": img_name,
                "width": img.shape[1],
                "height": img.shape[0],
                "date_captured": datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
            }
        )

    ann_dict["annotations"] = []

    with open(ann_filename, "w") as f:
        json.dump(ann_dict, f, indent=2)


def main(args):
    config = load_annotator_config(args.config)
    args.coco_folder = resolve_bbox_dataset_path(args.coco_folder, config.sequence_root)

    assert os.path.exists(args.coco_folder), "Given folder ({:s}) not found".format(args.coco_folder)
    assert os.path.isdir(args.coco_folder), "Given folder ({:s}) is not a folder".format(args.coco_folder)

    if args.img_path is None:
        subdirs = [d for d in os.listdir(args.coco_folder) if os.path.isdir(os.path.join(args.coco_folder, d))]
        if "val2017" in subdirs:
            args.img_path = os.path.join(args.coco_folder, "val2017")
        elif "images" in subdirs:
            args.img_path = os.path.join(args.coco_folder, "images")
        else:
            args.img_path = args.coco_folder

    args = prepare_filestructure(args)

    # Load the data
    coco_data, _, _, ann_dict = load_annotations(get_ann_filepath(args))
    img_list = [(img["file_name"], img["id"]) for img in coco_data["images"]]
    img_idx = 0
    save_path = os.path.join(args.coco_folder, "annotations", "person_keypoints_val2017.json")

    if args.cloud_upload:
        from pydrive.drive import GoogleDrive

        gauth = authenticate_drive()
        drive = GoogleDrive(gauth)
        folder_id = args.cloud_folder
        file_name = os.path.basename(save_path)

    cv2.namedWindow("Image", cv2.WINDOW_GUI_NORMAL)
    ia = BboxAnnotator(
        ann_dict[img_list[img_idx][1]],
        img_list[img_idx][1],
        os.path.join(args.img_path, img_list[img_idx][0]),
        is_start=img_idx == 0,
        fps=config.drag_redraw_fps,
        click_radius_ratio=config.click_radius_ratio,
        history_size=config.history_size,
        mark_checked_interval_seconds=config.mark_checked_interval_seconds,
    )
    cv2.setMouseCallback("Image", ia.mouse_callback)

    while cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) > 0:
        # The function waitKey waits for a key event infinitely (when delay<=0)
        k = cv2.waitKey(100)
        if k == ord("m") or k == 83:  # toggle current image
            ann_dict[img_list[img_idx][1]] = ia.get_annotation(json_compatible=True)
            img_idx = increment_idx(img_idx, len(img_list), 1)

            ia = BboxAnnotator(
                ann_dict[img_list[img_idx][1]],
                img_list[img_idx][1],
                os.path.join(args.img_path, img_list[img_idx][0]),
                is_start=img_idx == 0,
                fps=config.drag_redraw_fps,
                click_radius_ratio=config.click_radius_ratio,
                history_size=config.history_size,
                mark_checked_interval_seconds=config.mark_checked_interval_seconds,
            )
            save_annotations_by_image(save_path, coco_data, ann_dict, update_date=True)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        elif k == ord("n") or k == 81:
            ann_dict[img_list[img_idx][1]] = ia.get_annotation(json_compatible=True)
            img_idx = increment_idx(img_idx, len(img_list), -1)

            ia = BboxAnnotator(
                ann_dict[img_list[img_idx][1]],
                img_list[img_idx][1],
                os.path.join(args.img_path, img_list[img_idx][0]),
                is_start=img_idx == 0,
                fps=config.drag_redraw_fps,
                click_radius_ratio=config.click_radius_ratio,
                history_size=config.history_size,
                mark_checked_interval_seconds=config.mark_checked_interval_seconds,
            )
            save_annotations_by_image(save_path, coco_data, ann_dict, update_date=True)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        elif k == ord(",") or k == 83:  # toggle current image
            ann_dict[img_list[img_idx][1]] = ia.get_annotation(json_compatible=True)
            img_idx = increment_idx(img_idx, len(img_list), -config.jump_step)

            ia = BboxAnnotator(
                ann_dict[img_list[img_idx][1]],
                img_list[img_idx][1],
                os.path.join(args.img_path, img_list[img_idx][0]),
                is_start=img_idx == 0,
                fps=config.drag_redraw_fps,
                click_radius_ratio=config.click_radius_ratio,
                history_size=config.history_size,
                mark_checked_interval_seconds=config.mark_checked_interval_seconds,
            )
            save_annotations_by_image(save_path, coco_data, ann_dict, update_date=True)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        elif k == ord(".") or k == 81:
            ann_dict[img_list[img_idx][1]] = ia.get_annotation(json_compatible=True)
            img_idx = increment_idx(img_idx, len(img_list), config.jump_step)

            ia = BboxAnnotator(
                ann_dict[img_list[img_idx][1]],
                img_list[img_idx][1],
                os.path.join(args.img_path, img_list[img_idx][0]),
                is_start=img_idx == 0,
                fps=config.drag_redraw_fps,
                click_radius_ratio=config.click_radius_ratio,
                history_size=config.history_size,
                mark_checked_interval_seconds=config.mark_checked_interval_seconds,
            )
            save_annotations_by_image(save_path, coco_data, ann_dict, update_date=True)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        elif k == ord("x"):
            ann_dict[img_list[img_idx][1]] = ia.get_annotation(json_compatible=True)
            img_idx = np.random.randint(len(img_list))

            ia = BboxAnnotator(
                ann_dict[img_list[img_idx][1]],
                img_list[img_idx][1],
                os.path.join(args.img_path, img_list[img_idx][0]),
                is_start=img_idx == 0,
                fps=config.drag_redraw_fps,
                click_radius_ratio=config.click_radius_ratio,
                history_size=config.history_size,
                mark_checked_interval_seconds=config.mark_checked_interval_seconds,
            )
            save_annotations_by_image(save_path, coco_data, ann_dict, update_date=True)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        elif k == ord("q"):
            ann_dict[img_list[img_idx][1]] = ia.get_annotation(json_compatible=True)
            break
        elif k == ord("u"):
            ann_dict[img_list[img_idx][1]] = ia.get_annotation(json_compatible=True)
            while not ann_dict[img_list[img_idx][1]] == []:
                img_idx = increment_idx(img_idx, len(img_list), 1)

            ia = BboxAnnotator(
                ann_dict[img_list[img_idx][1]],
                img_list[img_idx][1],
                os.path.join(args.img_path, img_list[img_idx][0]),
                is_start=img_idx == 0,
                fps=config.drag_redraw_fps,
                click_radius_ratio=config.click_radius_ratio,
                history_size=config.history_size,
                mark_checked_interval_seconds=config.mark_checked_interval_seconds,
            )
            save_annotations_by_image(save_path, coco_data, ann_dict, update_date=True)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        else:
            ia.key_pressed(k)

    cv2.destroyAllWindows()
    save_annotations_by_image(save_path, coco_data, ann_dict, update_date=True)
    if args.cloud_upload:
        upload_annotations(drive, coco_data, file_name, folder_id)


if __name__ == "__main__":
    args = parse_args()
    main(args)
