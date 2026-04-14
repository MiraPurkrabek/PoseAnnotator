import argparse
import os

import cv2
import numpy as np

from src.annotator_config import DEFAULT_CONFIG_PATH, load_annotator_config
from src.interactive_annotator import InteractiveAnnotator
from src.json_utils import (
    authenticate_drive,
    build_pose_output_path,
    increment_idx,
    infer_image_dir,
    load_annotations,
    resolve_pose_annotations_path,
    save_annotations,
    upload_annotations,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "coco_filepath",
        type=str,
        help="Filename of the coco annotations file or dataset sequence name",
    )
    parser.add_argument("--img-path", type=str, help="Path to the folder with images", default=None)
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the annotator configuration file",
    )

    # Optional arguments
    parser.add_argument(
        "--pose-format",
        type=str,
        default=None,
        help="Format of the annotated skeleton (defaults to the INI config)",
    )
    parser.add_argument("--without-hands", default=True, action=argparse.BooleanOptionalAction)
    parser.add_argument("--save", default=True, action=argparse.BooleanOptionalAction)
    parser.add_argument("--cloud-upload", default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--cloud-folder",
        type=str,
        help="Google Drive folder ID for uploading annotations",
        default="root",
    )

    args = parser.parse_args()
    return args


def build_interactive_annotator(annotations, ann_idx, img_path, id2name, config, pose_format):
    image_path = os.path.join(img_path, id2name[annotations[ann_idx]["image_id"]])
    return InteractiveAnnotator(
        annotations[ann_idx],
        image_path,
        is_start=ann_idx == 0,
        with_example=config.show_example,
        two_scales=config.two_scales,
        inf_size=config.inf_size,
        default_bbox_padding=config.default_bbox_padding,
        click_radius_ratio=config.click_radius_ratio,
        fps=config.drag_redraw_fps,
        history_size=config.history_size,
        visibility_levels=config.visibility_levels,
        mark_checked_interval_seconds=config.mark_checked_interval_seconds,
        pose_format=pose_format,
    )


def main(args):
    config = load_annotator_config(args.config)
    args.pose_format = (args.pose_format or config.pose_format).lower()
    implemented_formats = ["coco", "coco_with_thumbs"]
    if args.pose_format not in implemented_formats:
        raise NotImplementedError(
            "Format {:s} not implemented. Use one of the following: {}".format(args.pose_format, implemented_formats)
        )

    args.coco_filepath = resolve_pose_annotations_path(
        args.coco_filepath,
        config.sequence_root,
        config.output_suffix,
    )
    assert os.path.exists(args.coco_filepath), "COCO annotations file ({:s}) not found".format(args.coco_filepath)
    assert os.path.isfile(args.coco_filepath), "COCO annotations file ({:s}) is not a file".format(args.coco_filepath)

    if args.img_path is None:
        args.img_path = infer_image_dir(args.coco_filepath, config.output_suffix)

    # Load the data
    coco_data, id2name, _, _ = load_annotations(args.coco_filepath)
    ann_idx = 0

    new_coco_filepath = build_pose_output_path(args.coco_filepath, config.output_suffix)
    if args.cloud_upload:
        from pydrive.drive import GoogleDrive

        gauth = authenticate_drive()
        drive = GoogleDrive(gauth)
        folder_id = args.cloud_folder
        file_name = os.path.basename(new_coco_filepath)

    annotations = coco_data["annotations"]

    cv2.namedWindow("Image", cv2.WINDOW_GUI_NORMAL)
    ia = build_interactive_annotator(
        annotations,
        ann_idx,
        args.img_path,
        id2name,
        config,
        args.pose_format,
    )
    cv2.setMouseCallback("Image", ia.mouse_callback)

    while cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) > 0:
        # The function waitKey waits for a key event infinitely (when delay<=0)
        k = cv2.waitKey(100)
        if k == ord("m") or k == 83:  # toggle current image
            annotations[ann_idx] = ia.get_annotation(json_compatible=True)
            ann_idx = increment_idx(ann_idx, len(annotations), 1)

            ia = build_interactive_annotator(
                annotations,
                ann_idx,
                args.img_path,
                id2name,
                config,
                args.pose_format,
            )
            coco_data["annotations"] = annotations
            save_annotations(new_coco_filepath, coco_data, update_date=True, save=args.save)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        elif k == ord("."):  # jump 10
            annotations[ann_idx] = ia.get_annotation(json_compatible=True)
            ann_idx = increment_idx(ann_idx, len(annotations), config.jump_step)

            ia = build_interactive_annotator(
                annotations,
                ann_idx,
                args.img_path,
                id2name,
                config,
                args.pose_format,
            )
            coco_data["annotations"] = annotations
            save_annotations(new_coco_filepath, coco_data, update_date=True, save=args.save)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        elif k == ord(","):  # jump -10
            annotations[ann_idx] = ia.get_annotation(json_compatible=True)
            ann_idx = increment_idx(ann_idx, len(annotations), -config.jump_step)

            ia = build_interactive_annotator(
                annotations,
                ann_idx,
                args.img_path,
                id2name,
                config,
                args.pose_format,
            )
            coco_data["annotations"] = annotations
            save_annotations(new_coco_filepath, coco_data, update_date=True, save=args.save)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        elif k == ord("n") or k == 81:
            annotations[ann_idx] = ia.get_annotation(json_compatible=True)
            ann_idx = increment_idx(ann_idx, len(annotations), -1)

            ia = build_interactive_annotator(
                annotations,
                ann_idx,
                args.img_path,
                id2name,
                config,
                args.pose_format,
            )
            coco_data["annotations"] = annotations
            save_annotations(new_coco_filepath, coco_data, update_date=True, save=args.save)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        elif k == ord("x"):
            annotations[ann_idx] = ia.get_annotation(json_compatible=True)
            ann_idx = np.random.randint(len(annotations))

            ia = build_interactive_annotator(
                annotations,
                ann_idx,
                args.img_path,
                id2name,
                config,
                args.pose_format,
            )
            coco_data["annotations"] = annotations
            save_annotations(new_coco_filepath, coco_data, update_date=True, save=args.save)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        elif k == ord("q"):
            annotations[ann_idx] = ia.get_annotation(json_compatible=True)
            break
        elif k == ord("u"):
            annotations[ann_idx] = ia.get_annotation(json_compatible=True)
            while "checked" in annotations[ann_idx].keys():
                ann_idx = increment_idx(ann_idx, len(annotations), 1)

            ia = build_interactive_annotator(
                annotations,
                ann_idx,
                args.img_path,
                id2name,
                config,
                args.pose_format,
            )
            coco_data["annotations"] = annotations
            save_annotations(new_coco_filepath, coco_data, update_date=True, save=args.save)

            cv2.setMouseCallback("Image", ia.mouse_callback)
        else:
            ia.key_pressed(k)

    cv2.destroyAllWindows()
    coco_data["annotations"] = annotations
    save_annotations(new_coco_filepath, coco_data, update_date=True, save=args.save)
    if args.cloud_upload:
        upload_annotations(drive, coco_data, file_name, folder_id)


if __name__ == "__main__":
    args = parse_args()
    main(args)
