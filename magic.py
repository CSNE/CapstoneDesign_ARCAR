# https://en.wikipedia.org/wiki/Magic_number_(programming)

class visuals:
	debug_pointcloud_count=1000
	mainpage_pointcloud_count=5000
	font_size=36
	
	text3d_segment_size=0.04
	text3d_segment_centerY=True
	
	text3d_building_size=0.07
	
	depthvis_absolute_clip=False
	
	visual2d_fontsize=24
	
class yolo:
	run_official_pretrained_model=True
	
class walls:
	# Scale the depth map down before running wall detection?
	do_prescale=True
	prescale_depth=(240,160)
	
	# How much area of the screen the wall should occupy for it to be valid
	match_threshold=0.05
	
	threaded=True
	thread_count=4
	
	# Blur when choking
	choke_use_gaussian=False
	choke_gaussian_sdev=5
	choke_box_size=7
	choke_thresh=0.9
	
	# How many samples to... sample
	random_samples=100
	# Radius for calculating derivative
	derivative_radius=10
	# How much to blur the depth map
	blur_sdev=5
	# How close the depths should be for it to be a valid in-wall point
	inwall_thresh_ratio=0.05
	# Walls farther than this will be discarded
	max_distance=30
	# Normal vectors with dot products bigger than this will
	# be considered the same.
	nvec_dot_thresh=0.7

class system:
	tk_initialize_wait=0.5
	
	
class web:
	server_port=28301
	
	
class monodepth:
	# Multiplier for depth estimate
	multiplier=0.3
class opencv:
	# Multiplier for depth estimate
	multiplier=700
	# StereoBM params
	numDisparities=32
	blockSize=15
class psm:
	# Multiplier for depth estimate
	multiplier=40
class igev:
	# Multiplier for depth estimate
	multiplier=20
	
class segdepth:
	# if less than this ratio of pixels have valid depth data,
	# the segdepth will be rejected
	ratio_threshold=0.1

class camera:
	# Camera parameters
	reference_distance=1.96
	reference_width=1.92
	aspect_hv=4/3

class gps:
	building_distance_cutoff=300
