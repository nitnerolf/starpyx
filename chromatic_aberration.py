import numpy as np
from PIL import Image

class ChromaticAberrationCorrection:
    def __init__(self, red_shift=(0, 0), blue_shift=(0, 0)):
        """
        Initialize the chromatic aberration correction.
        
        :param red_shift: Tuple (x, y) indicating the shift for the red channel
        :param blue_shift: Tuple (x, y) indicating the shift for the blue channel
        """
        self.red_shift = red_shift
        self.blue_shift = blue_shift

    def correct_aberration(self, image):
        """
        Apply chromatic aberration correction to the image by shifting the color channels.

        :param image: PIL Image object
        :return: Corrected PIL Image object
        """
        # Convert the image to a NumPy array (RGBA or RGB format)
        image_array = np.array(image)
        
        # If it's a 4-channel image (RGBA), separate the channels
        if image_array.shape[2] == 4:  # RGBA image
            r, g, b, a = np.split(image_array, 4, axis=-1)
            a = a.squeeze()  # remove the alpha channel as we don't need it for correction
        else:
            r, g, b = np.split(image_array, 3, axis=-1)

        r, g, b = r.squeeze(), g.squeeze(), b.squeeze()  # Remove extra dimensions

        # Apply shift correction
        r_corrected = self.shift_channel(r, *self.red_shift)
        b_corrected = self.shift_channel(b, *self.blue_shift)

        # Stack the channels back together
        corrected_image_array = np.stack([r_corrected, g, b_corrected], axis=-1)

        # Convert the corrected NumPy array back to a PIL Image
        corrected_image = Image.fromarray(corrected_image_array.astype(np.uint8))

        return corrected_image

    def shift_channel(self, channel, shift_x, shift_y):
        """
        Shift a color channel using padding and slicing.
        
        :param channel: 2D numpy array representing a single color channel
        :param shift_x: Horizontal shift in pixels
        :param shift_y: Vertical shift in pixels
        :return: Shifted 2D numpy array
        """
        # Shift the image (using numpy's roll function for efficiency)
        shifted_channel = np.roll(channel, shift_x, axis=1)  # horizontal shift
        shifted_channel = np.roll(shifted_channel, shift_y, axis=0)  # vertical shift

        return shifted_channel
