# Invesalius MPR Viewer
## Environment Settings
### 1. Install Python
[Download](https://www.python.org/downloads/)

### 2. Install Python Packages
```
pip install -r requirements.txt
```

## Start application
### 1. Replace path to dicom in src/main.py
### 2. Run application with render mode CPU
```
python3 src/viewer_slice.py
```
### Run application with render mode GPU
```
python3 src/viewer_slice.py --mode GPU
```
