# Image routines for the image processing application
import rawpy

# Define the main application class
class image:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing Application")
        self.create_widgets()

    def load_image(self, image_file):
        # Get the post-processed image without white balance and rotation
        # Use rawpy to read the RAW dark files
        print(f"Loading dark file: {image_file}")
        with rawpy.imread(image_file) as raw:
            image = raw.postprocess(no_auto_bright=True, use_camera_wb=False,
                                    output_color=rawpy.ColorSpace.raw, output_bps=16)  # 16-bit image
            
        print(f" image shape: {image.shape}")
            
        return image
                    