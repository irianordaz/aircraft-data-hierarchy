#!/bin/bash
file_name=$(python -m build | grep -Eo '[^/ ]+\.whl'| sort -u | head -n 1)
pip install dist/$file_name --force-reinstall
pip install "numpy==1.26.4"
