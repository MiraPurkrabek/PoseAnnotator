# Description: Analyze annotation file and print statistics. Works with COCO format.
# Usage: python analyze_annot.py <annotation_file>

import argparse
import json

import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze annotation file")
    parser.add_argument("annot_path", type=str, help="Path to annotation file")

    return parser.parse_args()


def main(annot_path):
    with open(annot_path, "r") as f:
        data = json.load(f)

    print("Annotation file has {} images and {} annotations".format(len(data["images"]), len(data["annotations"])))

    # Go through annotations and count bboxes and keypoints
    n_bboxes = 0
    n_kpts = 0
    n_full_kpts = 0
    n_img_w_kpts = []
    n_img_w_bboxes = []
    for ann in data["annotations"]:
        if "bbox" in ann.keys():
            bbox = np.array(ann["bbox"])
            if not np.allclose(bbox, np.zeros_like(bbox)):
                n_bboxes += 1
                n_img_w_bboxes.append(ann["image_id"])

            if "keypoints" in ann.keys():
                kpts = np.array(ann["keypoints"])
                if not np.allclose(kpts, np.zeros_like(kpts)):
                    n_kpts += 1
                    n_img_w_kpts.append(ann["image_id"])

                    if np.all(kpts[2::3] > 0):
                        n_full_kpts += 1

    print(
        "Found {} bboxes of which {} has keypoints annotated. ({:.2f} %)".format(
            n_bboxes, n_kpts, n_kpts / n_bboxes * 100
        )
    )
    if n_kpts > 0:
        print("{} of bboxes have all keypoints annotated. ({:.2f} %)".format(n_full_kpts, n_full_kpts / n_kpts * 100))
    else:
        print("{:d} of bboxes have all keypoints annotated. ({:.2f} %)".format(0, 0.0))

    unique_imgs_w_kpts, imgs_w_kpts_counts = np.unique(n_img_w_kpts, return_counts=True)
    unique_imgs_w_bboxes, imgs_w_bboxes_counts = np.unique(n_img_w_bboxes, return_counts=True)

    print(
        "Found {} ({:.2f} %) unique images with bboxes, last annotated image is {}".format(
            len(unique_imgs_w_bboxes),
            len(unique_imgs_w_bboxes) / len(data["images"]) * 100,
            unique_imgs_w_bboxes[-1],
        )
    )
    print(
        "Found {} ({:.2f} %) unique images with keypoints, last annotated image is {}".format(
            len(unique_imgs_w_kpts),
            len(unique_imgs_w_kpts) / len(data["images"]) * 100,
            unique_imgs_w_kpts[-1] if len(unique_imgs_w_kpts) > 0 else None,
        )
    )
    print(
        "{:.2f} % of bboxes have keypoints".format(
            len(np.intersect1d(unique_imgs_w_bboxes, unique_imgs_w_kpts)) / len(unique_imgs_w_bboxes) * 100
        )
    )


if __name__ == "__main__":
    args = parse_args()
    main(args.annot_path)
