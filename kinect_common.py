import cv2
import numpy as np
import collections
import PIL.Image
import io
from typing import Optional, Tuple

KinectCaptureData=collections.namedtuple(
    "KinectCaptureData",
    ["color_image", # RGB Color Image [PIL.Image]
     "depth_data_raw", # Raw Depth data [ndarray[float]] (depth in meters)
     "depth_data_mapped" # Depth data, mapped to the geometry of RGB image. [ndarray[float]]
     ])
	
	
def colorize(
    image: np.ndarray,
    clipping_range: Tuple[Optional[int], Optional[int]] = (None, None),
    colormap: int = cv2.COLORMAP_HSV,
) -> np.ndarray:
    if clipping_range[0] or clipping_range[1]:
        img = image.clip(clipping_range[0], clipping_range[1])
    else:
        img = image.copy()
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    img = cv2.applyColorMap(img, colormap)
    return img

def cv2_to_pil(cv2_image):
    # Convert CV2 image to PIL image
    # The rest of the code uses PIL images, so this just makes things
    # easier to handle
    conv = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    return PIL.Image.fromarray(conv)

def depth_millimeter_to_meters(depth_data):
    # Convert millimeter data of Kinect SDK to meters
    # This is to match how MonoDepth handles things
    return depth_data.astype(float)/1000.0

def filter_out_zeros(depth_data):
    # Mask out zeroes.
    return np.ma.masked_equal(depth_data, 0)



