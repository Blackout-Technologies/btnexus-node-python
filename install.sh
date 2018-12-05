#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:${HOME}/lib/python"
mkdir -p ~/lib/python
easy_install --install-dir ~/lib/python .
echo 'export PYTHONPATH="${PYTHONPATH}:${HOME}/lib/python"' >> ~/.bashrc
