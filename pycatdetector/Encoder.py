import cv2
import os
import PIL
import numpy as np


class Encoder:
    video_file = None
    video_writer = None
    opened = False

    def __init__(self, video_file):
        self.video_file = video_file

    def open(self, frame: np.ndarray):
        height, width, layers = frame.shape
        self.video_writer = \
            cv2.VideoWriter(self.video_file, 0, 1, (width, height))
        self.opened = True

    def add_image(self, image):
        if isinstance(image, PIL.Image.Image):
            frame = np.array(image)
        elif isinstance(image, np.ndarray):
            frame = image
        else:
            raise ValueError("Invalid sample_image type" + str(type(image)))
        if not self.opened:
            self.open(frame)
        self.video_writer.write(frame)

    def load_image(self, file) -> np.ndarray:
        return cv2.imread(file)

    def add_file(self, file):
        self.add_image(self.load_image(file))

    def add_folder(self, folder, extension=".png"):
        images = \
            [img for img in os.listdir(folder) if img.endswith(extension)]
        for image in images:
            self.add_file(os.path.join(folder, image))

    def close(self):
        if self.opened:
            self.video_writer.release()
            self.opened = False
        cv2.destroyAllWindows()  # safe to call even if no windows are created
