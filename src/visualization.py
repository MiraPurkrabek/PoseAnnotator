from copy import deepcopy

import cv2
import numpy as np

NEUTRAL_COLOR = (52, 235, 107)

LEFT_ARM_COLOR = (216, 235, 52, 255)
LEFT_LEG_COLOR = (235, 107, 52, 255)
LEFT_SIDE_COLOR = (245, 188, 113, 255)
LEFT_FACE_COLOR = (235, 52, 107, 255)

RIGHT_ARM_COLOR = (52, 235, 216, 255)
RIGHT_LEG_COLOR = (52, 107, 235, 255)
RIGHT_SIDE_COLOR = (52, 171, 235, 255)
RIGHT_FACE_COLOR = (107, 52, 235, 255)

COCO_MARKERS = [
    ["nose", cv2.MARKER_CROSS, NEUTRAL_COLOR],
    ["left_eye", cv2.MARKER_SQUARE, LEFT_FACE_COLOR],
    ["right_eye", cv2.MARKER_SQUARE, RIGHT_FACE_COLOR],
    ["left_ear", cv2.MARKER_CROSS, LEFT_FACE_COLOR],
    ["right_ear", cv2.MARKER_CROSS, RIGHT_FACE_COLOR],
    ["left_shoulder", cv2.MARKER_TRIANGLE_UP, LEFT_ARM_COLOR],
    ["right_shoulder", cv2.MARKER_TRIANGLE_UP, RIGHT_ARM_COLOR],
    ["left_elbow", cv2.MARKER_SQUARE, LEFT_ARM_COLOR],
    ["right_elbow", cv2.MARKER_SQUARE, RIGHT_ARM_COLOR],
    ["left_wrist", cv2.MARKER_TILTED_CROSS, LEFT_ARM_COLOR],
    ["right_wrist", cv2.MARKER_TILTED_CROSS, RIGHT_ARM_COLOR],
    ["left_hip", cv2.MARKER_TRIANGLE_UP, LEFT_LEG_COLOR],
    ["right_hip", cv2.MARKER_TRIANGLE_UP, RIGHT_LEG_COLOR],
    ["left_knee", cv2.MARKER_SQUARE, LEFT_LEG_COLOR],
    ["right_knee", cv2.MARKER_SQUARE, RIGHT_LEG_COLOR],
    ["left_ankle", cv2.MARKER_TILTED_CROSS, LEFT_LEG_COLOR],
    ["right_ankle", cv2.MARKER_TILTED_CROSS, RIGHT_LEG_COLOR],
]

COCO_MARKERS_WITH_HANDS = COCO_MARKERS + [
    ["left_thumb", cv2.MARKER_DIAMOND, LEFT_ARM_COLOR],
    ["right_thumb", cv2.MARKER_DIAMOND, RIGHT_ARM_COLOR],
    ["left_index", cv2.MARKER_CROSS, LEFT_ARM_COLOR],
    ["right_index", cv2.MARKER_CROSS, RIGHT_ARM_COLOR],
]

COCO_SKELETON = [
    [[16, 14], LEFT_LEG_COLOR],  # Left ankle - Left knee
    [[14, 12], LEFT_LEG_COLOR],  # Left knee - Left hip
    [[17, 15], RIGHT_LEG_COLOR],  # Right ankle - Right knee
    [[15, 13], RIGHT_LEG_COLOR],  # Right knee - Right hip
    [[12, 13], NEUTRAL_COLOR],  # Left hip - Right hip
    [[6, 12], LEFT_SIDE_COLOR],  # Left hip - Left shoulder
    [[7, 13], RIGHT_SIDE_COLOR],  # Right hip - Right shoulder
    [[6, 7], NEUTRAL_COLOR],  # Left shoulder - Right shoulder
    [[6, 8], LEFT_ARM_COLOR],  # Left shoulder - Left elbow
    [[7, 9], RIGHT_ARM_COLOR],  # Right shoulder - Right elbow
    [[8, 10], LEFT_ARM_COLOR],  # Left elbow - Left wrist
    [[9, 11], RIGHT_ARM_COLOR],  # Right elbow - Right wrist
    [[2, 3], NEUTRAL_COLOR],  # Left eye - Right eye
    [[1, 2], LEFT_FACE_COLOR],  # Nose - Left eye
    [[1, 3], RIGHT_FACE_COLOR],  # Nose - Right eye
    [[2, 4], LEFT_FACE_COLOR],  # Left eye - Left ear
    [[3, 5], RIGHT_FACE_COLOR],  # Right eye - Right ear
    [[4, 6], LEFT_FACE_COLOR],  # Left ear - Left shoulder
    [[5, 7], RIGHT_FACE_COLOR],  # Right ear - Right shoulder
]

COCO_SKELETON_WITH_HANDS = COCO_SKELETON + [
    [[10, 18], LEFT_ARM_COLOR],  # Left wrist - Left thumb
    [[11, 19], RIGHT_ARM_COLOR],  # Right wrist - Right thumb
    [[10, 20], LEFT_ARM_COLOR],  # Left wrist - Left index
    [[11, 21], RIGHT_ARM_COLOR],  # Right wrist - Right index
]


def cut_bbox(img, bbox_wh, color=(0, 255, 0), thickness=2, pad=0.2, show_bbox=True, inf_size=None):
    """
    This function draws bounding box on the image
    """
    if isinstance(img, str):
        img = cv2.imread(img)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    else:
        img = img.copy()

    bbox_wh = np.array(bbox_wh).astype(int)

    # bbox_wh[0] -= pad * bbox_wh[2]
    # bbox_wh[1] -= pad * bbox_wh[3]
    # bbox_wh[2] *= (1+2*pad)
    # bbox_wh[3] *= (1+2*pad)
    # start_pt = (bbox_wh[0], bbox_wh[1])
    # end_pt = (bbox_wh[0]+bbox_wh[2], bbox_wh[1]+bbox_wh[3])

    if show_bbox:
        img = cv2.rectangle(
            img,
            (bbox_wh[0], bbox_wh[1]),
            (bbox_wh[0] + bbox_wh[2], bbox_wh[1] + bbox_wh[3]),
            color=color,
            thickness=thickness,
        )

        # Draw corners of the bbox as circles
        img = cv2.circle(img, (bbox_wh[0], bbox_wh[1]), 5, color, -1)
        img = cv2.circle(img, (bbox_wh[0] + bbox_wh[2], bbox_wh[1]), 5, color, -1)
        img = cv2.circle(img, (bbox_wh[0], bbox_wh[1] + bbox_wh[3]), 5, color, -1)
        img = cv2.circle(img, (bbox_wh[0] + bbox_wh[2], bbox_wh[1] + bbox_wh[3]), 5, color, -1)

    original_bbox_wh = deepcopy(bbox_wh)

    # Enlarge the bbox with the padding
    bbox_wh[0] -= pad * bbox_wh[2]
    bbox_wh[1] -= pad * bbox_wh[3]
    bbox_wh[2] *= 1 + 2 * pad
    bbox_wh[3] *= 1 + 2 * pad

    # Make sure the bbox is within the image
    bbox_wh[0] = max(bbox_wh[0], 0)
    bbox_wh[1] = max(bbox_wh[1], 0)
    bbox_wh[2] = min(bbox_wh[2], img.shape[1] - bbox_wh[0])
    bbox_wh[3] = min(bbox_wh[3], img.shape[0] - bbox_wh[1])

    # Cut the image
    start_pt = (bbox_wh[0], bbox_wh[1])
    end_pt = (bbox_wh[0] + bbox_wh[2], bbox_wh[1] + bbox_wh[3])
    img = img[start_pt[1] : end_pt[1], start_pt[0] : end_pt[0]]

    # If inf_size is given, pad bbox with zeros
    if not inf_size is None:
        # Pad with grey
        grey_pad_size = (inf_size * original_bbox_wh[2:]).astype(int)
        img = np.pad(
            img,
            pad_width=(
                (grey_pad_size[1], grey_pad_size[1]),
                (grey_pad_size[0], grey_pad_size[0]),
                (0, 0),
            ),
            mode="constant",
            constant_values=200,
        )

        # Pad with black
        black_pad_size = np.array([0, 0])  # grey_pad_size//5
        img = np.pad(
            img,
            pad_width=(
                (black_pad_size[1], black_pad_size[1]),
                (black_pad_size[0], black_pad_size[0]),
                (0, 0),
            ),
            mode="constant",
            constant_values=0,
        )

        # Draw octants
        # offset = grey_pad_size + black_pad_size
        # zero = 0
        # pts = [
        #     [(offset, zero), (offset, offset)],
        #     [(offset, img.shape[0]-zero), (offset, img.shape[0]-offset)],
        #     [(zero, img.shape[0]-offset), (offset, img.shape[0]-offset)],
        #     [(zero, offset), (offset, offset)],
        #     [(img.shape[1]-zero, offset), (img.shape[1]-offset, offset)],
        #     [(img.shape[1]-zero, img.shape[0]-offset), (img.shape[1]-offset, img.shape[0]-offset)],
        #     [(img.shape[1]-offset, img.shape[0]-zero), (img.shape[1]-offset, img.shape[0]-offset)],
        #     [(img.shape[1]-offset, zero), (img.shape[1]-offset, offset)],
        # ]
        # for pt in pts:
        #     img = cv2.line(
        #         img, pt[0], pt[1], color=(0, 255, 0), thickness=max(grey_pad_size//50, 1),
        #     )

        # Visualize infinite space - first line is in the middle of the inf_pad,
        # second line is at 3/4 of the inf_pad, third line is at 7/8 of the inf_pad ...
        thickness = 1 if np.max(img.shape) < 1000 else 2
        start_pt = grey_pad_size
        for _ in range(1, 5):
            start_pt = start_pt // 2
            end_pt = np.array([img.shape[1], img.shape[0]]) - start_pt
            # Draw dar grey rectangle
            img = cv2.rectangle(
                img,
                start_pt.astype(int),
                end_pt.astype(int),
                color=(120, 120, 120),
                thickness=thickness,
            )

        # Draw red cross across the image
        img = cv2.line(
            img,
            (grey_pad_size[0], img.shape[0] // 2),
            (img.shape[1] - grey_pad_size[0], img.shape[0] // 2),
            # color=(0, 0, 255),
            color=(120, 120, 120),
            thickness=thickness,
        )
        img = cv2.line(
            img,
            (img.shape[1] // 2, grey_pad_size[1]),
            (img.shape[1] // 2, img.shape[0] - grey_pad_size[1]),
            # color=(0, 0, 255),
            color=(120, 120, 120),
            thickness=thickness,
        )

        # Get the numbers right so that the keypoints are still correct
        bbox_wh[0] -= grey_pad_size[0]
        bbox_wh[1] -= grey_pad_size[1]
        bbox_wh[2] += 2 * grey_pad_size[0]
        bbox_wh[3] += 2 * grey_pad_size[1]

        bbox_wh[0] -= black_pad_size[0]
        bbox_wh[1] -= black_pad_size[1]
        bbox_wh[2] += 2 * black_pad_size[0]
        bbox_wh[3] += 2 * black_pad_size[1]

    return img, bbox_wh


def show_keypoints(img, keypoints):
    """
    This function draws keypoints on the image
    """
    if isinstance(img, str):
        img = cv2.imread(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    keypoints = np.array(keypoints).astype(int).reshape(-1, 3)

    valid_kpts = np.all(keypoints[:, :2] > 0, axis=1)

    # No keypoints to draw
    if np.sum(valid_kpts) == 0:
        return img

    min_x = np.min(keypoints[valid_kpts, 0])
    min_y = np.min(keypoints[valid_kpts, 1])
    max_x = np.max(keypoints[valid_kpts, 0])
    max_y = np.max(keypoints[valid_kpts, 1])

    max_area = (max_x - min_x) * (max_y - min_y)
    line_width = max(int(np.sqrt(max_area) / 500), 1)
    marker_size = max(int(np.sqrt(max_area) / 30), 1)
    invisible_marker_size = max(int(np.sqrt(max_area) / 50), 1)
    marker_thickness = max(int(np.sqrt(max_area) / 100), 1)

    if len(keypoints) == len(COCO_MARKERS):
        coco_markers = COCO_MARKERS
        coco_skeleton = COCO_SKELETON
    else:
        coco_markers = COCO_MARKERS_WITH_HANDS
        coco_skeleton = COCO_SKELETON_WITH_HANDS

    for kpt, marker_info in zip(keypoints, coco_markers):
        # Do not show deleted keypoints
        if kpt[2] <= 0:
            continue

        # Do not show estimated keypoints, show only its bones
        if kpt[2] > 2:
            continue

        if kpt[2] == 2:
            color = marker_info[2]
        else:
            color = (150, 150, 150, 0)

        if kpt[2] == 2:
            img = cv2.drawMarker(
                img,
                (int(kpt[0]), int(kpt[1])),
                color=color,
                markerType=marker_info[1],
                markerSize=invisible_marker_size if kpt[2] == 1 else marker_size,
                thickness=marker_thickness,
            )

        else:
            img_overlay = img.copy()
            img_overlay = cv2.drawMarker(
                img_overlay,
                (int(kpt[0]), int(kpt[1])),
                color=color,
                markerType=marker_info[1],
                markerSize=marker_size,
                thickness=marker_thickness,
            )
            img = cv2.addWeighted(img_overlay, 0.7, img, 0.3, 0)

    for bone_info in coco_skeleton:
        kp1 = keypoints[bone_info[0][0] - 1, :]
        kp2 = keypoints[bone_info[0][1] - 1, :]

        # if (kp1[0] == 0 and kp1[1] == 0) or (kp2[0] == 0 and kp2[1] == 0):
        if (kp1[2] == 0) or (kp2[2] == 0):
            continue

        dashed = kp1[2] != 2 or kp2[2] != 2
        color = bone_info[1]

        if dashed:
            img_overlay = img.copy()
            img_overlay = cv2.line(
                img_overlay,
                (int(kp1[0]), int(kp1[1])),
                (int(kp2[0]), int(kp2[1])),
                color,
                thickness=line_width,
                lineType=cv2.LINE_AA,
            )
            img = cv2.addWeighted(img_overlay, 0.4, img, 0.6, 0)

        else:
            img = cv2.line(
                img,
                (int(kp1[0]), int(kp1[1])),
                (int(kp2[0]), int(kp2[1])),
                color,
                thickness=line_width,
                lineType=cv2.LINE_AA,
            )

    return img


def show_annotation(img, annotation, pad=0.2, two_scales=True, inf_size=None):
    """
    This function draws keypoints and bounding box on the image
    """

    assert not (two_scales and not inf_size is None), "Cannot use two_scales and inf_size at the same time"

    if isinstance(img, str):
        print("Loading image")
        img = cv2.imread(img)
    else:
        img = img.copy()

    annotation = deepcopy(annotation)
    img_cut, bbox_with_pad = cut_bbox(
        img,
        annotation["bbox"],
        pad=pad,
        color=(0, 120, 0) if "checked" in annotation.keys() else (0, 255, 0),
        inf_size=inf_size,
    )
    vis_kpts = annotation["keypoints"][:, 2] > 0
    annotation["keypoints"][vis_kpts, :2] -= bbox_with_pad[:2]
    img_cut = show_keypoints(
        img_cut,
        annotation["keypoints"],
    )

    # Create a mapping from image coordinates to keypoint index
    kpts_mapping = [
        np.array(list(range(len(annotation["keypoints"])))),
        annotation["keypoints"][:, :2],
    ]

    if two_scales:
        img_cut2, _ = cut_bbox(
            img,
            annotation["bbox"],
            pad=0,
            color=(0, 120, 0) if "checked" in annotation.keys() else (0, 255, 0),
            show_bbox=False,
        )
        resize_factor = img_cut2.shape[0] / img_cut.shape[0]
        resize_factor = 1 / resize_factor
        img_cut2 = cv2.resize(img_cut2, (img_cut.shape[1], img_cut.shape[0]))
        img_cut = np.hstack((img_cut, img_cut2))

        kpts_mapping[0] = np.concatenate((kpts_mapping[0], kpts_mapping[0]), axis=0)

        kpts_mapping[1] = np.concatenate(
            (
                kpts_mapping[1],
                (annotation["keypoints"][:, :2] - annotation["bbox"][:2]) * resize_factor
                + np.array([bbox_with_pad[2], 0]),
            ),
            axis=0,
        )

    kpts_mapping[1][kpts_mapping[1] < 0] = 0

    return img_cut, bbox_with_pad, kpts_mapping


def show_bboxes(img, starts, stops):
    if isinstance(img, str):
        print("Loading image")
        img = cv2.imread(img)
    else:
        img = img.copy()

    for start, stop in zip(starts, stops):
        img = cv2.rectangle(
            img,
            (int(start[0]), int(start[1])),
            (int(stop[0]), int(stop[1])),
            color=(0, 255, 0),
            thickness=2,
        )
        img = cv2.circle(
            img,
            (int(start[0]), int(start[1])),
            radius=5,
            color=(0, 0, 255),
            thickness=-1,
        )
        img = cv2.circle(
            img,
            (int(stop[0]), int(stop[1])),
            radius=5,
            color=(0, 0, 255),
            thickness=-1,
        )
    return img
