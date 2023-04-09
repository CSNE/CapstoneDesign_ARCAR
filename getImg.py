import cv2
import numpy as np
import pyk4a
from typing import Optional, Tuple
from pyk4a import Config, PyK4A

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

def getCap(k4a): # return tuple (color img, depth img)
    capture = k4a.get_capture()
    return (capture.color, colorize(capture.transformed_depth, (None, 10000), cv2.COLORMAP_JET))


"""
def main():
    k4a = getK4A()
    k4a.start()

    capture = getCap(k4a)

    cv2.imshow("color", capture[0])
    cv2.waitKey(3000000)
    cv2.imshow("depth", capture[1])
    cv2.waitKey(3000000)

    
if __name__ == "__main__":
    main()
"""
