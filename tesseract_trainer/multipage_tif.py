# -*- coding: utf-8 -*-

"""
API allowing the user to generate "black on white" multipage tif images
using a specified text, font and font-size, and to generate "box-files":
a file containing a list of characters and their associated box coordinates
and page number.

UTF-8 encoded characters are supported.
"""

import Image
import ImageFont
import ImageDraw
import glob
import subprocess
import os


class MultiPageTif(object):
    """ A class allowing generation of a multi-page tif. """

    def __init__(self, text, W, H, start_x, start_y, font_name, font_path, fontsize, exp_number, dictionary_name, verbose):

        # Width of the generated tifs (in px)
        self.W = W

        # Height of the generated tifs (in px)
        self.H = H

        # X coordinate of the first letter of the page
        self.start_x = start_x

        # Y coordinate of the first letter of the page
        self.start_y = start_y

        # Text to be written in generated multipage tif
        self.text = [word.decode('utf-8') for word in text.split(' ')]  # utf-8 characters support

        # Font used when "writing" the text into the tif
        self.font = ImageFont.truetype(font_path, fontsize)

        # Name of the font, used for generating the file prefix
        self.font_name = font_name

        # Name of the tesseract dictionary to be generated. Used for generating the file prefix.
        self.dictionary_name = dictionary_name

        # Prefix of the generated multi-page tif file
        self.prefix = ".".join([dictionary_name, font_name, "exp" + str(exp_number)])

        # A list of boxfile lines, each one of the form "char x0 y x1 y1 page_number"
        self.boxlines = []

        # prefix of all temporary single-page tif files
        self.indiv_page_prefix = 'page'

        # Set verbose to True to display output
        self.verbose = verbose

    def generate_tif(self):
        """ Create several individual tifs from text and merge them
            into a multi-page tif, and finally delete all individual tifs.
        """
        self._fill_pages()
        self._multipage_tif()
        self._clean()

    def generate_boxfile(self):
        """ Generate a boxfile from the multipage tif.
            The boxfile will be named {self.prefix}.box
        """
        boxfile_path = self.prefix + '.box'
        if self.verbose:
            print("Generating boxfile %s" % (boxfile_path))
        with open(boxfile_path, 'w') as boxfile:
            for boxline in self.boxlines:
                boxfile.write(boxline.encode('utf-8') + '\n')  # utf-8 characters support

    def _new_tif(self, color="white"):
        """ Create and returns a new RGB blank tif, with specified background color (default: white) """
        return Image.new("L", (self.W, self.H), color=color)

    def _save_tif(self, tif, page_number):
        """ Save the argument tif using 'page_number' argument in filename.
            The filepath will be {self.indiv_page_prefix}{self.page_number}.tif
        """
        tif.save(self.indiv_page_prefix + str(page_number) + '.tif')

    def _fill_pages(self):
        """ Fill individual tifs with text, and save them to disk.
            Each time a character is written in the tif, its coordinates will be added to the self.boxlines
            list (with the exception of white spaces).

            All along the process, we manage to contain the text within the image limits.
        """
        tif = self._new_tif()
        draw = ImageDraw.Draw(tif)
        page_nb = 0
        x_pos = self.start_x
        y_pos = self.start_y
        if self.verbose:
            print('Generating individual tif image %s' % (self.indiv_page_prefix + str(page_nb) + '.tif'))
        for word in self.text:
            word += ' '  # add a space between each word
            wordsize_w, wordsize_h = self.font.getsize(word)
            # Check if word can fit the line, if not, newline
            # if newline, check if the newline fits the page
            # if not, save the current page and create a new one
            if not word_fits_in_line(self.W, x_pos, wordsize_w):
                if newline_fits_in_page(self.H, y_pos, wordsize_h):
                    # newline
                    x_pos = self.start_x
                    y_pos += wordsize_h
                else:
                    # newline AND newpage
                    x_pos = self.start_x
                    y_pos = self.start_y
                    self._save_tif(tif, page_nb)  # save individual tif
                    page_nb += 1
                    if self.verbose:
                        print('Generating individual tif image %s' % (self.indiv_page_prefix + str(page_nb) + '.tif'))
                    tif = self._new_tif()  # new page
                    draw = ImageDraw.Draw(tif)  # write on this new page
            # write word
            for char in word:
                char_w, char_h = self.font.getsize(char)  # get character height / width
                char_x0, char_y0 = x_pos, y_pos  # character top-left corner coordinates
                char_x1, char_y1 = x_pos + char_w, y_pos + char_h  # character bottom-roght corner coordinates
                draw.text((x_pos, y_pos), char, fill="black", font=self.font)  # write character in tif file
                if char != ' ':
                    # draw.rectangle([(char_x0, char_y0),(char_x1, char_y1)], outline="red")
                    self._write_boxline(char, char_x0, char_y0, char_x1, char_y1, page_nb)  # add coordinates to boxfile
                x_pos += char_w
        self._save_tif(tif, page_nb)  # save last tif

    def _write_boxline(self, char, char_x0, char_y0, char_x1, char_y1, page_nb):
        """ Generate a boxfile line given a character coordinates, and append it to the
            self.boxlines list.
        """
        # top-left corner coordinates in tesseract particular frame
        tess_char_x0, tess_char_y0 = pil_coord_to_tesseract(char_x0, char_y0, self.H)
        # bottom-right corner coordinates in tessseract particular frame
        tess_char_x1, tess_char_y1 = pil_coord_to_tesseract(char_x1, char_y1, self.H)
        boxline = '%s %d %d %d %d %d' % (char, tess_char_x0, tess_char_y0, tess_char_x1, tess_char_y1, page_nb)
        self.boxlines.append(boxline)

    def _multipage_tif(self):
        """ Generate a multipage tif from all the generated tifs.
            The multipage tif will be named {self.prefix}.tif
        """
        cmd = ['convert']  # ImageMagick command `convert` can merge individual tifs into a multipage tif file
        tifs = sorted(glob.glob(self.indiv_page_prefix + '*.tif'), key=os.path.getmtime)
        cmd.extend(tifs)  # add all individual tifs as arguments
        multitif_name = self.prefix + '.tif'
        cmd.append(multitif_name)  # name of the result multipage tif
        if self.verbose:
            print('Generating multipage-tif %s' % (multitif_name))
        subprocess.call(cmd)  # merge of all individul tifs into a multipage one

    def _clean(self):
        """ Remove all generated individual tifs """
        if self.verbose:
            print("Removing all individual tif images")
        tifs = glob.glob('%s*' % (self.indiv_page_prefix))  # all individual tifd
        for tif in tifs:
            os.remove(tif)


# Utility functions
def word_fits_in_line(pagewidth, x_pos, wordsize_w):
    """ Return True if a word can fit into a line. """
    return (pagewidth - x_pos - wordsize_w) > 0


def newline_fits_in_page(pageheight, y_pos, wordsize_h):
    """ Return True if a new line can be contained in a page. """
    return (pageheight - y_pos - (2 * wordsize_h)) > 0


def pil_coord_to_tesseract(pil_x, pil_y, tif_h):
    """ Convert PIL coordinates into Tesseract boxfile coordinates:
        in PIL, (0,0) is at the top left corner and
        in tesseract boxfile format, (0,0) is at the bottom left corner.
    """
    return pil_x, tif_h - pil_y
