import datetime
import time
from collections import deque
from copy import deepcopy

import cv2
import numpy as np

from .visualization import show_bboxes


class BboxAnnotator(object):
    """
    Annotates bounding boxes on an image.

    Args:
        annotations (list): List of existing annotations.
        img_id (int): ID of the image.
        img_path (str): Path to the image file.
        window_name (str, optional): Name of the window to display the image. Defaults to "Image".
        fps (int, optional): Frames per second for displaying the image. Defaults to 20.
        is_start (bool, optional): Flag indicating if it is the start of the annotation. Defaults to True.
    """

    def __init__(
        self,
        annotations,
        img_id,
        img_path,
        window_name="Image",
        fps=20,
        is_start=True,
        click_radius_ratio=0.05,
        history_size=100,
        mark_checked_interval_seconds=3.0,
    ) -> None:
        self.started_at = time.time()

        # self.img_path = img_path
        self.img = cv2.imread(img_path)
        self.img_id = img_id

        self.annotations = deepcopy(annotations)
        self.starts = []
        self.stops = []
        for annotation in self.annotations:
            self.starts.append(annotation["bbox"][:2])
            self.stops.append(
                [
                    annotation["bbox"][0] + annotation["bbox"][2],
                    annotation["bbox"][1] + annotation["bbox"][3],
                ]
            )

        self.is_start = is_start
        self.current_keypoint = None
        self.dragging = False
        self.window_name = window_name
        self.pressed_at = 0
        self.fps = fps
        self.history_size = history_size
        self.mark_checked_interval_seconds = mark_checked_interval_seconds

        self.distance_threshold = (self.img.shape[0] + self.img.shape[1]) / 2 * click_radius_ratio

        self.memory = deque(maxlen=self.history_size)
        self.memory.append(deepcopy((self.starts, self.stops)))

        self.show()

    def mouse_callback(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.set_current_keypoint(x, y)
            self.dragging = True
            self.pressed_at = time.time()
        elif event == cv2.EVENT_LBUTTONUP:
            if self.current_keypoint is not None:
                self.memory.append(deepcopy((self.starts, self.stops)))

            self.current_keypoint = None
            self.dragging = False
            self.pressed_at = 0
            self.current_is_start = None
        elif event == cv2.EVENT_MOUSEMOVE:
            # Update the coordinates of the current keypoint
            if self.dragging and self.current_keypoint is not None:
                if self.current_is_start:
                    self.starts[self.current_keypoint] = (x, y)
                else:
                    self.stops[self.current_keypoint] = (x, y)

                if time.time() - self.pressed_at > 1 / self.fps:
                    self.pressed_at = time.time()
                    self.show()

    def key_pressed(self, k):
        # Delete the current bbox
        if k == ord("d"):
            if self.dragging and self.current_keypoint is not None:
                del self.starts[self.current_keypoint]
                del self.stops[self.current_keypoint]

                self.current_keypoint = None
                self.dragging = False
                self.pressed_at = 0
                self.current_is_start = None
                self.show()

        # Undo the last action
        elif k == ord("z"):
            self.undo()

        # Restart the annotation
        elif k == ord("r"):
            self.undo(all=True)

    def set_current_keypoint(self, x, y):
        # Check if the mouse click is within any keypoint
        if len(self.starts) > 0:
            starts = np.array(self.starts)
            dst = np.linalg.norm(starts - np.array([x, y]), axis=1)
            if np.min(dst) < self.distance_threshold:
                # Some keypoint is close enough
                self.current_keypoint = int(np.argmin(dst))
                self.current_is_start = True

            stops = np.array(self.stops)
            dst = np.linalg.norm(stops - np.array([x, y]), axis=1)
            if np.min(dst) < self.distance_threshold:
                # Some keypoint is close enough
                self.current_keypoint = int(np.argmin(dst))
                self.current_is_start = False

        if self.current_keypoint is None:
            # Create a new bbox
            self.starts.append([x, y])
            self.stops.append([x, y])
            self.current_is_start = False
            self.current_keypoint = int(len(self.starts) - 1)

    def show(self):
        img = show_bboxes(
            self.img,
            starts=self.starts,
            stops=self.stops,
        )

        # Put the text on the image
        text = "{}".format(self.img_id)

        text_color = (0, 0, 255) if self.is_start else (0, 255, 0)
        img = cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 1, cv2.LINE_AA)

        cv2.imshow(self.window_name, img)

    def undo(self, all=False):
        if len(self.memory) > 0:
            if all:
                self.starts, self.stops = self.memory[0]
                self.memory = deque(maxlen=self.history_size)
                self.memory.append(deepcopy((self.starts, self.stops)))
            else:
                self.starts, self.stops = self.memory.pop()

            self.show()

            if len(self.memory) == 0:
                self.memory.append(deepcopy((self.starts, self.stops)))

    def get_annotation(self, json_compatible=False):
        # Transfer corners to annotations
        self.annotations = []
        for start, stop in zip(self.starts, self.stops):
            start = list(start)
            stop = list(stop)
            for i in range(2):
                if start[i] > stop[i]:
                    tmp = start[i]
                    start[i] = stop[i]
                    stop[i] = tmp

            start[0] = max(0, start[0])
            start[1] = max(0, start[1])
            stop[0] = min(stop[0], self.img.shape[1])
            stop[1] = min(stop[1], self.img.shape[0])
            bbox_width = stop[0] - start[0]
            bbox_height = stop[1] - start[1]
            if (bbox_width > 1) and (bbox_height > 1):
                self.annotations.append(
                    {
                        "image_id": self.img_id,
                        "bbox": np.array([start[0], start[1], stop[0] - start[0], stop[1] - start[1]]),
                        "keypoints": np.zeros((17, 3)),
                        "category_id": 1,
                        "id": np.random.randint(low=0, high=1e6),
                    }
                )
                if (
                    self.mark_checked_interval_seconds > 0
                    and time.time() - self.started_at > self.mark_checked_interval_seconds
                ):
                    self.annotations[-1]["checked"] = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            else:
                print(f"Invalid bbox: {start}, {stop}, bbox_width: {bbox_width}, bbox_height: {bbox_height}")
                print(f"Img_id: {self.img_id}")

        if json_compatible:
            annotations = deepcopy(self.annotations)
            for annotation in annotations:
                annotation["bbox"] = annotation["bbox"].flatten().tolist()
                annotation["keypoints"] = annotation["keypoints"].flatten().tolist()
            return annotations
        else:
            return deepcopy(self.annotations)


if __name__ == "__main__":
    # Test the annotator
    img_path = "images/human_body_scheme.png"
    annotations = []
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    ia = BboxAnnotator(annotations, 0, img_path)
    cv2.setMouseCallback("Image", ia.mouse_callback)
    while True:
        k = cv2.waitKey(1)
        if k == ord("q"):
            break
        else:
            ia.key_pressed(k)
