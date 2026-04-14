import datetime
import time
from collections import deque
from copy import deepcopy

import cv2
import numpy as np

from .visualization import show_annotation


class InteractiveAnnotator(object):
    def __init__(
        self,
        annotation,
        img_path,
        window_name="Image",
        fps=20,
        with_example=True,
        is_start=True,
        two_scales=False,
        inf_size=None,
        normalize_shape=True,
        pose_format="coco",
    ) -> None:
        """
        Initializes an instance of the InteractiveAnnotator class.

        Parameters:
        - annotation: A dictionary containing the annotation information.
        - img_path: The path to the image file.
        - window_name: The name of the window to display the image.
        - fps: The frames per second for displaying the image.
        - with_example: A boolean indicating whether to show an example image.
        - is_start: A boolean indicating whether it is the start of the annotation.
        - two_scales: A boolean indicating whether to use two scales for annotation.
        - inf_size: The size of the inference image.
        - normalize_shape: A boolean indicating whether to normalize the shape of the annotation.
        - pose_format: The format of the pose annotation.
        """
        self.started_at = time.time()

        self.img = cv2.imread(img_path)

        if annotation is None:
            self.annotation = {
                "keypoints": np.zeros((17, 3)),
                "bbox": [0, 0, self.img.shape[1], self.img.shape[0]],
                "image_id": 0,
                "category_id": 1,
                "id": 0,
            }
            self.bbox_pad = 0.0 + 7 * 0.05
        else:
            self.annotation = deepcopy(annotation)

            if "keypoints" not in self.annotation.keys():
                self.annotation["keypoints"] = np.zeros((17, 3))

            if "area" not in self.annotation.keys():
                self.annotation["area"] = self.annotation["bbox"][2] * self.annotation["bbox"][3]

            self.annotation["keypoints"] = np.array(self.annotation["keypoints"]).reshape(-1, 3)
            self.bbox_pad = 0.0 + 7 * 0.05

        self.inf_size = inf_size
        self.preset_inf_size = inf_size
        self.is_start = is_start
        self.two_scales = two_scales
        self.pose_format = pose_format.lower()
        self.current_keypoint = None
        self.dragging = False
        self.window_name = window_name
        self.pressed_at = 0
        self.fps = fps

        self.implemented_formats = ["coco", "coco_with_thumbs"]
        assert (
            self.pose_format in self.implemented_formats
        ), "Format {:s} not implemented. Use one of the following: {}".format(
            self.pose_format, self.implemented_formats
        )

        self.normalize_shape = normalize_shape
        self.x_transform = lambda x: x
        self.y_transform = lambda x: x

        # If WITH HAND, the annotation should have 21 keypoints
        if self.pose_format == "coco_with_thumbs" and self.annotation["keypoints"].shape[0] != 21:
            missing_kpts = 21 - self.annotation["keypoints"].shape[0]
            self.annotation["keypoints"] = np.vstack(
                (self.annotation["keypoints"], np.zeros((missing_kpts, 3)))
            )

        self.distance_threshold = (
            (self.annotation["bbox"][2] + self.annotation["bbox"][3]) / 2 * 0.05
        )

        self.memory = deque(maxlen=100)
        self.memory.append(deepcopy(self.annotation))

        self.with_example = with_example
        if self.with_example:
            self.example_img = cv2.imread("example_images/{:s}.png".format(self.pose_format))
        self.show()

    def mouse_callback(self, event, x, y, flags, params):
        old_x, old_y = x, y
        x = self.x_transform(x)
        y = self.y_transform(y)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.set_current_keypoint(x, y)
            self.dragging = True
            self.pressed_at = time.time()
        elif event == cv2.EVENT_LBUTTONUP:
            if self.current_keypoint is not None:
                self.memory.append(deepcopy(self.annotation))

            self.current_keypoint = None
            self.dragging = False
            self.pressed_at = 0
        elif event == cv2.EVENT_MOUSEMOVE:
            # Update the coordinates of the current keypoint
            if self.dragging and self.current_keypoint is not None:
                # Offset the coordinates of the keypoint by the scale of the image
                if x < self.x_divider:
                    self.annotation["keypoints"][self.current_keypoint, :2] = (
                        x + self.x_offsets[0],
                        y + self.y_offsets[0],
                    )
                else:
                    self.annotation["keypoints"][self.current_keypoint, :2] = (
                        (x - self.x_divider) / self.x_offsets[1] * self.annotation["bbox"][2]
                        + self.annotation["bbox"][0],
                        (y) / self.y_offsets[1] * self.annotation["bbox"][3]
                        + self.annotation["bbox"][1],
                    )

                if time.time() - self.pressed_at > 1 / self.fps:
                    self.pressed_at = time.time()
                    self.show()

    def key_pressed(self, k):
        # Change the visibility of the current keypoint
        if k == ord("v"):
            if self.dragging and self.current_keypoint is not None:
                v = self.annotation["keypoints"][self.current_keypoint, 2]
                if v == 1:
                    self.annotation["keypoints"][self.current_keypoint, 2] = 2
                elif v == 2:
                    self.annotation["keypoints"][self.current_keypoint, 2] = 3
                elif v == 3:
                    self.annotation["keypoints"][self.current_keypoint, 2] = 1
                self.show()

        # Delete the current keypoint
        elif k == ord("d"):
            if self.dragging and self.current_keypoint is not None:
                self.annotation["keypoints"][self.current_keypoint, :] = 0

                self.current_keypoint = None
                self.show()

        # Undo the last action
        elif k == ord("z"):
            self.undo()

        # Restart the annotation
        elif k == ord("r"):
            self.undo(all=True)

        # Generate a completely new annotation
        elif k == ord("g"):
            self.generate()

        # Generate a completely new annotation
        elif k == ord("l"):
            self.flip_lr()

        # Add a new keypoint, if some is missing
        elif k == ord("a"):
            self.add_keypoint()

        # Clear
        elif k == ord("c"):
            self.add_keypoint()

        # Zoom the image
        elif k == ord("o"):
            self.bbox_pad += 0.05
            if abs(self.bbox_pad) < 1e-5:
                self.inf_size = self.preset_inf_size
            else:
                self.inf_size = None
            self.show()

            # Detect max zoom and if so, do not expand the bbox anymore
            if (
                self.x_offsets[0] == 0
                and self.x_offsets[1] == self.img.shape[1]
                and self.y_offsets[0] == 0
                and self.y_offsets[1] == self.img.shape[0]
            ):
                self.bbox_pad -= 0.05

        elif k == ord("p"):
            self.bbox_pad -= 0.05
            self.bbox_pad = max(self.bbox_pad, -0.45)
            if abs(self.bbox_pad) < 1e-5:
                self.inf_size = self.preset_inf_size
            else:
                self.inf_size = None
            self.show()

        elif k == ord("e"):
            mask_vis_kpts = self.annotation["keypoints"][:, 2] == 2
            mask_unvis_kpts = self.annotation["keypoints"][:, 2] == 1
            self.annotation["keypoints"][mask_vis_kpts, 2] = 1
            self.annotation["keypoints"][mask_unvis_kpts, 2] = 2
            self.show()

        # if k > -1:
        #     print(k, self.annotation)

    def set_current_keypoint(self, x, y):
        # Check if the mouse click is within any keypoint
        idxs, kpts = self.kpts_mapping
        dst = np.linalg.norm(kpts - np.array([x, y]), axis=1)
        # print(kpts)
        # print(dst)
        if np.min(dst) < self.distance_threshold:
            self.current_keypoint = idxs[np.argmin(dst)]

    def show(self):
        img, bbox_with_pad, kpts_mapping = show_annotation(
            self.img,
            annotation=self.annotation,
            pad=self.bbox_pad * 2 if self.two_scales else self.bbox_pad,
            two_scales=self.two_scales,
            inf_size=self.inf_size,
        )

        self.kpts_mapping = kpts_mapping
        self.x_divider = bbox_with_pad[2]
        self.x_offsets = (bbox_with_pad[0], bbox_with_pad[2])
        self.y_offsets = (bbox_with_pad[1], bbox_with_pad[3])

        # Stitch example next to the image
        if self.with_example:
            # Resite the example image
            if self.example_img.shape[0] != img.shape[0]:
                ratio = img.shape[0] / self.example_img.shape[0]
                self.example_img = cv2.resize(
                    self.example_img, (int(ratio * self.example_img.shape[1]), img.shape[0])
                )

            img = np.hstack((img, self.example_img))

        # Put the text on the image
        text = "{}-{:d}".format(self.annotation["image_id"], self.annotation["id"])
        text_color = (0, 0, 255) if self.is_start else (0, 0, 0)

        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)[0]

        img = cv2.putText(
            img,
            text,
            (img.shape[1] - text_size[0] - 5, text_size[1] + 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            text_color,
            1,
            cv2.LINE_AA,
        )

        self.normalize_shape = False
        if self.normalize_shape:
            coef = 192 / 256
            self.y_transform = lambda x: x * 1
            self.x_transform = lambda x: x * 1
            if img.shape[0] > img.shape[1]:
                print("Resizing x-axis")
                dst_size = [int(img.shape[0] / coef), img.shape[0]]
                self.x_transform = lambda x: x / coef
            else:
                print("Resizing y-axis")
                self.y_transform = lambda x: x / coef
                dst_size = [img.shape[1], int(img.shape[1] * coef)]
            print(img.shape[:2], dst_size[:2])
            img = cv2.resize(img, dst_size)
            print(img.shape[:2], img.shape[0] / img.shape[1], coef)

        cv2.imshow(self.window_name, img)

    def undo(self, all=False):
        if len(self.memory) > 0:
            if all:
                self.annotation = self.memory[0]
                self.memory = deque(maxlen=100)
                self.memory.append(deepcopy(self.annotation))
            else:
                self.annotation = self.memory.pop()

            self.show()

            if len(self.memory) == 0:
                self.memory.append(deepcopy(self.annotation))

    def generate(self):
        if self.pose_format == "coco":
            self.annotation["keypoints"] = np.zeros((17, 3), dtype=float)
        elif self.pose_format == "coco_with_thumbs":
            self.annotation["keypoints"] = np.zeros((21, 3), dtype=float)

        self.annotation["keypoints"][:, 2] = 2
        self.annotation["keypoints"][:17, :2] = [
            [0.50, 0.15],  # Nose
            [0.55, 0.10],  # Left eye
            [0.45, 0.10],  # Right eye
            [0.65, 0.10],  # Left ear
            [0.35, 0.10],  # Right ear
            [0.73, 0.30],  # Left shoulder
            [0.27, 0.30],  # Right shoulder
            [0.86, 0.43],  # Left elbow
            [0.14, 0.43],  # Right elbow
            [0.96, 0.56],  # Left wrist
            [0.04, 0.56],  # Right wrist
            [0.73, 0.65],  # Left hip
            [0.27, 0.65],  # Right hip
            [0.73, 0.79],  # Left knee
            [0.27, 0.79],  # Right knee
            [0.73, 0.93],  # Left ankle
            [0.27, 0.93],  # Right ankle
        ]
        if self.pose_format == "coco_with_thumbs":
            self.annotation["keypoints"][17:, :2] = [
                [0.92, 0.60],  # Left thumb
                [0.08, 0.60],  # Right index
                [0.98, 0.60],  # Left index
                [0.02, 0.60],  # Right index
            ]
        self.annotation["keypoints"][:, 0] *= self.annotation["bbox"][2]
        self.annotation["keypoints"][:, 1] *= self.annotation["bbox"][3]
        self.annotation["keypoints"][:, 0] += self.annotation["bbox"][0]
        self.annotation["keypoints"][:, 1] += self.annotation["bbox"][1]

        self.memory.append(deepcopy(self.annotation))
        self.show()

    def flip_lr(self):
        if self.pose_format == "coco_with_thumbs":
            self.annotation["keypoints"] = self.annotation["keypoints"][
                [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15, 18, 17, 20, 19], :
            ]
        else:
            self.annotation["keypoints"] = self.annotation["keypoints"][
                [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15], :
            ]
        self.memory.append(deepcopy(self.annotation))
        self.show()

    def get_annotation(self, json_compatible=False):
        if time.time() - self.started_at > 3:
            self.annotation["checked"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        if json_compatible:
            annotation = deepcopy(self.annotation)
            annotation["keypoints"] = annotation["keypoints"].flatten().tolist()
            # print(annotation)
            return annotation
        else:
            return deepcopy(self.annotation)

    def add_keypoint(self):
        for kpt in self.annotation["keypoints"]:
            if (kpt[0] == 0 and kpt[1] == 0) and (kpt[2] == 0):
                kpt[0] = np.random.rand() * self.annotation["bbox"][2] + self.annotation["bbox"][0]
                kpt[1] = np.random.rand() * self.annotation["bbox"][3] + self.annotation["bbox"][1]
                kpt[2] = 2
                self.show()
                break


if __name__ == "__main__":
    # Test the annotator
    img_path = "images/human_body_scheme.png"
    annotation = None
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    ia = InteractiveAnnotator(annotation, img_path, with_example=False)
    cv2.setMouseCallback("Image", ia.mouse_callback)
    while True:
        k = cv2.waitKey(1)
        if k == ord("q"):
            print(ia.get_annotation(json_compatible=True))
            break
        else:
            ia.key_pressed(k)
