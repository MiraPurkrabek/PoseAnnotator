# Description: This script transforms the keypoints annotations to COCO format.
# Usage: python transform_to_coco.py <annotation_file>

import argparse
import json

import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze annotation file")
    parser.add_argument("annot_path", type=str, help="Path to annotation file")

    return parser.parse_args()


def _fix_aspect_ratio(bbox_scale: np.ndarray, aspect_ratio: float) -> np.ndarray:
    """Extend the scale to match the given aspect ratio.

    Args:
        scale (np.ndarray): The image scale (w, h) in shape (2, )
        aspect_ratio (float): The ratio of ``w/h``

    Returns:
        np.ndarray: The reshaped image scale in (2, )
    """
    w, h = np.hsplit(bbox_scale, [1])
    bbox_scale = np.where(w > h * aspect_ratio, np.hstack([w, w / aspect_ratio]), np.hstack([h * aspect_ratio, h]))
    return bbox_scale


def bbox_xywh2cs(bbox: np.ndarray, padding: float = 1.0, aspect_ratio: float = None) -> tuple:
    """Transform the bbox format from (x,y,w,h) into (center, scale)

    Args:
        bbox (ndarray): Bounding box(es) in shape (4,) or (n, 4), formatted
            as (x, y, h, w)
        padding (float): BBox padding factor that will be multilied to scale.
            Default: 1.0

    Returns:
        tuple: A tuple containing center and scale.
        - np.ndarray[float32]: Center (x, y) of the bbox in shape (2,) or
            (n, 2)
        - np.ndarray[float32]: Scale (w, h) of the bbox in shape (2,) or
            (n, 2)
    """

    # convert single bbox from (4, ) to (1, 4)
    dim = bbox.ndim
    if dim == 1:
        bbox = bbox[None, :]

    x, y, w, h = np.hsplit(bbox, [1, 2, 3])
    center = np.hstack([x + w * 0.5, y + h * 0.5])
    scale = np.hstack([w, h]) * padding

    if dim == 1:
        center = center[0]
        scale = scale[0]

    if aspect_ratio is not None:
        scale = _fix_aspect_ratio(scale, aspect_ratio)

    return center, scale


def bbox_cs2xywh(center: np.ndarray, scale: np.ndarray, padding: float = 1.0) -> np.ndarray:
    """Transform the bbox format from (center, scale) to (x,y,w,h).

    Args:
        center (ndarray): BBox center (x, y) in shape (2,) or (n, 2)
        scale (ndarray): BBox scale (w, h) in shape (2,) or (n, 2)
        padding (float): BBox padding factor that will be multilied to scale.
            Default: 1.0

    Returns:
        ndarray[float32]: BBox (x, y, w, h) in shape (4, ) or (n, 4)
    """

    dim = center.ndim
    assert scale.ndim == dim

    if dim == 1:
        center = center[None, :]
        scale = scale[None, :]

    wh = scale / padding
    xy = center - 0.5 * wh
    bbox = np.hstack((xy, wh))

    if dim == 1:
        bbox = bbox[0]

    return bbox


def main(annot_path):
    with open(annot_path, "r") as f:
        data = json.load(f)

    # Make img id to img name mapping
    img_id_to_name = {}
    for img in data["images"]:
        img_id_to_name[img["id"]] = img

    for ann in data["annotations"]:
        # No keypoints --> skip
        if "keypoints" not in ann.keys():
            continue
        kpts = np.array(ann["keypoints"]).reshape(-1, 3)

        # No keypoints annotated --> skip
        if np.all(kpts[:, 2] == 0):
            continue

        # Normalize keypoints
        h = img_id_to_name[ann["image_id"]]["height"]
        w = img_id_to_name[ann["image_id"]]["width"]
        bbox = np.array(ann["bbox"])
        bbox_center = bbox[:2] + bbox[2:] / 2
        in_img = (kpts[:, 0] >= 0) & (kpts[:, 0] < w) & (kpts[:, 1] >= 0) & (kpts[:, 1] < h)
        in_bbox_x = (kpts[:, 0] >= bbox[0]) & (kpts[:, 0] < bbox[0] + bbox[2])
        in_bbox_y = (kpts[:, 1] >= bbox[1]) & (kpts[:, 1] < bbox[1] + bbox[3])
        in_bbox_x & in_bbox_y

        center, scale = bbox_xywh2cs(bbox, padding=1.25, aspect_ratio=3 / 4)
        ex_bbox = bbox_cs2xywh(center, scale, padding=1.25)
        in_ex_bbox = (
            (kpts[:, 0] >= ex_bbox[0])
            & (kpts[:, 0] < ex_bbox[0] + ex_bbox[2])
            & (kpts[:, 1] >= ex_bbox[1])
            & (kpts[:, 1] < ex_bbox[1] + ex_bbox[3])
        )

        # If keypoints are out of image, mark them as un-annotated
        kpts[~in_img, 2] = 0

        # If keypoints have visibility bigger than 2, mark them as un-annotated
        kpts[kpts[:, 2] > 2, 2] = 0

        # Zero-out un-annotated keypoints
        kpts[kpts[:, 2] == 0, :2] = 0

        ann["keypoints"] = kpts.flatten().tolist()

    save_path = annot_path.replace(".json", "_coco.json")
    with open(save_path, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    args = parse_args()
    main(args.annot_path)
