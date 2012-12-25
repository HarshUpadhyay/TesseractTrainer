import tesseract_trainer

from distutils.core import setup

setup(
    name="TesseractTrainer",
    version=tesseract_trainer.__version__,
    license=open('LICENSE.txt').read(),
    description='A small framework taking over the manual tesseract training process described in the Tesseract Wiki',
    author="Balthazar Rouberol",
    author_email='rouberol.b@gmail.com',
    url='https://github.com/BaltoRouberol/TesseractTrainer',
    packages=['tesseract_trainer'],
    requires=['PIL (>=1.1.7)'],
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
           'Topic :: Scientific/Engineering :: Artificial Intelligence',
           'Topic :: Scientific/Engineering :: Image Recognition',
        ],
    long_description=open('README.txt').read(),  # Long description: content of README.txt (DRY),
)
