from setuptools import setup, find_packages
setup(name='btnexus-node-python',
      version='3.2.0',
      packages = find_packages(),
      py_modules=['btNode', 'btHook'],
      install_requires=[
          'pyyaml',
          'six',
          'certifi',
          'backports.ssl_match_hostname'
      ],
      )
####TODO: add requirements and bring it to the newest style to install via PyPi, is find_packages the best option?
