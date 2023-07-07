import tkinter as tk
from tkinter.ttk import Notebook
from widgets.edge_detection import EdgeDetectionWidget
from widgets.blur import BlurWidget
from utils import open_image
from widgets.denoise import DenoiseWidget

import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # noqa

from pathlib import Path

SRC_PATH = Path(__file__).parent
RES_PATH = SRC_PATH.parent / "res"


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.style = ttk.Style("superhero")

        # set window icon
        window_icon_path = RES_PATH.joinpath("favicon-32x32.png").resolve()
        self.call("wm", "iconphoto", self._w, tk.Image("photo", file=window_icon_path))

        self.wm_title("Lemg")

        self.filter_widgets = []

        self.curr_image_fp = tk.StringVar(value="Current image:")

    def build(self):
        open_image_frame = ttk.Frame(self, height=100)

        open_image_button = ttk.Button(
            open_image_frame, text="Open Image", command=self.open_image
        )
        self.update()
        open_image_button.pack(side="left", padx=5)

        curr_image_label = ttk.Label(
            open_image_frame, textvariable=self.curr_image_fp
        )
        curr_image_label.pack(side="left", expand=True, fill="x")

        open_image_frame.pack(fill="x", pady=10)

        self.notebook = Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.edge_detection_widget = EdgeDetectionWidget(self.notebook).build()
        self.blur_widget = BlurWidget(self.notebook).build()
        self.denoise_widget = DenoiseWidget(self.notebook).build()

        self.add_filter_widget(self.edge_detection_widget, "Edge Detection")
        self.add_filter_widget(self.blur_widget, "Blur")
        self.add_filter_widget(self.denoise_widget, "Denoise")

        return self

    def add_filter_widget(self, widget, title):
        if widget not in self.filter_widgets:
            self.filter_widgets.append(widget)
            self.notebook.add(widget, text=title)

    def update_image(self):
        if self.pil_image is None:
            return
        for w in self.filter_widgets:
            w.update_image(self.pil_image)

    def open_image(self):
        image = open_image()
        if image is None:
            return
        self.pil_image, image_fp = (*image,)
        self.curr_image_fp.set(f"Current image: {image_fp}")
        self.update_image()


if __name__ == "__main__":
    app = App().build()

    app.mainloop()
