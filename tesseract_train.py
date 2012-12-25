"""
A small training framework for Tesseract 3.0.1, taking over the tedious manual process
of training Tesseract 3described in the Tesseract Wiki:
https://code.google.com/p/tesseract-ocr/wiki/TrainingTesseract3
"""

__version__ = '0.0.5'
__author__ = 'Balthazar Rouberol, rouberol.b@gmail.com'

import shutil
import os
import subprocess

from os.path import join, exists, dirname

from multipage_tif import MultiPageTif


# list of files generated during the training procedure
GENERATED_DURING_TRAINING = ['unicharset', 'pffmtable', 'Microfeat', 'inttemp', 'normproto']

FONT_SIZE = 25  # Default font size, used during tif generation
EXP_NUMBER = 0  # Default experience number, used in generated files name
FONT_PROPERTIES = join(dirname(__file__), 'font_properties')  # Default path to the 'font_properties' file
TESSDATA_PATH = '/usr/local/share/tessdata'  # Default path to the 'tessdata' directory
WORD_LIST = None  # Default path to the "word_list" file, contaning frequent words
VERBOSE = True  # verbosity enabled by default. Set to False to remove all text outputs


class TesseractTrainer:
    """ Object handling the training process of tesseract """

    def __init__(self,
        dictionary_name,
        text,
        font_name,
        font_path,
        font_size=FONT_SIZE,
        exp_number=EXP_NUMBER,
        font_properties=FONT_PROPERTIES,
        tessdata_path=TESSDATA_PATH,
        word_list=WORD_LIST,
        verbose=VERBOSE):

        # Training text: the text used for the multipage tif generation
        # we replace all \n by " " as we'll split the text over " "s
        self.training_text = open(text).read().replace("\n", " ")

        # Experience number: naming convention defined in the Tesseract training wiki
        self.exp_number = exp_number

        # The name of the result Tesseract "dictionary", trained on a new language/font
        self.dictionary_name = dictionary_name

        # The name of the font you're training tesseract on.
        # WARNING: this name must match a font name in the font_properties file
        # and must not contain spaces
        self.font_name = font_name
        if ' ' in self.font_name:
            raise SystemExit("The --font-name / -F argument must not contain any spaces. Aborting.")

        # The local path to the TrueType/OpentType file of the training font
        self.font_path = font_path
        if not exists(self.font_path):
            raise SystemExit("The %s file does not exist. Aborting." % (self.font_path))

        # The font size (in px) used during the multipage tif generation
        self.font_size = font_size

        # The prefix of all generated tifs, boxfiles, training files (ex: eng.helveticanarrow.exp0.box)
        self.prefix = '%s.%s.exp%s' % (self.dictionary_name, self.font_name, str(self.exp_number))

        # Local path to the 'font_propperties' file
        self.font_properties = font_properties
        with open(self.font_properties, 'r') as fp:
            if self.font_name not in fp.read().split():
                raise SystemExit("The font properties of %s have not been defined in %s. Aborting." % (self.font_name, self.font_properties))

        # Local path to the 'tessdata' directory
        self.tessdata_path = tessdata_path
        if not exists(self.tessdata_path):
            raise SystemExit("The %s directory does not exist. Aborting." % (self.tessdata_path))

        # Local path to a file containing frequently encountered words
        self.word_list = word_list

        # Set verbose to True to display the training commands output
        self.verbose = verbose

    def _generate_boxfile(self):
        """ Generate a multipage tif, filled with the training text and generate a boxfile
            from the coordinates of the characters inside it
        """
        mp = MultiPageTif(self.training_text, 800, 600, 20, 20, self.font_name, self.font_path,
            self.font_size, self.exp_number, self.dictionary_name, self.verbose)
        mp.generate_tif()  # generate a multi-page tif, filled with self.training_text
        mp.generate_boxfile()  # generate the boxfile, associated with the generated tif

    def _train_on_boxfile(self):
        """ Run tesseract on training mode, using the generated boxfiles """
        cmd = 'tesseract {prefix}.tif {prefix} nobatch box.train'.format(prefix=self.prefix)
        run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        display_output(run, self.verbose)

    def _compute_character_set(self):
        """ Computes the character properties set: isalpha, isdigit, isupper, islower, ispunctuation
            and encode it in the 'unicharset' data file

            examples:
            ';' is an punctuation character. Its properties are thus represented
                by the binary number 10000 (10 in hexadecimal).
            'b' is an alphabetic character and a lower case character.
                Its properties are thus represented by the binary number 00011 (3 in hexadecimal).
            W' is an alphabetic character and an upper case character. Its properties are
                thus represented by the binary number 00101 (5 in hexadecimal).
            '7' is just a digit. Its properties are thus represented by the binary number 01000 (8 in hexadecimal).
            '=' does is not punctuation not digit or alphabetic character. Its properties
                 are thus represented by the binary number 00000 (0 in hexadecimal).
        """
        cmd = 'unicharset_extractor %s.box' % (self.prefix)
        run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        display_output(run, self.verbose)

    def _clustering(self):
        """ Cluster character features from all the training pages, and create characters prototype """
        cmd = 'mftraining -F font_properties -U unicharset %s.tr' % (self.prefix)
        run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        display_output(run, self.verbose)

    def _normalize(self):
        """ Generate the 'normproto' data file (the character normalization sensitivity prototypes) """
        cmd = 'cntraining %s.tr' % (self.prefix)
        run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        display_output(run, self.verbose)

    def _rename_files(self):
        """ Add the self.dictionary_name prefix to each file generated during the tesseract training process """
        for generated_file in GENERATED_DURING_TRAINING:
            os.rename('%s' % (generated_file), '%s.%s' % (self.dictionary_name, generated_file))

    def _dictionary_data(self):
        """ Generate dictionaries, coded as a Directed Acyclic Word Graph (DAWG),
            from the list of frequent words if those were submitted during the Trainer initialization.
        """
        if self.word_list:
            cmd = 'wordlist2dawg %s %s.freq-dawg %s.unicharset' % (self.word_list, self.dictionary_name,
                self.dictionary_name)
            run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            display_output(run, self.verbose)

    def _combine_data(self):
        cmd = 'combine_tessdata %s.' % (self.dictionary_name)
        run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        display_output(run, self.verbose)

    def training(self):
        """ Execute all training steps """
        self._generate_boxfile()
        self._train_on_boxfile()
        self._compute_character_set()
        self._clustering()
        self._normalize()
        self._rename_files()
        self._dictionary_data()
        self._combine_data()
        if self.verbose:
            print('The %s.traineddata file has been generated !' % (self.dictionary_name))

    def clean(self):
        """ Remove all files generated during tesseract training process """
        if self.verbose:
            print('cleaning...')
        os.remove('%s.tr' % (self.prefix))
        os.remove('%s.txt' % (self.prefix))
        os.remove('%s.box' % (self.prefix))
        os.remove('%s.inttemp' % (self.dictionary_name))
        os.remove('%s.Microfeat' % (self.dictionary_name))
        os.remove('%s.normproto' % (self.dictionary_name))
        os.remove('%s.pffmtable' % (self.dictionary_name))
        os.remove('%s.unicharset' % (self.dictionary_name))
        if self.word_list:
            os.remove('%s.freq-dawg' % (self.dictionary_name))
        os.remove('mfunicharset')

    def add_trained_data(self):
        """ Copy the newly trained data to the tessdata/ directory """
        traineddata = '%s.traineddata' % (self.dictionary_name)
        if self.verbose:
            print('Copying %s to %s.' % (traineddata, self.tessdata_path))
        try:
            shutil.copyfile(traineddata, join(self.tessdata_path, traineddata))  # Copy traineddata fie to the tessdata dir
        except IOError:
            raise IOError("Permission denied. Super-user rights are required to copy %s to %s." % (traineddata, self.tessdata_path))


def display_output(run, verbose):
    """ Display the output/error of a subprocess.Popen object
        if 'verbose' is True.
    """
    out, err = run.communicate()
    if verbose:
        print out.strip()
        if err:
            print err.strip()


if __name__ == '__main__':
    import argparse

    # Parse training arguments
    parser = argparse.ArgumentParser(description='Tesseract training arguments.')
    # Required arguments
    parser.add_argument('--tesseract-lang', '-l', type=str, action='store', required=True,
        help="Set the tesseract language traineddata to create.")
    parser.add_argument('--training-text', '-t', type=str, action='store', required=True,
        help="The path of the training text.")
    parser.add_argument('--font-path', '-F', type=str, action='store', required=True,
        help="The path of TrueType/OpenType file of the used training font.")
    parser.add_argument('--font-name', '-n', type=str, action='store', required=True,
        help="The name of the used training font. No spaces.")
    # Optional arguments
    parser.add_argument('--experience_number', '-e', type=int, action='store', default=EXP_NUMBER,
        help="The number of the training experience.")
    parser.add_argument('--font-properties', '-f', type=str, action='store', default=FONT_PROPERTIES,
        help="The path of a file containing font properties for a list of training fonts.")
    parser.add_argument('--font-size', '-s', type=int, action='store', default=FONT_SIZE,
        help="The font size of the training font, in px.")
    parser.add_argument('--tessdata-path', '-p', type=str, action='store', default=TESSDATA_PATH,
        help="The path of the tessdata/ directory on your filesystem.")
    parser.add_argument('--word_list', '-w', type=str, action='store', default=WORD_LIST,
        help="The path of a file containing a list of frequent words.")
    parser.add_argument('--verbose', '-v', action='store_true',
        help="Use this argument if you want to display the training output.")
    args = parser.parse_args()

    # Training process
    trainer = TesseractTrainer(dictionary_name=args.tesseract_lang,
                                text=args.training_text,
                                font_name=args.font_name,
                                font_path=args.font_path,
                                font_size=args.font_size,
                                exp_number=args.experience_number,
                                font_properties=args.font_properties,
                                tessdata_path=args.tessdata_path,
                                word_list=args.word_list,
                                verbose=args.verbose)
    trainer.training()  # generate a multipage tif from args.training_text, train on it and generate a traineddata file
    trainer.clean()  # remove all files generated in the training process (except the traineddata file)
    trainer.add_trained_data()  # copy the traineddata file to the tessdata/ directory