#!/bin/bash

# Script to download required models for PassLLM

echo "Setting up models for PassLLM..."

# Create .model directory if it doesn't exist
mkdir -p .model

# Download Qwen2.5-0.5B-Instruct
echo "Downloading Qwen2.5-0.5B-Instruct..."
if [ ! -d ".model/Qwen2.5-0.5B-Instruct" ]; then
    cd .model
    git clone https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
    cd ..
    echo "Qwen2.5-0.5B-Instruct downloaded successfully"
else
    echo "Qwen2.5-0.5B-Instruct already exists"
fi

# Download Mistral-7B-v0.1 (optional, for larger experiments)
echo "Downloading Mistral-7B-v0.1..."
if [ ! -d ".model/Mistral-7B-v0.1" ]; then
    cd .model
    git clone https://huggingface.co/mistralai/Mistral-7B-v0.1
    cd ..
    echo "Mistral-7B-v0.1 downloaded successfully"
else
    echo "Mistral-7B-v0.1 already exists"
fi

echo "Model setup complete!"
