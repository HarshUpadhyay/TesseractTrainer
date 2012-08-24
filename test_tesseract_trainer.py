#!/usr/bin/env python

import unittest
import os
import glob

import lib.defaults as df
from lib.tesseract_training import TesseractTrainer


class TesseractTrainerTest(unittest.TestCase):

    GENERATED_DURING_TRAINING = ['unicharset', 'pffmtable', 'Microfeat', 'inttemp', 'normproto', 'mfunicharset']

    @classmethod
    def setUpClass(self):
        """ Setup a trainer with defaults arguments """
        self.trainer = TesseractTrainer(dictionary_name='test',
                                        text='text',
                                        font_name='helveticanarrow',
                                        font_path='./font/Helvetica-Narrow.otf',
                                        font_size=df.FONT_SIZE,
                                        exp_number=df.EXP_NUMBER,
                                        font_properties=df.FONT_PROPERTIES,
                                        tessdata_path=df.TESSDATA_PATH,
                                        word_list=df.WORD_LIST,
                                        verbose=False)
        self.prefix = '%s.%s.exp%d' % (self.trainer.dictionary_name, self.trainer.font_name, self.trainer.exp_number)

    @classmethod
    def tearDownClass(self):
        """ Delete all temporary files created during tests """
        tempfiles = glob.glob(self.trainer.dictionary_name + '.' + self.trainer.font_name + '*')
        for tempfile in tempfiles:
            os.remove(tempfile)
        os.remove(self.trainer.dictionary_name + '.traineddata')

    def assertFileExists(self, f):
        try:
            open(f)
        except IOError:
            raise AssertionError('The file %s does not exist.' % (f))

    def assertFileDoesNotExist(self, f):
        try:
            open(f)
        except IOError:
            pass
        else:
            raise AssertionError('The file %s does exist.' % (f))

    def test1_generate_boxfile(self):
        """ Test if the tif and box files are correctly created after executing the self.trainer._generate_boxfile() method. """
        self.trainer._generate_boxfile()
        self.assertFileExists(self.prefix + '.tif')
        self.assertFileExists(self.prefix + '.box')

    def test2_train_on_boxfile(self):
        """ Test if the tr file is correctly created after executing the self.trainer._train_on_boxfile() method. """
        self.trainer._train_on_boxfile()
        self.assertFileExists(self.prefix + '.tr')

    def test3_compute_character_set(self):
        """ Test if the unicharset file is correctly created after executing the self.trainer._compute_character_set() method. """
        self.trainer._compute_character_set()
        self.assertFileExists('unicharset')

    def test4_clustering(self):
        """ Test if the mfunicharset, inttemp, Microfeat and pffmtable files are correctly created
            after executing the self.trainer._clustering() method.
        """
        self.trainer._clustering()
        self.assertFileExists('mfunicharset')
        self.assertFileExists('inttemp')
        self.assertFileExists('Microfeat')
        self.assertFileExists('pffmtable')

    def test5_normalize(self):
        """ Test if the normproto file is correctly created after executing the self.trainer._normalize() method. """
        self.trainer._normalize()
        self.assertFileExists('normproto')

    def test6_rename_files(self):
        """ Check if all generated files were renamed to 'self.prefix'.old_name
            after executing the self.trainer._rename_files() method.
        """
        self.trainer._rename_files()
        for filename in self.GENERATED_DURING_TRAINING:
            if filename not in "mfunicharset":  # mfunicharset does not need to be renamed
                self.assertFileExists(self.trainer.dictionary_name + '.' + filename)
                self.assertFileDoesNotExist(filename)

    def test7_combine_data(self):
        """ Test if the traineddata file is correctly created after executing the self.combine_data() method. """
        self.trainer._combine_data()
        self.assertFileExists(self.trainer.dictionary_name + '.traineddata')

    def test8_clean(self):
        """ Test if the all generated files were removed after executing the self.trainer.clean() method. """
        self.trainer.clean()
        for filename in self.GENERATED_DURING_TRAINING:
            if filename not in "mfunicharset":  # mfunicharset does not need to be renamed
                self.assertFileDoesNotExist(self.trainer.dictionary_name + '.' + filename)
            else:
                self.assertFileDoesNotExist(filename)


if __name__ == '__main__':
    unittest.main()
