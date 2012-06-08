# TesseractTrainer
by Balthazar Rouberol, [rouberol.b@gmail.com](mailto:rouberol.b@gmail.com)

TesseractTrainer is a very simple API, taking over the tedious manual process of 
training Tesseract3, as it is described in the [wiki page](https://code.google.com/p/tesseract-ocr/wiki/TrainingTesseract3).

## Dependencies

* Tesseract3.x
* python 2.6+ (python 3.x included)
* the `libtiff` library, if you plan to use multipage tifs

## API
The `tesseract_training.py` file offers a very simple API, defined through the class `TesseractTrainer`.
This class has only 4 public methods:

* `__init__(self, exp_number, dictionary_name, font_name, font_properties, tessdata_path, word_list)`: returns a `TesseractTrainer` instance
* `training(self)`: performs all training operations, thus returning a `traineddata` file.
* `add_trained_data(self)`: copies the generated `traineddata` file to your `tessdata` directory 
* `clean(self)`: deletes all files generated during the training process (except for the `traineddata` one).

I'd advise you to combine this `TesseractTrainer` class with the `argparse.ArgumentParser` (and associated security checks) I defined in `example.py`.

## Usage

	example.py [-h] [--experience_number EXPERIENCE_NUMBER] --font-name
	                  FONT_NAME [--font-properties FONT_PROPERTIES]
	                  [--tessdata-path TESSDATA_PATH] --tesseract-lang
	                  TESSERACT_LANG [--word_list WORD_LIST]

**Tesseract training arguments**

	optional arguments:
	-h, --help            show this help message and exit
	--experience_number EXPERIENCE_NUMBER, -e EXPERIENCE_NUMBER
	                    The number of the training experience.
	--font-name FONT_NAME, -F FONT_NAME
	                    The name of the used font. No spaces.
	--font-properties FONT_PROPERTIES, -f FONT_PROPERTIES
	                    The path of a file containing font properties for a list of fonts.
	--tessdata-path TESSDATA_PATH, -p TESSDATA_PATH
	                    The path of the tessdata/ directory on your filesystem.
	--tesseract-lang TESSERACT_LANG, -t TESSERACT_LANG
	                    Set the tesseract language traineddata to create.
	--word_list WORD_LIST, -w WORD_LIST
	                    The path of a file containing a list of frequent words.

## Conventions and remarks

* The training image must be named `{dictionary_name}.{font_name}.exp{experience_number}.tif`.
* If your `tessdata` directory is not writable without superuser rights, use the `sudo` command when executing your python script.
* Do not forget to describe your font properties in a file (parser default value: "font_properties"), following [these instructions](https://code.google.com/p/tesseract-ocr/wiki/TrainingTesseract3#font_properties_%28new_in_3.01%29).


## FreeBSD license
Copyright (c) 2012, Balthazar Rouberol
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies, 
either expressed or implied, of the FreeBSD Project.