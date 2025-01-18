#!/bin/bash

# Install CUDA requirements
sudo apt update
sudo apt install -y nvidia-cuda-toolkit nvidia-cuda-toolkit-gcc

# Clone llama.cpp if you haven't already
# If you have it already, just cd into the directory
cd .venv
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Clean previous build
rm -rf build

# Create build directory and build with CUDA
mkdir build
cd build
cmake .. -DGGML_CUDA=ON
cmake --build . --config Release -j4

# Make server globally accessible (optional)
sudo ln -sf "$(pwd)/bin/llama-server" /usr/local/bin/llama-server

echo "Build complete! You can verify CUDA support by running:"
echo "llama-server --help | grep CUDA"