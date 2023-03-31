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
`python3 main.py`
