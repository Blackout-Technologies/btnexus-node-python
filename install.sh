#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:${HOME}/.local/lib/python"
mkdir -p ~/.local/lib/python
easy_install --install-dir ~/.local/lib/python .
echo 'export PYTHONPATH="${PYTHONPATH}:${HOME}/.local/lib/python"' >> ~/.bashrc
