# Functions using MonoDepth2.
# Code mostly copied from monodepth2/test_simple.py

import os
import sys
import time

import numpy as np
import PIL.Image as pil

import torch
from torchvision import transforms



# Import from MonoDepth2
sys.path.append("monodepth2")
import networks
from layers import disp_to_depth
from utils import download_model_if_doesnt_exist
from evaluate_depth import STEREO_SCALE_FACTOR



class DepthEstimator:
	'''
	Class for running the monodepth2 code.
	Will load & setup model on initialization.
	and estimate() does the actual depth estimation.
	'''
	def __init__(self,model_name="mono+stereo_640x192",use_cuda=False):
		self._model_name=model_name
		self._cuda=use_cuda
		self.net_setup()
		
	def net_setup(self):
		'''
		Setup network. Automatically run on initialization.
		Code mostly from monodepth2/test_simple.py
		'''
		#print("Setup DepthEstimator...")
		if self._cuda:
			self.device = torch.device("cuda")
		else:
			self.device = torch.device("cpu")

		download_model_if_doesnt_exist(self._model_name)
		model_path = os.path.join("models", self._model_name)
		#print("-> Loading model from ", model_path)
		encoder_path = os.path.join(model_path, "encoder.pth")
		depth_decoder_path = os.path.join(model_path, "depth.pth")

		# LOADING PRETRAINED MODEL
		#print("   Loading pretrained encoder")
		self.encoder = networks.ResnetEncoder(18, False)
		loaded_dict_enc = torch.load(encoder_path, map_location=self.device)

		# extract the height and width of image that this model was trained with
		self.feed_height = loaded_dict_enc['height']
		self.feed_width = loaded_dict_enc['width']
		filtered_dict_enc = {k: v for k, v in loaded_dict_enc.items() if k in self.encoder.state_dict()}
		self.encoder.load_state_dict(filtered_dict_enc)
		self.encoder.to(self.device)
		self.encoder.eval()

		#print("   Loading pretrained decoder")
		self.depth_decoder = networks.DepthDecoder(
			num_ch_enc=self.encoder.num_ch_enc, scales=range(4))

		loaded_dict = torch.load(depth_decoder_path, map_location=self.device)
		self.depth_decoder.load_state_dict(loaded_dict)

		self.depth_decoder.to(self.device)
		self.depth_decoder.eval()

	def estimate(self,img,*,metric_depth=True,depth_multiplier=1.0):
		'''
		Run estimation on PIL image. Returns depth map.
		Code mostly from monodepth2/test_simple.py
		'''
		if metric_depth and "stereo" not in self._model_name:
			print("Warning: The --pred_metric_depth flag only makes sense for stereo-trained KITTI "
				"models. For mono-trained models, output depths will not in metric space.")
			sys.exit(1)

		with torch.no_grad():
			# Load image and preprocess
			input_image = img
			original_width, original_height = input_image.size
			input_image = input_image.resize((self.feed_width, self.feed_height), pil.LANCZOS)
			input_image = transforms.ToTensor()(input_image).unsqueeze(0)

			# PREDICTION
			input_image = input_image.to(self.device)
			features = self.encoder(input_image)
			outputs = self.depth_decoder(features)

			disp = outputs[("disp", 0)]

			# Saving numpy file
			scaled_disp, depth = disp_to_depth(disp, 0.1, 100)
			depth_data=depth.cpu().numpy()
			if metric_depth:
				depth_data = STEREO_SCALE_FACTOR * depth_data * depth_multiplier

		# 'unpack' twice since depth is [1][1][192][640]
		assert len(depth_data)==1
		depth_data=depth_data[0]

		assert len(depth_data)==1
		depth_data=depth_data[0]

		return depth_data

# Just initialize a global one.
'''
_de=_DepthEstimator()
def estimate_depth(img,depth_multiplier=1.0):
	return _de.estimate(img,depth_multiplier=depth_multiplier)
'''
if __name__=="__main__":
	# Testing code.
	import visualizations
	src_img=pil.open("testimg.png")
	dat=estimate_depth(src_img)
	vis=visualizations.visualize_matrix(dat)
	vis.show()



