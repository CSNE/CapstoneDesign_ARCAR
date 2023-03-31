# Capstone Design / ARCAR

## Installation
#### PyTorch
https://pytorch.org/get-started/locally  
CPU: `pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu`  
CUDA: `pip3 install torch torchvision`
#### Other dependencies
`pip3 install matplotlib opencv scikit-image`  
`pip3 install tensorboardX`
#### YOLOv8
`pip3 install ultralytics`
#### FFMPEG
`apt install ffmpeg`
#### Get code
`git clone --recurse-submodules https://github.com/CSNE/CapstoneDesign_ARCAR.git`

## Check install
#### Monodepth2
`cd monodepth2`  
`python3 test_simple.py --image_path assets/test_image.jpg --model_name mono+stereo_640x192`

#### YOLOv8
`yolo detect predict model=yolov8n.pt source='https://ultralytics.com/images/bus.jpg' show=True`

## Run
`main.py --source SOURCE --input-file INPUT_FILE --webcam-number WEBCAM_NUMBER --output OUTPUT`  
`--source` `-src`: select the frame source. `webcam`, `image`, or `video`  
`--input-file` `-i`: for `image` and `video` sources, you need to supply the file path here.  
`--webcam-number` `-wc`: for `webcam` source, you can set the webcam number here. If not, defaults to 0.  
`--output` `-o`: Select how to visualize the program output.  
- `tk`: Outputs to a `tkinter` GUI.
- `web`: Starts a web server. Go to `http://localhost:28301` to view results.
- `file`: outputs to a JPG file.
- `nothing`: Don't output anything.

Examples:  
`python3 main.py --source image -i testimg.png --output nothing`  
`python3 main.py --source video --input-file video.mp4 --output tk`  
`python3 main.py -src webcam -wc 2 -o web`  
