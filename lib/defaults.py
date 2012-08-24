import os

FONT_SIZE = 25  # Default font size, used during tif generation
EXP_NUMBER = 0  # Default experience number, used in generated files name
FONT_PROPERTIES = './font_properties'  # Default path to the 'font_properties' file
TESSDATA_PATH = '/usr/local/share/tessdata'  # Default path to the 'tessdata' directory
WORD_LIST = None  # Default path to the "word_list" file, contaning frequent words
VERBOSE = True  # verbosity enabled by default. Set to False to remove all text outputs

# path to the 'tiffcp' binary, stored into the environment variables.
# At the end of the runtime, it will be automatically removed, so it won't have any impact
# on your permanent environment variables.
os.environ['TIFFCP'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',  'bin', 'tiffcp'))
