#!/usr/bin/env python
import codecs
import os
import re
from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(name='BRDF_descriptors',
      version=find_version("BRDF_descriptors", "__init__.py"),
      description='Interface to BRDF descriptors dataset',
      author='J Gomez-Dans',
      author_email='j.gomez-dans@ucl.ac.uk',
      url='https://github.com/jgomezdans/BRDF_descriptors',
      packages=['BRDF_descriptors']   ,
     )
