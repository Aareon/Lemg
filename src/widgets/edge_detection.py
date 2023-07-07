import tkinter as tk

import cv2

from widgets import ImageCompareWidget
from widgets.blur import get_blur


def get_edges(image, t_lower, t_upper):
    # Apply Canny edge detection
    edges = cv2.Canny(image, t_lower, t_upper)
    return edges


def get_gaussian_edges(image, ksize, sigma):
    # img1: get gaussian with no sigma (scaler)
    # img2: get gaussian with sigma
    # subtract img2 from img1 and return result
    try:
        img1 = get_blur(image, ksize, 0)
        img2 = get_blur(image, ksize, sigma)
        return cv2.subtract(img1, img2)
    except cv2.error as e:
        print(e)
        print(f"ksize: {type(ksize)} : {ksize}")


class EdgeDetectionWidget(ImageCompareWidget):
    def __init__(self, root, parent=None):
        super().__init__(root, parent=parent)
        self.root = root
        self.parent = parent or root

        # Canny vars
        self.t_lower = tk.IntVar()
        self.t_upper = tk.IntVar()

        # Gaussian vars
        self.kernel = tk.IntVar()
        self.sigma = tk.IntVar()

        self.mode = tk.StringVar()

        self.mode_combo = self.add_combo(
            ["Canny", "Gaussian Differential"],
            "Canny",
            self.mode,
            "edge-det-mode",
            "Detection method",
        )

        # Canny sliders
        self.add_slider(1, "edge-det-lower", self.t_lower, (0, 255), "Lower threshold")
        self.add_slider(1, "edge-det-upper", self.t_upper, (0, 255), "Upper threshold")

        # Gaussian sliders
        self.add_slider(2, "edge-det-kernel", self.kernel, (1, 255), "Kernel size")
        self.add_slider(1, "edge-det-sigma", self.sigma, (0, 255), "Sigma")
        self.hide_slider("edge-det-kernel")  # hide sliders by default
        self.hide_slider("edge-det-sigma")

    def update_filter(self, *args):
        if self.orig_image is None:
            return
        curr_mode = self.mode.get()

        if curr_mode == "Canny":
            cv2_img = get_edges(
                self.orig_image, float(self.t_lower.get()), float(self.t_upper.get())
            )
        elif curr_mode == "Gaussian Differential":
            cv2_img = get_gaussian_edges(
                self.orig_image, int(self.kernel.get()), self.sigma.get()
            )
        self.modified_image = cv2_img
        self.update_filtered_image()

    def change_combo(self, event):
        if event == "Canny":
            self.hide_slider("edge-det-kernel")
            self.hide_slider("edge-det-sigma")
            self.show_slider("edge-det-lower")
            self.show_slider("edge-det-upper")
        elif event == "Gaussian Differential":
            self.hide_slider("edge-det-lower")
            self.hide_slider("edge-det-upper")
            self.show_slider("edge-det-kernel")
            self.show_slider("edge-det-sigma")
