#!/usr/bin/python2

from distutils.core import setup
from dragon_on_wheels import __version__ as package_version

package_name = 'dragon_on_wheels'
michurin = 'Alexey V Michurin'
michurin_email = 'a.michurin@gmail.com'

setup(name = package_name,
    version = package_version,
    packages = [package_name],
    description = 'Simple SCGI WSGI server',
    long_description = 'Pure Python implementation of simple threaded SCGI WSGI server',
    url = 'https://github.com/michurin/dragon-on-wheels',
    author = michurin,
    author_email = michurin_email,
    maintainer = michurin,
    maintainer_email = michurin_email,
    license = 'Simplified BSD License',
    platforms = 'any',
    classifiers = [
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2'
        'License :: OSI Approved :: BSD License']
    )
