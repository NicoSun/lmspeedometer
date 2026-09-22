# lmspeedometer

A lightweight Python utility to benchmark Large Language Models (LLMs) using [LM Studio](https://lmstudio.ai/). It measures **LLM loading speed**, **prompt processing speed** and **token generation speed**, allowing you to evaluate model performance on your specific hardware.

## ✨ Features

- 🚀 **Speed Benchmarking**: Accurately measure LLM load times and tokens per second (TPS).
- 🛠️ **Custom Prompts**: Easily customize benchmark inputs via a simple JSON configuration file.
- 🖥️ **Simple UI**: Select multiple models to run benchmarks sequentially.

## 📋 Prerequisites

- Python 3.8+
- [LM Studio](https://lmstudio.ai/) installed and running

## 🚀 Quick Start

### 1. Installation

Clone the repository and set up your virtual environment:

```bash
# Clone the repo
git clone https://github.com/yourusername/lmspeedometer.git
cd lmspeedometer

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Configuration

1. **Start LM Studio**: Ensure LM Studio is running and set up your desired model runtime/settings
2. **Customize Prompts** (Optional): Edit `benchprompts.json` to use your own test prompts.

---

### 3. Run the Benchmark

1. Activate your virtual environment (if not already active).
2. Run the main script:

```bash
python main.py
```

3. Follow the on-screen prompts to select the models you wish to benchmark.

---

## 🐧 Tips for AMD iGPU Users (Linux)

By default, AMD integrated GPUs on Linux often have a limited Graphics Translation Table (GTT) allocation (typically 50% of system RAM). You can increase this limit to accommodate larger LLMs using kernel parameters.

### Calculate Memory Pages

You need to calculate the number of 4KB memory pages to allocate. Use the following formula:

$$ \text{ttm\_pages} = \frac{\text{Size in GB} \times 1024 \times 1024 \times 1024}{4096} $$

#### Example

To allocate **38 GB** of VRAM:

```bash
38 * 1024 * 1024 * 1024 / 4096 = 9961472
```

### Apply Changes

Run the following commands to update your GRUB kernel parameters:

```bash
sudo grubby --update-kernel=ALL --args='ttm.pages_limit=9961472'
sudo grubby --update-kernel=ALL --args='ttm.page_pool_size=9961472'
```

> **⚠️ Warning:** If your system fails to boot due to an incorrect value, you can recover by editing or deleting the changes in the GRUB menu at startup.
