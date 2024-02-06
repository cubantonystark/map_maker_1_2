# MapMaker.

#### Installation

## Base Requirements

- Windos Subsystem for Linux (WSL), Ubuntu 22.04<br>
- NVIDIA RTX20, RTX30 or RTX40 GPU with at least 8 Gb VRAM
- At least 16Gb RAM</ul>

## Installation

Download Anaconda from https://www.anaconda.com/download#downloads and install, then type the commands listed below.

```shell
conda create -n nksr python=3.10
conda activate nksr
conda install -c "nvidia/label/cuda-11.8.0" cuda-toolkit
conda install pytorch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c pytorch -c nvidia
pip install torch-scatter pyntcloud plyfile pymeshlab pillow utm
export TORCH_VERSION=2.0.0
export CUDA_VERSION=cu118
pip install -U nksr -f https://nksr.huangjh.tech/whl/torch-${TORCH_VERSION}+${CUDA_VERSION}.html
pip install python-pycg[full] -f https://pycg.s3.ap-northeast-1.amazonaws.com/packages/index.html
git clone https://github.com/cubantonystark/fsrpc_mapmapker.git
```

