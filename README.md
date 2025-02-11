# N-Body Simulation

## Overview
This project is an interactive N-body simulation using OpenGL. It simulates the gravitational interactions of celestial bodies in three different modes:
1. **Solar System Mode** (predefined celestial data)
2. **Random Mode** (N randomly placed bodies)
3. **Random-Star Mode** (N bodies with a central star)

## Installation
### **Prerequisites**
Ensure you have Python 3.x installed. Install dependencies with:

```bash
pip install -r requirements.txt
```

### **Usage**
Run the simulation using:

```bash
python N-body.py
```

Modes:
- **Solar system mode** (default):
  ```bash
  python N-body.py
  ```
- **Random mode with N bodies**:
  ```bash
  python N-body.py random 10
  ```
- **Random-star mode with N bodies and a central star**:
  ```bash
  python N-body.py random-star 10
  ```

### **Keyboard Controls**
| Key  | Action |
|------|--------|
| `X`  | Exit simulation |
| `I/O` | Rotate up/down |
| `J/K` | Rotate left/right |
| `N/M` | Zoom in/out |
| `W/S` | Move up/down |
| `A/D` | Move left/right |
| `E/Q` | Scale simulation up/down |
| `1` | Toggle orbit trails |
| `2` | Toggle body display |
| `3` | Toggle short orbit mode |
| `=`/`-` | Increase/Decrease orbit length |
| `[`/`]` | Adjust simulation speed |
| `R/T` | Adjust planet size |
| `SPACE` | Pause/unpause |

### **File Structure**
```
N-Body-Simulation/
│── config/                  # Configuration files
│── data/                    # Data files (e.g., Solar_system.csv)
│── images/                  # Texture files
│── src/                     # Main source code
│   ├── N-body.py            # Main simulation script
│── output/                  # Generated CSV files (simulation logs)
│── requirements.txt         # Dependencies
│── README.md                # This file
```

### **Dependencies**
The required Python packages are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

### **Troubleshooting**
If you encounter issues running the simulation, consider the following:

#### **1. OpenGL Not Found**
If you get errors related to missing OpenGL dependencies:
- **macOS**:  
  ```bash
  brew install freeglut
  ```
- **Linux**:  
  ```bash
  sudo apt-get install freeglut3-dev
  ```
- **Windows**:  
  Install OpenGL libraries manually or use a package manager like `choco install freeglut`.

#### **2. Permission Errors on macOS (`brew link freeglut` fails)**
If you see an error like:
```bash
Error: Could not symlink lib/cmake/FreeGLUT
/usr/local/lib/cmake is not writable.
```
Try:
```bash
sudo chown -R $(whoami) /usr/local/lib/cmake
brew link --overwrite freeglut
```

### **Future Improvements**
Note that I have moved on from this project and don't see myself returning.
- [ ] Online interface (VCN)
- [ ] Mouse controls for acceleration and velocity with friction deceleration
- [ ] Record closest distances between certain bodies
- [ ] Optimize memory usage by combining close calculations with collision checks
- [ ] Make time a global attribute instead of a body attribute
- [ ] Optimize performance for larger body counts using tree methods
- [ ] Implement more accurate physics models
- [ ] Improve UI for configuring simulation parameters

