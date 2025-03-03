import rawpy
import numpy as np
from PIL import Image
import pyexiv2  # For EXIF data
import os
from astropy.io import fits

class MasterDark:
    def __init__(self):
        self.master_dark = None

    def compute_master_dark(self, dark_files):
        if not dark_files:
            return None, "No dark files loaded."

        dark_images = []
        print(f"Working in directory: {os.path.dirname(dark_files[0])}")
        for dark_file in dark_files:
            try:
                # Use rawpy to read the RAW dark files
                print(f"Loading dark file: {os.path.basename(dark_file)}")
                with rawpy.imread(dark_file) as raw:
                    # Get the post-processed image without white balance and rotation
                    dark_image = raw.postprocess(no_auto_bright=True, use_camera_wb=False, output_color=rawpy.ColorSpace.raw, output_bps=16)  # 16-bit image
                    
                    #print(f"Dark image shape: {dark_image.shape}")
                    
                    # Step 2: Extract EXIF data using pyexiv2
                    metadata = pyexiv2.Image(dark_file)
                    exif_data = metadata.read_exif()
        
                    
                    # Step 3: Check for orientation tag (tag 274 corresponds to orientation)
                    for key in exif_data:
                        #print(key)
                        if key == 'Exif.Image.Orientation':
                            orientation = int(exif_data[key])
                            #print(f"Orientation: {orientation}")
                            
                            # Apply rotation based on EXIF orientation value
                            if orientation == 1:  # 90 degrees clockwise
                                print('Rotating 90 degrees clockwise.')
                                dark_image = np.rot90(dark_image, 1, axes=(0, 1))
                            if orientation == 3:  # 180 degrees
                                print('Rotating 180 degrees.')
                                dark_image = np.rot90(dark_image, 2, axes=(0, 1))
                            elif orientation == 6:  # 90 degrees counterclockwise
                                print('Rotating 90 degrees counterclockwise.')
                                dark_image = np.rot90(dark_image, 3, axes=(0, 1))
                            elif orientation == 8:  # No rotation
                                #print('No rotation needed.')
                                do_nothing = True
                            break
                    
                    #print(f"Dark image shape: {dark_image.shape}")
                    
                    dark_images.append(dark_image.astype(np.float32))  # Ensure high precision with float32
                #print(f"Successfully loaded dark file: {dark_file}")
            except Exception as e:
                print(f"Error opening dark file {dark_file}: {str(e)}")

        # Compute the average of the dark images (master dark)
        
        print(f"Computing master dark from {len(dark_images)} dark frames.")
        # Apply sigma clipping before averaging
        print(f"Computing mean...")
        mean = np.mean(dark_images, axis=0)
        print(f"Computing std...")
        std = np.std(dark_images, axis=0)
        sigma = 5  # You can adjust the sigma value as needed

        print("Applying sigma clipping...")
        # Create a mask for values within the sigma range
        mask = np.abs(dark_images - mean) < sigma * std

        print("Computing masked average...")
        # Compute the average of the masked values
        masked_dark_images = np.ma.masked_array(dark_images, mask=~mask)
        master_dark_array = np.ma.mean(masked_dark_images, axis=0)
        
        self.master_dark = np.array(master_dark_array)  # Convert to a regular NumPy array
        print("Master dark computed successfully.")
        return self.master_dark, "Master dark computed successfully."
    
    def load_master_dark(self, master_dark_file):
        try:
            with fits.open(master_dark_file) as hdul:
                self.master_dark = hdul[0].data.astype(np.float32)
            print(f"Master dark loaded successfully from {master_dark_file}.")
        except Exception as e:
            print(f"Error loading master dark file {master_dark_file}: {str(e)}")

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
