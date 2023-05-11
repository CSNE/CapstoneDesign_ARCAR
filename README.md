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
#### Get code
`git clone --recurse-submodules https://github.com/CSNE/CapstoneDesign_ARCAR.git`

## Run
`python3 main.py [args]`  
- `--source` `-src` : Required. Select the frame source. 
    - `webcam`: Capture webcam.
    - `webcam_stereo`: Capture two webcams, for stereo depth.
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
- `--stereo-solvers` `-ss` : Select (multiple) stereo solvers. Comma-separated. Default is `opencv,monodepth`.
    - `monodepth`: MonoDepth2 (Monocular)
    - `opencv`: OpenCV StereoBM (Stereo)
    - `psm`: PSMNet (Stereo)
    - `igev`: IGEV (Stereo)
- `--single-frame` `-sf` : Exit after processing a single frame. Use in combination with `-o file` for debugging.
- `--verbose` `-v` : Verbose logging. Repeat for even more verbosity. (`-vvv`)

Examples:  
`python3 main.py --source=image -i testimg.png --single-frame --output file`  
`python3 main.py --source video --input-file video.mp4 --output tk`  
`python3 main.py -src webcam -wc 2 -o web`  
`python3 main.py --source=webcam_stereo --webcam-left 6 --webcam-right 8 --output web --stereo-solvers=psm,igev`
`python3 main.py --source=screenshot --screenshot-region=1920,0,3840,1080 --output=web`  

## Structure
`captures/`: Manually captured stereo images, by us.  
`IGEV_Stereo/`: IGEV code, copy of the [original git repo](https://github.com/gangweiX/IGEV). Some modifications made, to make it able to run on a CPU.  
`monodepth2/`: MonoDepth2 code, submodule from the [original git repo](https://github.com/nianticlabs/monodepth2).  
`PSMNet/`: PSMNet code, copy of the [original git repo](https://github.com/JiaRenChang/PSMNet). Some modifications made, to make it able to run on a CPU.  
`test_images/`: Test stereo images, downloaded.  
