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

## Verify install
Some commands you can run to make sure the dependencies are installed correctly.
#### Monodepth2
`cd monodepth2`  
`python3 test_simple.py --image_path assets/test_image.jpg --model_name mono+stereo_640x192`

#### YOLOv8
`yolo detect predict model=yolov8n.pt source='https://ultralytics.com/images/bus.jpg' show=True`

## Run
`python3 main.py [args]`  
- `--source` `-src` : Required. Select the frame source. `webcam`, `kinect`, `image`, `video`, or `screenshot`  
- `--input-file` `-i` : for `image` and `video` sources, you need to supply the file path here.  
- `--video-speed` `-vs` : for `video` source, you can supply a video speed multiplier here. For example, `-vs 0.5` will play the video at half speed.  
- `--webcam-number` `-wc` : for `webcam` source, you can set the webcam number here. If not, defaults to 0.  
- `--screenshot-region` `-sr` : for `screenshot` source, you can set the capture region. If not specified, captures the whole desktop.  
- `--output` `-o` : Required. Select how to visualize the program output.  
    - `tk`: Outputs to a `tkinter` GUI.
    - `web`: Starts a web server. Go to `http://localhost:28301` to view results.
    - `file`: outputs to a JPG file.
    - `nothing`: Don't output anything.
- `--single-frame` `-sf` : Exit after processing a single frame. Use in combination with `-o file` for debugging.  

Examples:  
`python3 main.py --source=image -i testimg.png --single-frame --output file`  
`python3 main.py --source video --input-file video.mp4 --output tk`  
`python3 main.py -src webcam -wc 2 -o web`  
`python3 main.py --source=screenshot --screenshot-region=1920,0,3840,1080 --output=web`  
