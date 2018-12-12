from setuptools import setup, find_packages
setup(name='btnexus-node-python',
      version='3.0.0',
      packages = find_packages(),
      py_modules=['btNode'],
      install_requires=[
          'pyyaml',
          'six'
      ],
      )
####TODO: add requirements and bring it to the newest style to install via PyPi, is find_packages the best option?