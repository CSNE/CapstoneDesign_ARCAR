import cv2
import numpy as np
import pyk4a
from typing import Optional, Tuple
from pyk4a import Config, PyK4A
import collections
import PIL.Image

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

def getK4A(): # get k4a
    k4a = PyK4A(
        Config(
            color_resolution=pyk4a.ColorResolution.RES_720P,
            depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
        )
    )
    return k4a

KinectCaptureData=collections.namedtuple(
    "KinectCaptureData",
    ["color_image", # RGB Color Image [PIL.Image]
     "depth_data_raw", # Raw Depth data [ndarray[float]] (depth in meters)
     "depth_data_mapped", # Depth data, mapped to the geometry of RGB image. [ndarray[float]]
     "depth_visualization", # Depth visuals. [PIL.Image]
     "IR_image", # IR Image NYI
     "IR_mapped" # IR, mapped to the geometry of RGB image. NYI
     ])
def getCap(k4a:PyK4A):
    capture = k4a.get_capture()
    return KinectCaptureData(
        color_image=cv2_to_pil(capture.color), 
        depth_data_raw=depth_millimeter_to_meters(capture.depth),
        depth_data_mapped=depth_millimeter_to_meters(capture.transformed_depth),
        depth_visualization=cv2_to_pil(colorize(capture.transformed_depth, (None, 10000), cv2.COLORMAP_JET)),
        IR_image=None,#cv2_to_pil(capture.ir),
        IR_mapped=None)#cv2_to_pil(capture.transformed_ir))

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


def main():
    k4a = getK4A() 
    k4a.start()

    kcd = getCap(k4a)
    print("Color")
    print(type(kcd.color_image))
    kcd.color_image.show()
    print("Depth Mapped")
    print(type(kcd.depth_data_mapped))
    print(kcd.depth_data_mapped.dtype)
    print(kcd.depth_data_mapped)
    kcd.depth_visualization.show()
    
    

    
if __name__ == "__main__":
    main()

