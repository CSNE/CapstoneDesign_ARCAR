import argparse
import sys

# Arguments Definition
_ap=argparse.ArgumentParser(description="ARCAR Python Program")

# Required
_ap.add_argument(
	"--source","-src",
	choices=["webcam","webcam_stereo",
		  "image","image_stereo","video","screenshot",
		  "kinect","kinectcapture"],
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
	"--webcam-left","-wl",
	type=int)
_ap.add_argument(
	"--webcam-right","-wr",
	type=int)
_ap.add_argument(
	"--input-file","-i")
_ap.add_argument(
	"--input-left","-il")
_ap.add_argument(
	"--input-right","-ir")
_ap.add_argument(
	"--video-speed","-vs",
	type=float,
	default=1.0)
_ap.add_argument(
	"--screenshot-region","-sr")
_ap.add_argument(
	"--kinect-depth","-kd",
	choices=[
		'NFOV_2X2BINNED',"nb",
		'NFOV_UNBINNED',"nu",
		'WFOV_2X2BINNED',"wb",
		'WFOV_UNBINNED',"wu"],
	default="NFOV_UNBINNED")
_ap.add_argument(
	"--kinect-rgb","-kr",
	choices=[
		'RES_720P',"720",
		'RES_1080P',"1080",
		'RES_1440P',"1440",
		'RES_1536P',"1536",
		'RES_2160P',"2160",
		'RES_3072P',"3072"],
	default="RES_720P")
_ap.add_argument(
	"--kinect-fps","-kf",
	choices=["5","15","30"],
	default="15")
_ap.add_argument(
	"--stereo-solver","-ss",
	choices=["opencv","psm"],
	default="opencv")

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

stereo_solver=_args.stereo_solver

if source in ("image","video","kinectcapture"):
	if _args.input_file is None:
		print("For image or video or kinectcapture input, you need to supply the input file or directory.")
		print("( --input-file=FILE or -f FILE )")
		sys.exit(1)
	else:
		infile=_args.input_file

if source in ("webcam_stereo",):
	if (_args.webcam_left is None) or (_args.webcam_right is None):
		print("For webcam_stereo source, you need to supply both webcam's number.")
		print("( --webcam-left N --webcam-left N )")
		sys.exit(1)
	else:
		wcL=_args.webcam_left
		wcR=_args.webcam_right

if source in ("image_stereo",):
	if (_args.input_left is None) or (_args.input_right is None):
		print("For image_stereo source, you need to supply both files.")
		print("( --input-left FILE --input-right FILE )")
		sys.exit(1)
	else:
		infileL=_args.input_left
		infileR=_args.input_right

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

kinect_depth=_args.kinect_depth
kinect_rgb=_args.kinect_rgb
kinect_fps=_args.kinect_fps

singleframe=_args.single_frame
verblevel=_args.verbose
