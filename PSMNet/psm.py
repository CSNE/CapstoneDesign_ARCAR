from __future__ import print_function
import argparse
import os
import random
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torch.nn.functional as F
import numpy as np
import time
import math
from .models import *
import cv2
from PIL import Image

# 2012 data /media/jiaren/ImageNet/data_scene_flow_2012/testing/

'''
parser = argparse.ArgumentParser(description='PSMNet')
parser.add_argument('--KITTI', default='2015',
                    help='KITTI version')
parser.add_argument('--datapath', default='/media/jiaren/ImageNet/data_scene_flow_2015/testing/',
                    help='select model')
parser.add_argument('--loadmodel', default='./trained/pretrained_model_KITTI2015.tar',
                    help='loading model')
parser.add_argument('--leftimg', default= './VO04_L.png',
                    help='load model')
parser.add_argument('--rightimg', default= './VO04_R.png',
                    help='load model')                                      
parser.add_argument('--model', default='stackhourglass',
                    help='select model')
parser.add_argument('--maxdisp', type=int, default=192,
                    help='maxium disparity')
parser.add_argument('--no-cuda', action='store_true', default=False,
                    help='enables CUDA training')
parser.add_argument('--seed', type=int, default=1, metavar='S',
                    help='random seed (default: 1)')
args = parser.parse_args()
'''
class args:
    model="stackhourglass"
    maxdisp=192
    seed=1

class PSMDriver:
    def __init__(self,model_path,use_cuda=False):
        self._cuda=use_cuda
        torch.manual_seed(args.seed)
        if use_cuda:
            torch.cuda.manual_seed(args.seed)

        if args.model == 'stackhourglass':
            model = stackhourglass(args.maxdisp,use_cuda=use_cuda)
        elif args.model == 'basic':
            0/0#model = basic(args.maxdisp)
        else:
            print('no model')
        
        self._model = nn.DataParallel(model, device_ids=[0])
        if use_cuda:
            self._model.cuda()
        else:
            self._model.cpu()

        #print('load PSMNet')
        if use_cuda:
            state_dict = torch.load(model_path,map_location=torch.device("cuda"))
        else:
            state_dict = torch.load(model_path,map_location=torch.device("cpu"))        
        self._model.load_state_dict(state_dict['state_dict'])
        
        # When using CPU, unwrap from DataParallel immediately.
        # Or this model will error out when evaluating.
        # https://discuss.pytorch.org/t/solved-keyerror-unexpected-key-module-encoder-embedding-weight-in-state-dict/1686/2
        if not use_cuda:
            self._model=self._model.module

        #print('Number of model parameters: {}'.format(sum([p.data.nelement() for p in self._model.parameters()])))

    def test(self,imgL,imgR):
        self._model.eval()

        if self._cuda:
           imgL = imgL.cuda()
           imgR = imgR.cuda()   
           #print(type(imgL))
           #print(imgL.get_device())
           #print(type(self._model))

        with torch.no_grad():
            disp = self._model(imgL,imgR)

        disp = torch.squeeze(disp)
        pred_disp = disp.data.cpu().numpy()

        return pred_disp


    def calculate(self,*,left,right,depth_multiplier=100):

        normal_mean_var = {'mean': [0.485, 0.456, 0.406],
                            'std': [0.229, 0.224, 0.225]}
        infer_transform = transforms.Compose([transforms.ToTensor(),
                                              transforms.Normalize(**normal_mean_var)])    

        imgL_o = left.convert('RGB')
        imgR_o = right.convert('RGB')

        imgL = infer_transform(imgL_o)
        imgR = infer_transform(imgR_o) 
       

        # pad to width and hight to 16 times
        if imgL.shape[1] % 16 != 0:
            times = imgL.shape[1]//16       
            top_pad = (times+1)*16 -imgL.shape[1]
        else:
            top_pad = 0

        if imgL.shape[2] % 16 != 0:
            times = imgL.shape[2]//16                       
            right_pad = (times+1)*16-imgL.shape[2]
        else:
            right_pad = 0    

        imgL = F.pad(imgL,(0,right_pad, top_pad,0)).unsqueeze(0)
        imgR = F.pad(imgR,(0,right_pad, top_pad,0)).unsqueeze(0)

        start_time = time.time()
        pred_disp = self.test(imgL,imgR)
        #print('time = %.2f' %(time.time() - start_time))

        
        if top_pad !=0 and right_pad != 0:
            img = pred_disp[top_pad:,:-right_pad]
        elif top_pad ==0 and right_pad != 0:
            img = pred_disp[:,:-right_pad]
        elif top_pad !=0 and right_pad == 0:
            img = pred_disp[top_pad:,:]
        else:
            img = pred_disp
        
        #img = (img*256).astype('uint16')
        #img = Image.fromarray(img)
        return 1/img*depth_multiplier#.astype(float)
        #img.save('Test_disparity.png')







