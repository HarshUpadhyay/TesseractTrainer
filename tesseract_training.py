#!/usr/bin/env python

"""
A small training framework for Tesseract 3.x, taking over the tedious manual process
described in the Tesseract Wiki: https://code.google.com/p/tesseract-ocr/wiki/TrainingTesseract3

Written by Balthazar Rouberol, <balthazar@strongsteam.com>, @BaltoRouberol


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
"""

import sys
import shutil
from os import system
from os.path import join

class TesseractTrainer:
    """ Object handling the training process of tesseract """

    def __init__(self, exp_number, dictionary_name, font_name, font_properties, tessdata_path, word_list):
        self.dictionary_name = dictionary_name
        self.font_name = font_name
        self.prefix = '%s.%s.exp%s' %(self.dictionary_name, self.font_name, str(exp_number))
        self.font_properties = font_properties
        self.tessdata_path = tessdata_path
        self.word_list = word_list

    def _generate_boxfile(self):
        """ Generate a boxfile from the training image """
        cmd = 'tesseract {prefix}.tif {prefix} batch.nochop makebox'.format(prefix = self.prefix)
        system(cmd)
    
    def _train_on_boxfile(self):
        """ Run tesseract on training mode, using the generated boxfiles """
        cmd = 'tesseract {prefix}.tif {prefix} nobatch box.train'.format(prefix = self.prefix)
        system(cmd)

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
        cmd = 'unicharset_extractor %s.box ' %(self.prefix)
        system(cmd)

    def _clustering(self):
        """ Cluster character features from all the training pages, and create characters prototype """
        cmd = 'mftraining -F font_properties -U unicharset %s.tr ' %(self.prefix)
        system(cmd)

    def _normalize(self):
        """ Generate the 'normproto' data file (the character normalization sensitivity prototypes) """
        cmd = 'cntraining %s.tr ' %(self.prefix)
        system(cmd)

    def _rename_files(self):
        """ Add the self.dictionary_name prefix to each file generated during the tesseract training process """
        for f in ['unicharset', 'pffmtable', 'Microfeat', 'inttemp', 'normproto']:
            cmd = 'mv %s %s.%s' %(f, self.dictionary_name, f)
            system(cmd)

    def _dictionary_data(self):
        """ Generate dictionaries, coded as a Directed Acyclic Word Graph (DAWG), 
        from the list of frequent words if those were submitted during the Trainer initialization. 
        """
        if self.word_list:
            freq = 'wordlist2dawg %s %s.freq-dawg %s.unicharset' %(self.word_list, self.dictionary_name, self.dictionary_name)
            system(freq)

    def _combine_data(self):
        cmd = 'combine_tessdata %s.' %(self.dictionary_name)
        system(cmd)

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
        print('The %s.traineddata file has been generated !' %(self.dictionary_name))

    def clean(self):
        """ Remove all files generated during tesseract training process """
        print('cleaning...')
        cmd = 'rm '
        cmd += '%s.tr ' %(self.prefix)
        cmd += '%s.txt ' %(self.prefix)
        cmd += '%s.box ' %(self.prefix)
        cmd += '%s.inttemp ' %(self.dictionary_name) 
        cmd += '%s.Microfeat ' %(self.dictionary_name)
        cmd += '%s.normproto ' %(self.dictionary_name)
        cmd += '%s.pffmtable ' %(self.dictionary_name)
        cmd += '%s.unicharset ' %(self.dictionary_name)
        if self.word_list:
            cmd += '%s.freq-dawg ' %(self.dictionary_name)
        cmd += 'mfunicharset '
        system(cmd)
    
    def add_trained_data(self):
        """ Copy the newly trained data to the tessdata/ directory """
        traineddata = '%s.traineddata' %(self.dictionary_name)
        print('Copying %s to %s.' %(traineddata, self.tessdata_path))
        shutil.copyfile(traineddata, join(self.tessdata_path, traineddata))
        