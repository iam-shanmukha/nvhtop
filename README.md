# NVHTop-TUI

A `htop`-like utility for NVIDIA GPUs implemented in Python using `Textual` and `pynvml`.

## Features

- **Real-time GPU Stats**: View utilization, memory usage, temperature, fan speed, and power draw for all NVIDIA GPUs.
- **Process List**: Live list of processes running on the GPU with memory usage.
- **Modern TUI**: Built with Textual for a premium terminal user interface experience.

## Installation

You can install `nvhtop-tui` directly from PyPI:

```bash
pip install nvhtop-tui
```

### Manual Installation (Development)

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

If installed via pip:

```bash
nvhtop-tui
```

If running from source:

```bash
python main.py
```

## Shortcuts

- `q`: Quit the application.
- `k`: Kill the selected process (opens confirmation dialog).

## Requirements

- NVIDIA Driver installed
- Python 3.8+
