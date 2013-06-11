import re
from setuptools import setup

from os.path import dirname, join, relpath


VERSION = re.search("__version__ = '([^']+)'", open(
    relpath(join(dirname(__file__), 'tesseract_trainer', '__init__.py'))
).read().strip()).group(1)


setup(
    name="TesseractTrainer",
    version=VERSION,
    license=open(relpath(join(dirname(__file__), 'LICENSE.txt'))).read(),
    description='A small framework taking over the manual tesseract training process described in the Tesseract Wiki',
    author="Balthazar Rouberol",
    author_email='rouberol.b@gmail.com',
    url='https://github.com/BaltoRouberol/TesseractTrainer',
    packages=['tesseract_trainer'],
    install_requires=['Pillow>=2.0.0'],
    keywords=['tesseract', 'OCR', 'optical character recogniton', 'training'],
    scripts=['tesseract_trainer/tesstrain'],
    classifiers=[
           'Development Status :: 3 - Alpha',
           'Environment :: Console',
           'Intended Audience :: Developers',
           'License :: OSI Approved :: BSD License',
           'Natural Language :: English',
           'Operating System :: POSIX :: Linux',
           'Operating System :: Unix',
           'Operating System :: MacOS :: MacOS X',
           'Programming Language :: Python :: 2.6',
           'Programming Language :: Python :: 2.7',
           'Programming Language :: Python :: 3.2',
           'Programming Language :: Python :: 3.3',
           'Topic :: Scientific/Engineering :: Artificial Intelligence',
           'Topic :: Scientific/Engineering :: Image Recognition',
        ],
    long_description=open(relpath(join(dirname(__file__), 'README.txt'))).read(),
    # Long description: content of README.txt (DRY),
)
