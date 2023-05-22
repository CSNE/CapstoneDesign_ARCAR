import argparse
import sys
import os.path

# Arguments Definition
_ap=argparse.ArgumentParser(description="ARCAR Python Program")


# Required
_ap.add_argument(
	"--source","-src",
	choices=[
		"webcam","webcam_stereo",
		"image","image_stereo","stereo_playback",
		"video","screenshot"],
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


# Optional
_ap.add_argument(
	"--debug-output","-do",
	choices=["tk","web","file","nothing"],
	default="nothing")
_ap.add_argument(
	"--cuda","-cuda",
	action="store_true")
_ap.add_argument(
	"--stereo-solvers","-ss",
	default="opencv,monodepth")
_ap.add_argument(
	"--solve-resize","-srz",
	default="480x320")
_ap.add_argument(
	"--single-frame","-sf",
	action="store_true")
_ap.add_argument(
	'--verbose', '-v',
	action='count',
	default=0)
_ap.add_argument(
	"--pointcloud","-pc",
	action="store_true")
_ap.add_argument(
	"--detect-walls","-dw",
	action="store_true")
_ap.add_argument(
	"--visualize-wall-detections","-vwd",
	action="store_true")
_ap.add_argument(
	"--flatten-segments","-fs",
	action="store_true")
_ap.add_argument(
	"--skip-matrix-visuals","-smv",
	action="store_true")

_ap.add_argument(
	"--gps-device","-gps")
_ap.add_argument(
	"--gps-playback","-gpb")
_ap.add_argument(
	"--gps-look-offset","-glo",
	default=0,type=float)

_ap.add_argument(
	"--stereo-distance","-sd",
	default=16,type=float)

# Arguments Parsing
_args=_ap.parse_args()

source=_args.source
debug_output=_args.debug_output
pointcloud=_args.pointcloud
detect_walls=_args.detect_walls
do_wall_visual= _args.visualize_wall_detections
stereo_multiplier=_args.stereo_distance/16


gps_dev=_args.gps_device
gps_playback=_args.gps_playback
use_gps = (gps_dev is not None) or (gps_playback is not None)
gps_look_offset = _args.gps_look_offset

if do_wall_visual and (not detect_walls):
	print("We can't visualize walls if wall detection is turned off!")
	print("  (enable with --detect-walls)")
	sys.exit(1)
visualize_depth_matrix = not _args.skip_matrix_visuals
flatten_segments=_args.flatten_segments

wc=_args.webcam_number
vs=_args.video_speed

_valid_ss=["opencv","psm","monodepth","igev"]
stereo_solvers={i:False for i in _valid_ss}
for ss in _args.stereo_solvers.split(","):
	ss=ss.strip().lower()
	if ss not in _valid_ss:
		print(F"{ss} not a valid stereo solver (must be one of {_valid_ss})")
		sys.exit(1)
	stereo_solvers[ss]=True


if source in ("image","video","stereo_playback"):
	if _args.input_file is None:
		print("For image or video or stereo_playback input, you need to supply the input file or directory.")
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

def l2r(filepath,r2l=False):
	fp,ex=os.path.splitext(filepath)


	if r2l:
		postfix_from,postfix_to,conversion="_R","_L","R->L"
	else:
		postfix_from,postfix_to,conversion="_L","_R","L->R"
	print("Only one stereo image provided.")
	print(F"Inferring stereo image pair of {filepath} ({conversion})")
	if fp.endswith(postfix_from):
		fp=fp[:-2]+postfix_to
	else:
		print(F"  Filename does not end with {postfix_from}!")
		return None

	res=fp+ex

	if not os.path.exists(res):
		print(F"Inferred stereo image ({res}) not present!")

	print(F"Inferred & found stereo image {res}")
	return res


if source in ("image_stereo",):
	if (_args.input_left is None) and (_args.input_right is None):
		print("For image_stereo source, you need to supply both files.")
		print("( --input-left FILE --input-right FILE )")
		sys.exit(1)
	elif _args.input_left is None:
		infileR=_args.input_right
		infileL=l2r(infileR,r2l=True)
		if infileL is None:
			sys.exit(1)
	elif _args.input_right is None:
		infileL=_args.input_left
		infileR=l2r(infileL,r2l=False)
		if infileR is None:
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

singleframe=_args.single_frame
verblevel=_args.verbose

cuda=_args.cuda

try:
	_w,_h=_args.solve_resize.lower().split("x")
	solve_resize=(int(_w),int(_h))
	#print(solve_resize)
except ValueError:
	print("--solve-resize must be WxH, both integers. ex) 640x480")
	sys.exit(1)
