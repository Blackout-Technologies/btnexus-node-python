from setuptools import setup, find_packages
# import pathlib
import os

# The directory containing this file
# HERE = pathlib.Path(__file__).parent
HERE = os.path.dirname(__file__)

# The text of the README file
readmePath = os.path.join(HERE , "README.md")
README = ""
with open(readmePath) as readmeFile:
    README = readmeFile.read()

versionPath = os.path.join(HERE , "VERSION")
VERSION = ""
with open(versionPath) as versionFile:
    VERSION = versionFile.read()

# VERSION = (HERE / "VERSION").read_text()
# try:
#     VERSION += '.{}'.format(os.environ["CI_PIPELINE_IID"])
# except:
#     print('LOCAL BUILD')



setup(name='btnexus-node-python',
    version=VERSION,
    description="Provides Node, Hook and PostRequests that follow the btProtocol.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Blackout-Technologies/btnexus-node-python",
    author="Blackout Technologies",
    author_email="dev@blackout.ai",
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages = find_packages(),
    py_modules=['btNode', 'btHook', 'btPostRequest', 'btStreamingNode'],
    install_requires=[
          'pyyaml',
          'six>=1.9.0',
          'certifi',
          'backports.ssl_match_hostname',
          'requests',
          'python-engineio', #==3.11.2', # newer version has a bug in 2.7 saying `AttributeError: 'module' object has no attribute 'main_thread'\n threading.current_thread() == threading.main_thread():`
          'python-socketio', #==4.4.0', # newer version has a bug in 2.7 saying `AttributeError: 'module' object has no attribute 'main_thread'\n threading.current_thread() == threading.main_thread():`
          'Twisted',
          'pyOpenSSL', 
          'service_identity'
    ],
)