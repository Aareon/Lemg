import tkinter as tk

import cv2
from PIL import Image, ImageFilter

from utils import convert_from_image_to_cv2
from widgets import ImageCompareWidget


def get_blur(image: Image, kernel, sigma):
    blurred_image = cv2.GaussianBlur(
        convert_from_image_to_cv2(image), (kernel, kernel), sigmaX=sigma
    )
    return blurred_image


def get_blur_with_radius(image: Image, radius=2):
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=radius))
    return blurred_image


class BlurWidget(ImageCompareWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        # variables for cv2 blur
        self.kernel = tk.IntVar()
        self.sigma = tk.IntVar()

        # variable for PIL blur
        self.radius = tk.IntVar()

        self.mode = tk.StringVar()

        self.add_combo(
            ["Gaussian(k,o)", "Gaussian(r)"],
            "Gaussian(k,o)",
            self.mode,
            "blur-mode",
            "Blur method",
            side="above",
        )

        self.add_slider(2, "blur-kernel", self.kernel, (1, 255), "Kernel size")
        self.add_slider(1, "blur-sigma", self.sigma, (1, 255), "Sigma")

        self.add_slider(1, "blur-radius", self.radius, (0, 25), "Radius")
        self.hide_slider(
            "blur-radius"
        )  # cv2 is used by default, and uses kernel and sigma

    def update_filter(self):
        if self.orig_image is None:
            return
        curr_mode = self.mode.get()

        if curr_mode == "Gaussian(k,o)":
            self.modified_image = get_blur(
                self.orig_image, int(self.kernel.get()), int(self.sigma.get())
            )
        elif curr_mode == "Gaussian(r)":
            self.modified_image = get_blur_with_radius(
                self.pil_orig_image, int(self.radius.get())
            )

        self.update_filtered_image()

    def change_combo(self, event):
        if event == "Gaussian(k,o)":
            self.hide_slider("blur-radius")
            self.show_slider("blur-kernel")
            self.show_slider("blur-sigma")
        elif event == "Gaussian(r)":
            self.hide_slider("blur-kernel")
            self.hide_slider("blur-sigma")
            self.show_slider("blur-radius")
