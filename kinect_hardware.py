import pyk4a
from typing import Optional, Tuple
from pyk4a import Config, PyK4A

from kinect_common import *



def getK4A(cr,dm,fps): # get k4a
    dm={
        'NFOV_2X2BINNED': pyk4a.DepthMode.NFOV_2X2BINNED,
        "nb":             pyk4a.DepthMode.NFOV_2X2BINNED,
        'NFOV_UNBINNED':  pyk4a.DepthMode.NFOV_UNBINNED,
        "nu":             pyk4a.DepthMode.NFOV_UNBINNED,
        'WFOV_2X2BINNED': pyk4a.DepthMode.WFOV_2X2BINNED,
        "wb":             pyk4a.DepthMode.WFOV_2X2BINNED,
        'WFOV_UNBINNED':  pyk4a.DepthMode.WFOV_UNBINNED,
        "wu":             pyk4a.DepthMode.WFOV_UNBINNED
        }[dm]
    cr={
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
        }[cr]
    fps={
        "5":pyk4a.FPS.FPS_5,
        "15":pyk4a.FPS.FPS_15,
        "30":pyk4a.FPS.FPS_30
        }[fps]
    k4a = PyK4A(
        Config(
            color_resolution=cr,
            depth_mode=dm,
            camera_fps=fps
        )
    )
    return k4a

def getCap(k4a:PyK4A):
    capture = k4a.get_capture()
    return KinectCaptureData(
        color_image=cv2_to_pil(capture.color), 
        depth_data_raw=depth_millimeter_to_meters(filter_out_zeros(capture.depth)),
        depth_data_mapped=depth_millimeter_to_meters(filter_out_zeros(capture.transformed_depth)))

if __name__ == "__main__":
    # Testing code
    k4a = getK4A(pyk4a.ColorResolution.RES_720P,
                 pyk4a.DepthMode.NFOV_UNBINNED,
                 pyk4a.FPS.FPS_15)
    k4a.start()
    kcd = getCap(k4a)
    kcd.color_image.show()
