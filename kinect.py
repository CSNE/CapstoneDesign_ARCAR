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


DepthMode={
    'NFOV_2X2BINNED': pyk4a.DepthMode.NFOV_2X2BINNED,
    "nb":             pyk4a.DepthMode.NFOV_2X2BINNED,
    'NFOV_UNBINNED':  pyk4a.DepthMode.NFOV_UNBINNED,
    "nu":             pyk4a.DepthMode.NFOV_UNBINNED,
    'WFOV_2X2BINNED': pyk4a.DepthMode.WFOV_2X2BINNED,
    "wb":             pyk4a.DepthMode.WFOV_2X2BINNED,
    'WFOV_UNBINNED':  pyk4a.DepthMode.WFOV_UNBINNED,
    "wu":             pyk4a.DepthMode.WFOV_UNBINNED
    }
ColorResolution={
    'RES_720P':  pyk4a.ColorResolution.RES_720P,
    "720":       pyk4a.ColorResolution.RES_720P,
    'RES_1080P': pyk4a.ColorResolution.RES_1080P,
    "1080":      pyk4a.ColorResolution.RES_1080P,
    'RES_1440P': pyk4a.ColorResolution.RES_1440P,
    "1440":      pyk4a.ColorResolution.RES_1440P,
    'RES_1536P': pyk4a.ColorResolution.RES_1536P,
    "1536":      pyk4a.ColorResolution.RES_1536P,
    'RES_2160P': pyk4a.ColorResolution.RES_2160P,
    "2160":      pyk4a.ColorResolution.RES_2160P,
    'RES_3072P': pyk4a.ColorResolution.RES_3072P,
    "3072":      pyk4a.ColorResolution.RES_3072P
    }
FPS={
    "5":pyk4a.FPS.FPS_5,
    "15":pyk4a.FPS.FPS_15,
    "30":pyk4a.FPS.FPS_30
    }

def getK4A(cr:ColorResolution,dm:DepthMode,fps:FPS): # get k4a
    k4a = PyK4A(
        Config(
            color_resolution=cr,
            depth_mode=dm,
            camera_fps=fps
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
        depth_data_raw=depth_millimeter_to_meters(filter_out_zeros(capture.depth)),
        depth_data_mapped=depth_millimeter_to_meters(filter_out_zeros(capture.transformed_depth)),
        depth_visualization=cv2_to_pil(colorize(filter_out_zeros(capture.transformed_depth), (None, 10000), cv2.COLORMAP_JET)),
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

def filter_out_zeros(depth_data):
    # Mask out zeroes.
    return np.ma.masked_equal(depth_data, 0)


if __name__ == "__main__":
    # Testing code
    k4a = getK4A(pyk4a.ColorResolution.RES_720P,
                 pyk4a.DepthMode.NFOV_UNBINNED,
                 pyk4a.FPS.FPS_15)
    k4a.start()
    kcd = getCap(k4a)
    kcd.color_image.show()

