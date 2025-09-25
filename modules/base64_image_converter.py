import base64
import json
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from PIL import Image, ImageTk
import io
import time

class Base64ImageConverterApp:
    def __init__(self):
        self.original_image = None
        self.root = tk.Tk()
        self.root.title("Base64 to Image Converter")

        self.text_box = tk.Text(self.root, height=10, width=50)
        self.text_box.pack(padx=10, pady=10)

        self.decode_button = tk.Button(self.root, text="Decode", command=self.decode_image)
        self.decode_button.pack(pady=10)

        self.select_button = tk.Button(self.root, text="Select File", command=self.select_file)
        self.select_button.pack(pady=10)

        self.save_button = tk.Button(self.root, text="Save Image", command=self.save_image)
        self.save_button.pack_forget()  # Hidden at start

        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=10)

    def base64_to_img(self, base64_string):
        try:
            img_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(img_data))
            image.info['dpi'] = (72, 72)
            self.original_image = image
            return image
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return None

    def decode_image(self):
        input_data = self.text_box.get("1.0", "end-1c").strip()
        if input_data:
            try:
                data = json.loads(input_data)
                base64_string = data.get("image")
                if base64_string:
                    image = self.base64_to_img(base64_string)
                    if image:
                        self.display_image(image)
                        self.save_button.pack()
                else:
                    messagebox.showerror("Error", "No 'image' field found in the JSON data.")
            except json.JSONDecodeError:
                image = self.base64_to_img(input_data)
                if image:
                    self.display_image(image)
                    self.save_button.pack()
                else:
                    messagebox.showerror("Error", "Invalid Base64 string.")
        else:
            messagebox.showerror("Error", "Input is empty.")

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text and CSV files", "*.txt *.csv")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                input_data = file.read().strip()

            if input_data:
                try:
                    data = json.loads(input_data)
                    base64_string = data.get("image")
                    if base64_string:
                        image = self.base64_to_img(base64_string)
                        if image:
                            self.display_image(image)
                            self.save_button.pack()
                    else:
                        messagebox.showerror("Error", "No 'image' field found in the JSON data.")
                except json.JSONDecodeError:
                    image = self.base64_to_img(input_data)
                    if image:
                        self.display_image(image)
                        self.save_button.pack()
                    else:
                        messagebox.showerror("Error", "Invalid Base64 string.")
            else:
                messagebox.showerror("Error", "File is empty.")

    def display_image(self, image):
        preview_image = image.copy()
        preview_image.thumbnail((400, 400))  # Resize for preview
        photo = ImageTk.PhotoImage(preview_image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

    def save_image(self):
        if not self.original_image:
            messagebox.showerror("Error", "No image to save.")
            return

        save_folder = r"C:\Users\900803\Downloads\Hendri\Project\decoded_image"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        save_path = os.path.join(save_folder, f"KTP_IMG_{time.strftime('%Y%m%d_%H%M%S')}.png")

        try:
            self.original_image.save(save_path)
            messagebox.showinfo("Success", f"Image saved as {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the image: {str(e)}")

    def run(self):
        self.root.mainloop()
