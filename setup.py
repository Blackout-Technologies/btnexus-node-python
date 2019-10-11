from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(name='btnexus-node-python',
    version='3.2.6',
    description="Provides Node, Hook and PostRequests that follow the btProtocol.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Blackout-Technologies/btnexus-node-python",
    author="Blackout Technologies",
    author_email="dev@blackout.ai",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
      #packages = find_packages(), #TODO I think I dont need packages...
    py_modules=['btNode', 'btHook', 'btPostRequest'],
    install_requires=[
          'pyyaml',
          'six',
          'certifi',
          'backports.ssl_match_hostname',
          'requests'
    ],
)
####TODO: add requirements and bring it to the newest style to install via PyPi, is find_packages the best option?
####TODO: https://realpython.com/pypi-publish-python-package/ maybe use Flit that makes it easier