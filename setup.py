###############################################################################
# Copyright 2019 Alex M.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################

from setuptools import find_packages
from distutils.core import setup

try:
    import pypandoc
except (IOError, ImportError, OSError):
    print("failed to import pypandoc")
    with open("README.md", "r") as f:
        long_description = f.read()
else:
    long_description = pypandoc.convert_file("README.md", "rst")
    long_description = long_description.replace("\r", "")


setup(
    name="monitorcontrol",
    description="Monitor controls using MCSS over DDC-CI.",
    long_description=long_description,
    version="1.3",
    author="Alex M.",
    author_email="7845120+newAM@users.noreply.github.com",
    url="https://github.com/newAM/monitorcontrol",
    license="MIT",
    python_requires=">=3.6",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"],
    ),
)
