#!/usr/bin/env python

import unittest
import os
import glob

from lib.tesseract_training import TesseractTrainer


class TesseractTrainerTest(unittest.TestCase):
    """ A monolithic test suite ensuring that all training files are correctly created
        duting the tesseract training process.
    """

    GENERATED_DURING_TRAINING = ['unicharset', 'pffmtable', 'Microfeat', 'inttemp', 'normproto', 'mfunicharset']

    @classmethod
    def setUpClass(self):
        """ Setup a trainer with defaults arguments """
        self.trainer = TesseractTrainer(dictionary_name='test',
                                        text='text',
                                        font_name='helveticanarrow',
                                        font_path='./font/Helvetica-Narrow.otf',
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


class TesseractTrainerFailuresTest(unittest.TestCase):
    """ A test suite ensuring that invalid self.training parameters will cause the
        program to raise an exception.
    """

    def test_font_path_exists(self):
        """ Checks that an invalid font path as self.trainer.font_path argument
            raises a SystemExit exception.
        """
        with self.assertRaises(SystemExit):
            self.trainer = TesseractTrainer(dictionary_name='test',
                                    text='text',
                                    font_name='helveticanarrow',
                                    font_path='invalid-font-path',
                                    verbose=False)

    def test_font_name_spaces(self):
        """ Checks that an self.trainer.font_name argument containing spaces
            raises a SystemExit exception.
        """
        with self.assertRaises(SystemExit):
            self.trainer = TesseractTrainer(dictionary_name='test',
                                    text='text',
                                    font_name='helveti canarrow',
                                    font_path='./font/Helvetica-Narrow.otf',
                                    verbose=False)

    def test_tessdata_path_exists(self):
        """ Checks that an invalid path as self.trainer.tessdata_path argument
            raises a SystemExit exception.
        """
        with self.assertRaises(SystemExit):
            self.trainer = TesseractTrainer(dictionary_name='test',
                                    text='text',
                                    font_name='helveticanarrow',
                                    font_path='./font/Helvetica-Narrow.otf',
                                    tessdata_path='indvalid/tessdata_path',
                                    verbose=False)

    def test_font_name_matches_font_properties(self):
        """ Checks that self.trainer.font_name matches a line of the
            self.font_properties file.
        """
        font_properties_path = 'test-font-properties'
        with open(font_properties_path, 'w') as fp:
            fp.write('testfont 0 0 0 0 0\n')
            with self.assertRaises(SystemExit):
                self.trainer = TesseractTrainer(dictionary_name='test',
                                        text='text',
                                        font_name='helveticanarrow',
                                        font_path='./font/Helvetica-Narrow.otf',
                                        font_properties=font_properties_path,
                                        verbose=False)
        os.remove(font_properties_path)


if __name__ == '__main__':
    unittest.main()
