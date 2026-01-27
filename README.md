# NVHTop

A `htop`-like utility for NVIDIA GPUs implemented in Python using `Textual` and `pynvml`.

## Features

- **Real-time GPU Stats**: View utilization, memory usage, temperature, fan speed, and power draw for all NVIDIA GPUs.
- **Process List**: Live list of processes running on the GPU with memory usage.
- **Modern TUI**: Built with Textual for a premium terminal user interface experience.

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the utility:

```bash
python main.py
```

Or using the provided script:

```bash
./run.sh
```

## Shortcuts

- `q`: Quit the application.
- `k`: Kill the selected process (opens confirmation dialog).

## Requirements

- NVIDIA Driver installed
- Python 3.8+
