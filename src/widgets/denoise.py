import tkinter as tk

import cv2
from PIL import Image

from utils import convert_from_image_to_cv2
from widgets import ImageCompareWidget


def get_denoise(
    image: Image,
    strength: int,
    colored_strength: int,
    templateWindowSize: int,
    searchWindowSize: int,
):
    denoised_image = cv2.fastNlMeansDenoisingColored(
        convert_from_image_to_cv2(image),
        None,  # used for multiple frames
        strength,  # h
        colored_strength,  # usually same as `strength`
        templateWindowSize,  # odd, recommended 7
        searchWindowSize,  # odd, recommended 21
    )

    return denoised_image


class DenoiseWidget(ImageCompareWidget):
    def __init__(self, root, parent=None):
        super().__init__(root, parent=self)
        self.root = root
        self.parent = parent or root

        self.strength = tk.IntVar()
        self.colored_strength = tk.IntVar()
        self.templateWindowSize = tk.IntVar()
        self.searchWindowSize = tk.IntVar()

        self.add_slider(1, "dn-strength", self.strength, (0, 100), "Strength")
        self.add_slider(
            1,
            "dn-colored-strength",
            self.colored_strength,
            (0, 255),
            "Colored strength",
        )
        self.add_slider(
            2,
            "dn-template-window-size",
            self.templateWindowSize,
            (1, 100),
            "Template window size",
        )
        self.add_slider(
            2,
            "dn-search-window-size",
            self.searchWindowSize,
            (1, 100),
            "Search window size",
        )

    def update_filter(self):
        if self.orig_image is None:
            return
        cv2_img = get_denoise(
            self.orig_image,
            int(self.strength.get()),
            int(self.colored_strength.get()),
            int(self.templateWindowSize.get()),
            int(self.searchWindowSize.get()),
        )
        self.modified_image = cv2_img
        self.update_filtered_image()
