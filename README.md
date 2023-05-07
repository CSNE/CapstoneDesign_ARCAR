# Capstone Design / ARCAR

## Installation
#### Python
Tested on Python `3.10`. Some required packages below are not available on `3.11`.  
You can install all dependencies directly to system python, but using `conda` might be a good idea.
#### PyTorch
https://pytorch.org/get-started/locally  
CPU: `pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu`  
CUDA: `pip3 install torch torchvision`  
Conda: `conda install pytorch torchvision`
#### Other dependencies
PIP: `pip3 install matplotlib opencv-python scikit-image tensorboardX`  
Conda: `conda install matplotlib opencv scikit-image tensorboardX`  
#### YOLOv8
`pip3 install ultralytics`
#### FFMPEG
Only required for video input.  
`apt install ffmpeg`  
On Windows, download a precompiled `ffmpeg` binary and put it in `PATH` somewhere.
#### Kinect Azure
Only required for Kinect Azure input.  
[Download and install Azure Kinect SDK from Microsoft.](https://github.com/microsoft/Azure-Kinect-Sensor-SDK/blob/develop/docs/usage.md)  
Install python wrapper: `pip install pyk4a`
#### Get code
`git clone --recurse-submodules https://github.com/CSNE/CapstoneDesign_ARCAR.git`

## Run
`python3 main.py [args]`  
- `--source` `-src` : Required. Select the frame source. 
    - `webcam`: Capture webcam.
    - `webcam_stereo`: Capture two webcams, for stereo depth.
    - `kinect`: Capture from Azure Kinect.
    - `kinectcapture`: Read Azure Kinect recording made with `kinect_record.py`
    - `image`: Read image file.
    - `image_stereo`: Read two image files, for stereo depth.
    - `video`: Read video file.
    - `screenshot`: Capture desktop.
- `--output` `-o` : Required. Select how to visualize the program output.
    - `tk`: Outputs to a `tkinter` GUI.
    - `web`: Starts a web server. Go to `http://localhost:28301` to view results.
    - `file`: Outputs to JPG files under `out/` directory.
    - `nothing`: Don't output anything.
- `--webcam-number` `-wc` : For `webcam` source, you can set the webcam number here. If not, defaults to 0. (On linux, run `v4l2-ctl --list-devices` to get the device number.)
- `--webcam-left` `-wl` / `--webcam-right` `-wr` : For `webcam_stereo` source. Self-explanatory.
- `--input-file` `-i` : For `image`, `video`, and `kinectcapture` sources, you need to supply the file path here.
- `--image-left` `-il` / `--image-right` `-ir` : For `image_stereo` source. Self-explanatory.
- `--video-speed` `-vs` : For `video` source, you can supply a video speed multiplier here. For example, `-vs 0.5` will play the video at half speed.
- `--screenshot-region` `-sr` : For `screenshot` source, you can set the capture region. If not specified, captures the whole desktop.
- `--kinect-depth` `-kd` / `--kinect-rgb` `-kr` / `--kinect-fps` `-kf` : For `kinect` source, configure Azure Kinect capture settings. View `--help` for possible values.
- `--stereo-solver` `-ss` : For `_stereo` sources, choose how to calculate the disparity. `opencv`(OpenCV StereoBM, default) or `psm`(PSMNet).
- `--single-frame` `-sf` : Exit after processing a single frame. Use in combination with `-o file` for debugging.
- `--verbose` `-v` : Verbose logging. Repeat for even more verbosity. (`-vvv`)

Examples:  
`python3 main.py --source=image -i testimg.png --single-frame --output file`  
`python3 main.py --source video --input-file video.mp4 --output tk`  
`python3 main.py -src webcam -wc 2 -o web`  
`python3 main.py --source=webcam_stereo --webcam-left 6 --webcam-right 8 --output web --stereo-solver=psm`  
`python3 main.py --source=screenshot --screenshot-region=1920,0,3840,1080 --output=web`  
`python3 main.py --source=kinect --kinect-depth=NFOV_2X2BINNED --kinect-rgb 1080 -kf 5 --output=web`
