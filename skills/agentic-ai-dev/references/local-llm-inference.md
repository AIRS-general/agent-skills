# Prepare LLMs for local inference with llama.cpp

## Overview

```text
HF safetensors repo
        ↓
convert_hf_to_gguf.py
        ↓
gemma4.gguf
        ↓
quantize → Q4_K_M
        ↓
gemma4-q4.gguf
```

## 0. Setup

### Download llama.cpp

```zsh
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

### Install dependencies

```zsh
uv sync
```

### Install `huggingface_hub` (if needed)

```zsh
uv add huggingface_hub
```

### Project structure

```zsh
llama.cpp/
models/
├── download/
├── gguf/
README.md # (this file)
```

## 1. Download model from Hugging Face

```zsh
cd models
hf download google/gemma-4-31B-it --local-dir download/gemma-4-31B-it
```

## 2. Convert to GGUF format

Need to include an `mmproj` file for multimodal models.

```zsh
cd llama.cpp
uv run python convert_hf_to_gguf.py ../models/download/gemma-4-31B-it \
  --outfile ../models/gguf/gemma-4-31B-it/gemma-4-31B-it.gguf \
  --outtype f16 \
  --mmproj <path-to-mmproj>
```

This converts the model to `.gguf`. For multimodal models, an mmproj file is also produced.

## 3. Quantize to Q4_K_M format

Only the model file needs quantization. The mmproj file is not needed.

```zsh
cd llama.cpp
./build/bin/llama-quantize \
  ../models/gguf/gemma-4-31B-it/gemma-4-31B-it.gguf \
  ../models/gguf/gemma-4-31B-it/gemma-4-31B-it-q4.gguf \
  Q4_K_M
```

## 4. Serve the model using `llama.cpp` server

Web interface: `http://localhost:8080`.
OpenAI-compatible endpoint: `http://localhost:8080/v1/chat/completions`

```zsh
./build/bin/llama-server \
  -m ../models/gguf/gemma-4-31B-it/gemma-4-31B-it-q4.gguf \
  --mmproj ../models/gguf/gemma-4-31B-it/gemma-4-31B-it-mmproj.gguf \
  -ngl 999 \
  -c 32768 \
  -fa on \
  --host 0.0.0.0 \
  --port 8080
```

- `-ngl`: offload all possible layers to Metal GPU
- `-c`: context window size. 8K default (8192). 32K (32768), 256K (262144)
- `-m`: model path
- `-fa`: Flash Attention (faster/lower memory)
- `--host`: host address
- `--port`: port number
- `--mmproj`: model projection path, for multimodal

### `gemma-4-26B-A4B-it`

```zsh
./build/bin/llama-server \
  -m ../models/gguf/gemma-4-26B-A4B-it/gemma-4-26B-A4B-it-q4.gguf \
  --mmproj ../models/gguf/gemma-4-26B-A4B-it/gemma-4-26B-A4B-it-mmproj.gguf \
  -ngl 999 \
  -c 32768 \
  -fa on
```
