import argparse
import sys
from os.path import exists
from training_framework import TesseractTrainer


def perform_security_checks(args):
    """ Perform several checks on the tesseract training arguments:
        * the tif file {tesseract_lang}.{font_name}.exp{experience_number}.tif must exist
        * the {tessdata_path} directorty must exist
        * the font name must not contain any spaces
        * the font defined by {font_name} must be described in the {font_properties} file
    If any of those tests fail, the execution will stop.
    """
    tifname = '.'.join([args.tesseract_lang, args.font_name, 'exp'+str(args.experience_number)]) + '.tif'
    if not exists(tifname):
        print "The %s file does not exist. Aborting." %(tifname)
        sys.exit(1)

    if not exists(args.tessdata_path):
        print "The %s directory does not exist. Aborting." %(args.tessdata_path)
        sys.exit(1)

    if " " in args.font_name:
        print "The --font-name / -F argument must not contain any spaces. Aborting."
        sys.exit(1)

    if args.font_name not in open(args.font_properties, 'r').read().split():
        print "The font properties of %s have not been defined in %s. Aborting." %(args.font_name, args.font_properties)
        sys.exit(1)

if __name__ == '__main__':

    # Parse training arguments
    parser = argparse.ArgumentParser(description='Tesseract training arguments.')
    parser.add_argument('--experience_number', '-e', type=int, action='store', default=0, help="The number of the training experience.")
    parser.add_argument('--font-name', '-F', type=str, action='store', required=True, help="The name of the used font. No spaces.")
    parser.add_argument('--font-properties', '-f', type=str, action='store' , default="./font_properties",        
        help="The path of a file containing font properties for a list of fonts.")
    parser.add_argument('--tessdata-path', '-p', type=str, action='store', default='/usr/local/share/tessdata/', 
        help="The path of the tessdata/ directory on your filesystem.")
    parser.add_argument('--tesseract-lang', '-t', type=str, action='store', required=True, help="Set the tesseract language traineddata to create.") 
    parser.add_argument('--word_list', '-w', type=str, action='store', default=None, help="The path of a file containing a list of frequent words.")
    args = parser.parse_args()    

    perform_security_checks(args) # Check validity of args

    # Training process
    trainer = TesseractTrainer(args.experience_number, args.tesseract_lang, args.font_name, args.font_properties, args.tessdata_path, args.word_list)
    trainer.training()
    trainer.clean()
    trainer.add_trained_data()