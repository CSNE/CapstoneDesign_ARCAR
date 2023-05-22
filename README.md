# Capstone Design / ARCAR

## Installation
Tested OS: Archlinux / Ubuntu 20.04 / Windows 10  
Tested compute device: CPU / CUDA (single-GPU)
#### Python
Tested on Python `3.10` - some required packages are not yet available on `3.11`.  
Using `conda` is recommended:  
`conda create -n arcar python=3.10`  
`conda activate arcar`  
#### PyTorch
Please follow the instructions on the PyTorch website:  
https://pytorch.org/get-started/locally  
#### Other dependencies (Conda or PIP)
Conda: `conda install matplotlib opencv scikit-image tensorboardX pyserial`  
PIP: `pip3 install matplotlib opencv-python scikit-image tensorboardX pyserial`  
#### Other dependencies (PIP only)
`pip install ultralytics timm==0.5.4 pynmea2`
#### CUDA
Only required when using `--cuda` options.  
On Windows, install the latest NVIDIA Drivers, then install CUDA runtime: `conda install cuda`  
On Linux, refer to your distribution's documentation.
#### FFMPEG
Only required for video input.  
`apt install ffmpeg`  
On Windows, download a precompiled `ffmpeg` binary and put it in `PATH` somewhere.
#### Get code
`git clone --recurse-submodules https://github.com/CSNE/CapstoneDesign_ARCAR.git`  
Note: `--recurse-submodules` is required, or it won't pull in the MonoDepth submodule.

## Run
`python3 main.py [args]`  
Open `http://localhost:28301/main.html` with a browser to view AR content.  
Argument list (`python3 main.py --help` may be more accurate):  
- `--source` `-src` : Required. Select the frame source. 
    - `webcam` : Capture webcam.
    - `webcam_stereo` : Capture two webcams, for stereo depth.
    - `image` : Read image file.
    - `image_stereo` : Read two image files, for stereo depth.
    - `stereo_playback`: Read capture directory created by `stereo_capture.py`
    - `video` : Read video file.
    - `screenshot` : Capture desktop.
- `--debug-output` `-do` : Select how to display debug information.
    - `tk` : Outputs to a `tkinter` GUI.
    - `web` : Starts a web server. Go to `http://localhost:28301/debug.html` to view results.
    - `file` : Outputs to JPG files under `out/` directory.
    - `nothing` : Don't output anything. Default.
- `--webcam-number` `-wc` : For `webcam` source, you can set the webcam number here. If not, defaults to 0. (On linux, run `v4l2-ctl --list-devices` to get the device number.)
- `--webcam-left` `-wl` / `--webcam-right` `-wr` : For `webcam_stereo` source. Self-explanatory.
- `--input-file` `-i` : For `image` and `video` and `stereo_playback` sources, you need to supply the file path here.
- `--image-left` `-il` / `--image-right` `-ir` : For `image_stereo` source. Self-explanatory. If only one is given, the program will try to infer the other pair's name.  
- `--video-speed` `-vs` : For `video` source, you can supply a video speed multiplier here. For example, `-vs 0.5` will play the video at half speed.
- `--screenshot-region` `-sr` : For `screenshot` source, you can set the capture region. If not specified, captures the whole desktop.
- `--cuda` `-cuda` : Use GPU acceleration. Only uses CPU by default.
- `--stereo-solvers` `-ss` : Select (multiple) stereo solvers. Comma-separated. Default is `opencv,monodepth`.
    - `monodepth` : MonoDepth2 (Monocular)
    - `opencv` : OpenCV StereoBM (Stereo)
    - `psm` : PSMNet (Stereo)
    - `igev` : IGEV (Stereo)
- `--solve-resize` `-srz` : Stereo image dimension to resize before feeding it to the stereo solver algorithms(Except OpenCV). For example `-srz 640x480` will resize each stereo image pair to no bigger than 640x480 (preserving aspect ratio, and no upscaling) before being input to the algorithms. Smaller sizes are faster but less accurate. Default `480x320`. Note that PSMNet errors out if this is too small.  
- `--single-frame` `-sf` : Exit after processing a single frame. Tip: use in combination with `-o file` for debugging.
- `--verbose` `-v` : Verbose logging. Repeat for even more verbosity. (`-vvv`)
- `--pointcloud` `-pc` : Enable "point-cloud" visuals. Bad for performance.
- `--detect-walls` `-dw` : Enable wall detection.
- `--visualize-wall-detections` `-vwd` : Visualize wall detection algorithm in the debug page.  
- `--flatten-segments` `-fs` : Make segments flat.

Examples:  
`python3 main.py --source=image -i testimg.png --single-frame`  
`python3 main.py --source video --input-file video.mp4 --debug_output tk`  
`python3 main.py -src webcam -wc 2 -o web`  
`python3 main.py --source=webcam_stereo --webcam-left 6 --webcam-right 8 --debug_output web --stereo-solvers=psm,igev --solve-resize=640x480`
`python3 main.py --source=screenshot --screenshot-region=1920,0,3840,1080`  

## Structure
`samples/`: Sample stereo images, some captured by us, some downloaded.  
`IGEV_Stereo/`: IGEV code, copy of the [original git repo](https://github.com/gangweiX/IGEV). Some modifications made, to make it able to run on a CPU.  
`monodepth2/`: MonoDepth2 code, submodule from the [original git repo](https://github.com/nianticlabs/monodepth2).  
`PSMNet/`: PSMNet code, copy of the [original git repo](https://github.com/JiaRenChang/PSMNet). Some modifications made, to make it able to run on a CPU.  

