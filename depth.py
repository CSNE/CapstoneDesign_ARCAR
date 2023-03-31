# Code mostly copied from monodepth2/test_simple.py

import os
import sys
import glob
import argparse
import numpy as np
import PIL.Image as pil
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt

mpl.use('TKAgg')

import torch
from torchvision import transforms, datasets


sys.path.append("monodepth2")

import networks
from layers import disp_to_depth
from utils import download_model_if_doesnt_exist
from evaluate_depth import STEREO_SCALE_FACTOR

import time
import io

class DepthEstimator:
	def __init__(self,model_name="mono+stereo_640x192"):
		self._model_name=model_name
		self.net_setup()
	def net_setup(self):
		print("Setup...")
		if torch.cuda.is_available() and not args.no_cuda:
			self.device = torch.device("cuda")
		else:
			self.device = torch.device("cpu")

		download_model_if_doesnt_exist(self._model_name)
		model_path = os.path.join("models", self._model_name)
		print("-> Loading model from ", model_path)
		encoder_path = os.path.join(model_path, "encoder.pth")
		depth_decoder_path = os.path.join(model_path, "depth.pth")

		# LOADING PRETRAINED MODEL
		print("   Loading pretrained encoder")
		self.encoder = networks.ResnetEncoder(18, False)
		loaded_dict_enc = torch.load(encoder_path, map_location=self.device)

		# extract the height and width of image that this model was trained with
		self.feed_height = loaded_dict_enc['height']
		self.feed_width = loaded_dict_enc['width']
		filtered_dict_enc = {k: v for k, v in loaded_dict_enc.items() if k in self.encoder.state_dict()}
		self.encoder.load_state_dict(filtered_dict_enc)
		self.encoder.to(self.device)
		self.encoder.eval()

		print("   Loading pretrained decoder")
		self.depth_decoder = networks.DepthDecoder(
			num_ch_enc=self.encoder.num_ch_enc, scales=range(4))

		loaded_dict = torch.load(depth_decoder_path, map_location=self.device)
		self.depth_decoder.load_state_dict(loaded_dict)

		self.depth_decoder.to(self.device)
		self.depth_decoder.eval()

	def estimate(self,img,metric_depth=True):
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
				depth_data = STEREO_SCALE_FACTOR * depth_data

		# 'unpack' twice since depth is [1][1][192][640]
		assert len(depth_data)==1
		depth_data=depth_data[0]

		assert len(depth_data)==1
		depth_data=depth_data[0]

		return depth_data


# aspect 0.5 -> width twice of height
def visualize_depth(arr,target_aspect=(9/16)):

	array_aspect=arr.shape[0]/arr.shape[1]

	fig = plt.figure()
	cmap=mpl.colormaps.get_cmap("plasma").reversed()
	ax = fig.add_subplot()
	ax.set_title('Distance')
	plt.imshow(arr,cmap=cmap)
	ax.set_aspect(target_aspect/array_aspect) #height=N*width
	plt.colorbar(orientation='vertical')

	bio=io.BytesIO()
	plt.savefig(bio)
	bio.seek(0)
	return pil.open(bio).convert("RGB")

if __name__=="__main__":
	t1=time.time()
	src_img=pil.open("testimg.png")
	t2=time.time()
	de=DepthEstimator("mono+stereo_640x192")
	t3=time.time()
	dat=de.estimate(src_img)
	t4=time.time()
	vis=visualize_depth(dat)
	t5=time.time()
	vis.save("out.png")
	t6=time.time()

	print(dat,dat.shape)
	print(vis.height,vis.width)

	print("Image open",round((t2-t1)*1000),"ms")
	print("Net setup",round((t3-t2)*1000),"ms")
	print("Estimate",round((t4-t3)*1000),"ms")
	print("Visualize",round((t5-t4)*1000),"ms")
	print("Save image",round((t6-t5)*1000),"ms")



