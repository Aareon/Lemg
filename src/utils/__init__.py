from tkinter import filedialog

import cv2
import numpy as np
from PIL import Image


def open_image():
    # Load the image
    image_path = filedialog.askopenfile(
        filetypes=[("Image files", "*.jpg *.jpeg *.bmp")]
    )
    if image_path is None:
        return
    image = Image.open(image_path.name)
    return image, image_path.name


def convert_from_cv2_to_image(img: np.ndarray) -> Image:
    # return Image.fromarray(img)
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def convert_from_image_to_cv2(img: Image) -> np.ndarray:
    # return np.asarray(img)
    return cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
