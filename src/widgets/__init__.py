import tkinter as tk
from tkinter import filedialog

import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFilter

from utils import convert_from_cv2_to_image, convert_from_image_to_cv2
import ttkbootstrap as ttk


# TODO add_combo(
#    options: List[str],
#    name: str,
#    callback: function
# )

# TODO add_checkbox(
#    name: str,
#    callback: function
# )


class ImageCompareWidget(tk.Frame):
    def __init__(self, root, parent=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self.parent = parent or root

        self.placholder_image: ImageTk = None  # white image used at start

        self.pil_orig_image: Image = None  # Pillow image
        self.tk_orig_image: ImageTk = None  # Tkinter image
        self.orig_image: np.ndarray = None  # Selected by user / cvimage

        self.pil_modified_image: Image = None
        self.modified_image: np.ndarray = None  # Generated using Canny, np.array
        self.tk_modified_image: ImageTk = None

        self.sliders = []
        self.combos = []

        self.hidden = []

        self.selected_slider = None  # updated every time a slider is clicked
        self.has_updated = False  # set the first time the edges are updated

        self.slider_frame = None  # a frame is created and displayed if needed

    def add_combo(
        self,
        options: list[str],
        default: str,
        var: tk.Variable,
        name: str,
        label_text: str | None,
        side: str = "above",  # above / below images
    ):
        combo_frame = tk.Frame(self)

        if label_text is not None:
            combo_label = tk.Label(combo_frame, text=label_text)
            combo_label.pack(side="left", anchor="center")

        combo = ttk.OptionMenu(
            combo_frame, var, default, *options, command=lambda e: self.change_combo(e)
        )
        combo.pack(side="right", anchor="center", expand=True)
        self.combos.append((combo_frame, side))
        return combo

    def add_slider(
        self,
        increment: int,
        name: str,
        var: tk.Variable,
        min_max: tuple[int],
        label_text: str | None,
    ):
        if self.slider_frame is None:
            self.slider_frame = tk.Frame(self, name="master-slider-frame")

        this_frame = tk.Frame(self.slider_frame)

        if label_text is not None:
            label_frame = tk.Frame(this_frame)
            slider_label = tk.Label(label_frame, text=label_text)
            slider_label.pack(side="left", anchor="w", expand=True)
            label_frame.pack(side="left", expand=True)

        scale = tk.Scale(
            this_frame,
            from_=min_max[0],
            to=min_max[1],
            resolution=increment,
            orient="horizontal",
            variable=var,
            name=name,
            command=lambda x: self.update_filter(),
        )
        scale.pack(side="bottom", anchor="center", expand=True)
        self.sliders.append(scale)

        return scale

    def _get_slider_from_name(self, name: str):
        for slider_frame in self.slider_frame.children:
            slider_frame = self.slider_frame.nametowidget(slider_frame)
            try:
                slider = slider_frame.nametowidget(name)
                return slider
            except KeyError:
                continue

    def hide_slider(self, slider: str):
        slider = self._get_slider_from_name(slider)
        if slider is not None:
            slider.master.pack_forget()
            self.hidden.append(slider)

    def show_slider(self, slider: str):
        slider = self._get_slider_from_name(slider)
        if slider is not None and slider in self.hidden:
            slider.pack(side="right")
            slider.master.pack(anchor="center")
            self.hidden.remove(slider)

    def change_combo(self, event):
        """Overwrite this function to handle a combobox change"""
        return

    def update_filter(self):
        """Overwrite this function to apply post-processing to self.image"""
        return

    def update_image(self, image: Image):
        self.pil_orig_image = image.resize((200, 200))
        self.orig_image = convert_from_image_to_cv2(self.pil_orig_image)
        self.tk_orig_image = ImageTk.PhotoImage(self.pil_orig_image)
        self.image1.configure(image=self.tk_orig_image)

        if not self.has_updated:
            self.update_filter()
            self.has_updated = True

    def update_filtered_image(self, image=None):
        # does conversion to ImageTk and updates the displayed filtered image
        if self.modified_image is None:
            return

        if Image.isImageType(self.modified_image):
            self.pil_modified_image = self.modified_image
            self.modified_image = convert_from_image_to_cv2(self.pil_modified_image)
        elif isinstance(self.modified_image, np.ndarray):
            # weirdly
            # colors have come out rotated unless you rotate them again here (BGR->RGB)
            self.pil_modified_image = convert_from_cv2_to_image(
                cv2.cvtColor(self.modified_image, cv2.COLOR_BGR2RGB)
            )
        elif isinstance(self.modified_image, ImageFilter.Filter):
            self.pil_modified_image = self.modified_image
        else:
            raise Exception(f"Unknown image type '{type(self.modified_image)}'")
        self.tk_modified_image = ImageTk.PhotoImage(self.pil_modified_image)
        self.image2.configure(image=self.tk_modified_image)

    def save(self):
        if self.modified_image is None:
            return
        # fmt: off
        fp = filedialog.asksaveasfile(
                filetypes=[("PNG Image", "*.png")],
                defaultextension="*.png",
        )
        # fmt: on
        if fp is None:
            return
        self.pil_modified_image.save(fp.name, format="png")

    def handle_slider_arrows(self, event: tk.Event):
        if self.selected_slider is None:
            return

        if event.type == "3":
            # key release event
            self.update_filter()
            self.update_filtered_image()
            return

    def handle_slider_clicked(self, name):
        self.selected_slider = name
        if self.selected_slider == "lower":
            self.t_lower_slider.focus()
        elif self.selected_slider == "upper":
            self.t_upper_slider.focus()
        self.update_filter()

    def build(self):
        # Create a blank white image for placeholder
        width, height = 200, 200
        white_pil_image = Image.new("RGB", (width, height), "white")
        self.placeholder_image = ImageTk.PhotoImage(white_pil_image)

        used_combos = []  # append combos that are packed at the top
        for combo, side in self.combos:
            if side == "above":
                combo.pack(expand=True)
                used_combos.append(combo)

        image_frame = tk.Frame(self)

        label_frame = tk.Frame(image_frame)
        orig_label = tk.Label(label_frame, text="Original")
        orig_label.pack(side="left", anchor="nw", padx=10)

        filtered_label = tk.Label(label_frame, text="Filtered")
        filtered_label.pack(side="right", anchor="ne", padx=10)
        label_frame.pack(side="top", anchor="center", pady=8)

        self.image1 = tk.Label(image_frame, image=self.placeholder_image)
        self.image1.pack(side="left", anchor="center", padx=10)

        self.image2 = tk.Label(image_frame, image=self.placeholder_image)
        self.image2.pack(side="right", anchor="center", padx=10)
        image_frame.pack(side="top", padx=10, pady=10, anchor="center")

        self.save_button = tk.Button(self, text="Save Filter", command=self.save)
        self.save_button.pack(side="bottom", anchor="center")

        for combo, side in self.combos:
            if combo not in used_combos:
                combo.pack()

        for slider in self.sliders:
            if slider not in self.hidden:
                slider.pack(expand=True, padx=10)
                slider.master.pack()
        self.slider_frame.pack()

        # bind keyboard arrow press events for changing sliders with arrow keys
        self.root.bind("<Left>", self.handle_slider_arrows)
        self.root.bind("<KeyRelease>", self.handle_slider_arrows)
        self.root.bind("<Right>", self.handle_slider_arrows)
        self.root.bind("<KeyRelease>", self.handle_slider_arrows)
        return self
