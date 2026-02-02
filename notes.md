### Raspberry Pi:
Must install PyQt6 using global apt installer
```sudo apt install python3-pyqt6 python3-venv```
Then you must create a venv with system packages
```python -m venv --system-site-packages venv```
Then install from toml file
```pip install -e .```
Then run glider
```glider```