import sys
import os

import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = 'v0.1'
PACKAGE_NAME = 'hdltools'
AUTHOR = 'Ricardo F Tafas Jr'
AUTHOR_EMAIL = 'contato@repodinamica.com.br'
URL = 'https://github.com/rftafas/hdltools'

LICENSE = 'Apache License 2.0'
DESCRIPTION = 'Python VHDL code generators.'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'math',
      'random',
      'mdutils',
      'datetime',
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )
