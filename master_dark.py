import rawpy
import numpy as np
from PIL import Image
import pyexiv2  # For EXIF data

class MasterDark:
    def __init__(self):
        self.master_dark = None

    def compute_master_dark(self, dark_files):
        if not dark_files:
            return None, "No dark files loaded."

        dark_images = []
        for dark_file in dark_files:
            try:
                # Use rawpy to read the RAW dark files
                print(f"Loading dark file: {dark_file}")
                with rawpy.imread(dark_file) as raw:
                    # Get the post-processed image without white balance and rotation
                    dark_image = raw.postprocess(no_auto_bright=True, use_camera_wb=False, output_color=rawpy.ColorSpace.raw, output_bps=16)  # 16-bit image
                    
                    # Step 2: Extract EXIF data using pyexiv2
                    metadata = pyexiv2.ImageMetadata(dark_file)
                    metadata.read()
                    exif_data = metadata.exif_keys
        
                    
                    # Step 3: Check for orientation tag (tag 274 corresponds to orientation)
                    for key in exif_data:
                        if key == 'Exif.Image.Orientation':
                            orientation = metadata[key]
                            
                            # Apply rotation based on EXIF orientation value
                            if orientation == 3:  # 180 degrees
                                dark_image = np.rot90(dark_image, 2)
                            elif orientation == 6:  # 90 degrees clockwise
                                dark_image = np.rot90(dark_image, 3)
                            elif orientation == 8:  # 90 degrees counterclockwise
                                dark_image = np.rot90(dark_image, 1)
                    
                    
                    dark_images.append(dark_image.astype(np.float32))  # Ensure high precision with float32
                print(f"Successfully loaded dark file: {dark_file}")
            except Exception as e:
                return None, f"Error opening dark file {dark_file}: {str(e)}"

        # Compute the average of the dark images (master dark)
        master_dark_array = np.mean(dark_images, axis=0)  # Keep as float32 for precision
        self.master_dark = master_dark_array
        return self.master_dark, "Master dark computed successfully."

    def subtract_master_dark(self, image):
        if self.master_dark is None:
            return image, "No master dark to subtract."

        # Use rawpy to read the input image and get the post-processed data without white balance and rotation
        with rawpy.imread(image) as raw:
            image_data = raw.postprocess(no_auto_bright=True, use_camera_wb=False, output_color=rawpy.ColorSpace.raw, output_bps=16)  # 16-bit image
            image_array = image_data.astype(np.float32)  # Ensure high precision with float32

        # Ensure the image and master dark arrays have the same shape
        if image_array.shape != self.master_dark.shape:
            return image, "Image and master dark dimensions do not match."

        # Subtract the master dark from the image
        corrected_image_array = image_array - self.master_dark

        # Clip the values to valid range (0-65535 for 16-bit images)
        corrected_image_array = np.clip(corrected_image_array, 0, 65535)

        # Convert back to a 16-bit image (using rawpy to handle the conversion properly)
        corrected_image = Image.fromarray(corrected_image_array.astype(np.uint16))  # Use uint16 for precision
        return corrected_image, "Master dark subtracted."
