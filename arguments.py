import argparse
import sys

import kinect

# Arguments Definition
_ap=argparse.ArgumentParser(description="ARCAR Python Program")

# Required
_ap.add_argument(
	"--source","-src",
	choices=["webcam","image","video","screenshot","kinect"],
	required=True)
_ap.add_argument(
	"--output","-o",
	choices=["tk","web","file","nothing"],
	required=True)

# Per-Input
_ap.add_argument(
	"--webcam-number","-wc",
	type=int,
	default=0)
_ap.add_argument(
	"--input-file","-i")
_ap.add_argument(
	"--video-speed","-vs",
	type=float,
	default=1.0)
_ap.add_argument(
	"--screenshot-region","-sr")
_ap.add_argument(
	"--kinect-depth","-kd",
	choices=list(kinect.DepthMode.keys()),
	default="NFOV_UNBINNED")
_ap.add_argument(
	"--kinect-rgb","-kr",
	choices=list(kinect.ColorResolution.keys()),
	default="RES_720P")
_ap.add_argument(
	"--kinect-fps","-kf",
	choices=list(kinect.FPS.keys()),
	default="15")

# Optional
_ap.add_argument(
	"--single-frame","-sf",
	action="store_true")
_ap.add_argument(
	'--verbose', '-v',
	action='count',
	default=0)


# Arguments Parsing
_args=_ap.parse_args()

source=_args.source
output=_args.output

wc=_args.webcam_number
vs=_args.video_speed

if source in ("image","video"):
	if "input_file" not in _args:
		print("For image or video input, you need to supply the input file.")
		print("( --input-file=FILE or -f FILE )")
		sys.exit(1)
	else:
		infile=_args.input_file

if _args.screenshot_region is not None:
	spl=_args.screenshot_region.split(",")
	try:
		if len(spl) != 4:
			raise ValueError
		sr=[int(i) for i in spl]
	except ValueError:
		print("--screenshot-region must be 4 integers, separated by commas without spaces")
		sys.exit(1)
else:
	sr=None

kinect_depth=kinect.DepthMode[_args.kinect_depth]
kinect_rgb=kinect.ColorResolution[_args.kinect_rgb]
kinect_fps=kinect.FPS[_args.kinect_fps]

singleframe=_args.single_frame
verblevel=_args.verbose
