# Description: Merge two annotation files in COCO format.
# Usage: python merge_annot.py <file1> <file2> <output_file>

import argparse
import json

import numpy as np


def merge_annotations(file1, file2, output_file):
    visibility_match = 0

    with open(file1, "r") as f1, open(file2, "r") as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    # Check if annotation IDs and image IDs are the same
    annotation_ids1 = set([ann["id"] for ann in data1["annotations"]])
    annotation_ids2 = set([ann["id"] for ann in data2["annotations"]])
    image_ids1 = set([img["id"] for img in data1["images"]])
    image_ids2 = set([img["id"] for img in data2["images"]])

    if annotation_ids1 != annotation_ids2 or image_ids1 != image_ids2:
        print("Error: Annotation IDs or image IDs are not the same in the two files.")
        return

    anns1 = {ann["id"]: ann for ann in data1["annotations"]}
    anns2 = {ann["id"]: ann for ann in data2["annotations"]}

    merged_anns = []
    stds_all = []
    for ann_id in annotation_ids1:
        ann1 = anns1[ann_id]
        ann2 = anns2[ann_id]

        # Merge annotations
        kpts1 = np.array(ann1["keypoints"]).reshape(-1, 3)
        kpts2 = np.array(ann2["keypoints"]).reshape(-1, 3)
        kpts = np.zeros((kpts1.shape[0], 3))
        stds = np.zeros((kpts1.shape[0], 2))
        for j in range(kpts1.shape[0]):
            v1 = kpts1[j, 2]
            v2 = kpts2[j, 2]
            visibility_match += int(v1 == v2)
            vs = np.array([v1, v2])
            xs = np.array([kpts1[j, 0], kpts2[j, 0]])
            ys = np.array([kpts1[j, 1], kpts2[j, 1]])
            if v1 == v2:
                stds[j, :] = [xs[0] - xs[1], ys[0] - ys[1]]
            if v1 == 0 and v2 == 0:
                # Both 0
                v = 0
                xs = [0, 0]
                ys = [0, 0]
                stds[j, :] = [0, 0]
            elif v1 == 2 or v2 == 2:
                # One is 2
                v = 2
                xs = xs[vs == 2]
                ys = ys[vs == 2]
            elif v1 > 0 and v2 > 0:
                # Both > 0 --> Either 1 or 3
                v = min(v1, v2)
                xs = xs[vs == v]
                ys = ys[vs == v]
            else:
                # One is 0 and the other is > 1 or 3
                v = max(v1, v2)
                xs = xs[vs == v]
                ys = ys[vs == v]
            kpts[j, :] = [np.mean(xs), np.mean(ys), v]
        num_kpts = np.sum(kpts[:, 2] > 0)
        stds = np.sqrt(np.sum(stds**2, axis=1))
        stds_all.append(stds / ann1["area"] ** 0.5)

        merged_ann = {
            "id": ann_id,
            "image_id": ann1["image_id"],
            "category_id": ann1["category_id"],
            "area": ann1["area"],
            "bbox": ann1["bbox"],
            "iscrowd": ann1["iscrowd"],
            "keypoints": kpts.flatten().tolist(),
            "num_keypoints": int(num_kpts),
        }
        if "segmentation" in ann1.keys():
            merged_ann["segmentation"] = ann1["segmentation"]
        merged_anns.append(merged_ann)
    stds_all = np.array(stds_all)

    print("Keypoints visibility match: {:.2f} %".format(visibility_match / (len(merged_anns) * 17) * 100))

    sigmas = stds_all.std(axis=0)
    coco_sigmas = np.array(
        [
            0.0260,
            0.0250,
            0.0250,
            0.0350,
            0.0350,
            0.0790,
            0.0790,
            0.0720,
            0.0720,
            0.0620,
            0.0620,
            0.1070,
            0.1070,
            0.0870,
            0.0870,
            0.0890,
            0.0890,
        ]
    )
    np.set_printoptions(formatter={"float": "{: 0.3f}".format})
    print("Sigmas for different keypoints: {}".format(sigmas))
    print("Sigmas in the COCO dataset    : {}".format(coco_sigmas))
    # breakpoint()

    # Merge annotations
    merged_data = {
        "info": data1["info"],
        "licenses": data1["licenses"],
        "images": data1["images"],
        "annotations": merged_anns,
        "categories": data1["categories"],
    }

    # Save merged data to output file
    with open(output_file, "w") as f:
        json.dump(merged_data, f, indent=2)

    print("Annotations merged successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge annotations in COCO format.")
    parser.add_argument("file1", help="Path to the first annotation file")
    parser.add_argument("file2", help="Path to the second annotation file")
    parser.add_argument("output_file", help="Path to the output merged annotation file")

    args = parser.parse_args()

    merge_annotations(args.file1, args.file2, args.output_file)
