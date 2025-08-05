import PIL.Image
import cv2
import os
import PIL
import numpy as np


class Encoder:
    """
    Class that provides functionality to encode images into a video file.

    Attributes:

    - video_file (str): The path to the output video file.
    - video_writer: The video writer object from OpenCV.
    """

    def __init__(self, video_file):
        """
        Initializes the Encoder object with the specified video file path.

        Args:
        - video_file (str): The path to the output video file.
        """
        self.video_file = video_file
        self.video_writer = None

    def open(self, height: int, width: int) -> cv2.VideoWriter:
        """

        Opens the video writer with the dimensions of the input frame.

        Args:
        - frame (np.ndarray): The input frame to determine video dimensions.

        Raises:
        - ValueError: If the frame is not a valid numpy array.
        """
        return cv2.VideoWriter(self.video_file, 0, 1, (width, height))

    def add_image(self, image: PIL.Image.Image | np.ndarray):
        """
        Adds an image to the video file.

        Args:
        - image: The image to be added.

        Raises:
        - ValueError: If the image is not a valid PIL Image or numpy array.
        """
        if isinstance(image, PIL.Image.Image):
            frame = np.array(image)
        elif isinstance(image, np.ndarray):
            frame = image
        else:
            raise ValueError("Invalid image type: " + str(type(image)))

        if self.video_writer is None:
            height, width, _ = frame.shape
            self.video_writer = self.open(height, width)

        self.video_writer.write(frame)

    def load_image(self, filename: str) -> np.ndarray:
        """
        Loads an image from a file.

        Args:
        - file (str): The path to the image file.


        Returns:
        - np.ndarray: The loaded image as a numpy array.
        """
        image = cv2.imread(filename=filename)
        if image is None:
            raise FileNotFoundError(f"Could not load image from {filename}")
        return image

    def add_file(self, filename: str):
        """
        Adds an image file to the video file.

        Args:
        - filename (str): The path to the image file.
        """
        self.add_image(self.load_image(filename))

    def add_folder(self, folder, extension=".png"):
        """
        Adds all images in a folder to the video file.

        Args:
        - folder (str): The path to the folder containing the images.
        - extension (str): The file extension of the images to be added.
                           Defaults to ".png".
        """
        images = [img for img in os.listdir(folder) if img.endswith(extension)]
        for image in images:
            self.add_file(os.path.join(folder, image))

    def close(self):
        """
        Closes the video writer and releases resources.
        """
        if self.video_writer:
            self.video_writer.release()
            self.video_opened = False
