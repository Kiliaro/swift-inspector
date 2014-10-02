# Copyright 2014 Richard Hawkins
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

from swift_inspector import __version__ as version

name = "swift-inspector"

setup(
    name = name,
    version = version,
    author = "Richard Hawkins",
    author_email = "hurricanerix@gmail.com",
    description = "Swift Inspector",
    license = "The MIT License (MIT)",
    keywords = "openstack swift middleware",
    url = "http://github.com/hurricanerix/swift-inspector",
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Environment :: OpenStack',
        ],
    install_requires=[],
    entry_points={
        'paste.filter_factory': [
            'swift_proxy_inspector=swift_inspector.middleware.proxy:filter_factory',
            'swift_object_inspector=swift_inspector.middleware.object:filter_factory',
            ],
        },
    )
