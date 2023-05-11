import sys
#sys.path.append('IGEV_Stereo/core')
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import argparse
import glob
import numpy as np
import numpy.ma
import torch
from tqdm import tqdm
from pathlib import Path
from .core.igev_stereo import IGEVStereo
from .core.utils.utils import InputPadder
from PIL import Image
from matplotlib import pyplot as plt
import os
import cv2

def load_image(imfile,device):
    img = np.array(Image.open(imfile)).astype(np.uint8)
    img = torch.from_numpy(img).permute(2, 0, 1).float()
    return img[None].to(device)

def pim_to_torch(pim,device):
    img = np.array(pim).astype(np.uint8)
    img = torch.from_numpy(img).permute(2, 0, 1).float()
    return img[None].to(device)


class ArgProvider:
    def __getattr__(self,k):
        return default_args[k]
default_args={
    "mixed_precision":False,
    "valid_iters":32,
    "hidden_dims":[128,128,128],
    "corr_implementation":"reg",
    "shared_backbone":False,
    "corr_levels":2,
    "corr_radius":4,
    "n_downsample":2,
    "slow_fast_gru":False,
    "n_gru_layers":3,
    "max_disp":192
    }
args=ArgProvider()# So janky ...but it runs so ehhh

class IGEVDriver:
    def __init__(self,modelpath,use_cuda=False):
        
        if use_cuda:
            self._device="cuda"
        else:
            self._device="cpu"

        checkpoint=modelpath
        model = torch.nn.DataParallel(IGEVStereo(args), device_ids=[0])
        model.load_state_dict(torch.load(checkpoint,map_location=torch.device('cpu')))

        model = model.module
        model.to(self._device)
        model.eval()

        #output_directory = Path(args.output_directory)
        #output_directory.mkdir(exist_ok=True)

        self._model=model

    def calculate(self,*,left,right,depth_multiplier=1):
        model=self._model
        with torch.no_grad():

            #for (imfile1, imfile2) in tqdm(list(zip(left_images, right_images))):
            image1 = pim_to_torch(left,self._device)
            image2 = pim_to_torch(right,self._device)

            padder = InputPadder(image1.shape, divis_by=32)
            image1, image2 = padder.pad(image1, image2)

            disp = model(image1, image2, iters=args.valid_iters, test_mode=True)
            disp = disp.cpu().numpy()
            disp = padder.unpad(disp)

                #file_stem = imfile1.split('/')[-2]
                #filename = os.path.join(output_directory, f"{file_stem}.png")
                #plt.imsave(output_directory / f"{file_stem}.png", disp.squeeze(), cmap='jet')
                # disp = np.round(disp * 256).astype(np.uint16)
                # cv2.imwrite(filename, cv2.applyColorMap(cv2.convertScaleAbs(disp.squeeze(), alpha=0.01),cv2.COLORMAP_JET), [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        disparity = disp[0][0]
        disparity_masked=numpy.ma.masked_less_equal(disparity,0)
        #return disparity_masked
        disparity_float=disparity_masked.astype(float)
        depth=1/disparity_float
        return depth*depth_multiplier


'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--restore_ckpt', help="restore checkpoint", default='./pretrained_models/sceneflow/sceneflow.pth')
    parser.add_argument('--save_numpy', action='store_true', help='save output as numpy arrays')

    parser.add_argument('-l', '--left_imgs', help="path to all first (left) frames", default="./demo-imgs/*/im0.png")
    parser.add_argument('-r', '--right_imgs', help="path to all second (right) frames", default="./demo-imgs/*/im1.png")

    # parser.add_argument('-l', '--left_imgs', help="path to all first (left) frames", default="/data/Middlebury/trainingH/*/im0.png")
    # parser.add_argument('-r', '--right_imgs', help="path to all second (right) frames", default="/data/Middlebury/trainingH/*/im1.png")
    # parser.add_argument('-l', '--left_imgs', help="path to all first (left) frames", default="/data/ETH3D/two_view_training/*/im0.png")
    # parser.add_argument('-r', '--right_imgs', help="path to all second (right) frames", default="/data/ETH3D/two_view_training/*/im1.png")
    parser.add_argument('--output_directory', help="directory to save output", default="./demo-output/")
    parser.add_argument('--mixed_precision', action='store_true', help='use mixed precision')
    parser.add_argument('--valid_iters', type=int, default=32, help='number of flow-field updates during forward pass')

    # Architecture choices
    parser.add_argument('--hidden_dims', nargs='+', type=int, default=[128]*3, help="hidden state and context dimensions")
    parser.add_argument('--corr_implementation', choices=["reg", "alt", "reg_cuda", "alt_cuda"], default="reg", help="correlation volume implementation")
    parser.add_argument('--shared_backbone', action='store_true', help="use a single backbone for the context and feature encoders")
    parser.add_argument('--corr_levels', type=int, default=2, help="number of levels in the correlation pyramid")
    parser.add_argument('--corr_radius', type=int, default=4, help="width of the correlation pyramid")
    parser.add_argument('--n_downsample', type=int, default=2, help="resolution of the disparity field (1/2^K)")
    parser.add_argument('--slow_fast_gru', action='store_true', help="iterate the low-res GRUs more frequently")
    parser.add_argument('--n_gru_layers', type=int, default=3, help="number of hidden GRU levels")
    parser.add_argument('--max_disp', type=int, default=192, help="max disp of geometry encoding volume")
    
    args = parser.parse_args()

    Path(args.output_directory).mkdir(exist_ok=True, parents=True)

    demo(args)
'''

if __name__=="__main__":
    pimL=Image.open("../captures/acu_L.jpg")
    pimR=Image.open("../captures/acu_R.jpg")
    print(calculate(pimL,pimR))
