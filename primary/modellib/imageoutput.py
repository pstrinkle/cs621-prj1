#! /usr/bin/python
"""Module developed for outputing data as an image."""

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: This module is meant to represent output of data.
#

import sys
import math
from PIL import Image

MAX_COLOR = 256**3
MAX_GREYSCALE = 256

def image_create_color(file_name, dictionary, data, val_range):
    """Dump the matrix as a color bmp file.

    file_name  is the file to create.
    dictionary is the dictionary of terms.
    data       is the document-weight dictionary.
    val_range  is the value range, max - min."""
    
    # Each column is a document within data
    # Each row is a term.

    # for greyscale.
    img = Image.new('RGB', (len(data), len(dictionary)))
    pix = img.load()
    
    #print "\twidth: %d; height: %d" % (len(data), len(dictionary)) 

    # This code is identical to the method used to create the text file.
    # Except because it's building bitmaps, I think it will be flipped. lol.
    sorted_docs = sorted(data.keys())  
    sorted_terms = sorted(dictionary)
    
    # val_range value is how far the minimum value and maximum value are apart 
    # from each other.
    # so val_range / color_range gives us a way of representing the values with 
    # shading. --> divisible.
    #
    # math.floor(val / divisible) -> shade.
    #
    # the lower the value, the closer to black -- so this will create images
    # that are black with light spots.
    shade_range = float(val_range / MAX_COLOR)

    if shade_range == 0:
        sys.stderr.write("invalid shade_range\n")
        sys.exit(-3)
    
    #print "%f" % shade_range
    # my pictures really hm... maybe, I should halve the scale.

    # Print Term Rows
    # with L the pixel value is from 0 - 255 (black -> white)
    for i in range(len(sorted_terms)):
        for j in range(len(sorted_docs)):
            # for each row, for each column
            if sorted_terms[i] in data[sorted_docs[j]]:
                val = data[sorted_docs[j]][sorted_terms[i]]

                color = math.ceil(val / shade_range)

                # not bloodly likely (until i switched to ceil)                
                if color > MAX_COLOR-1:
                    color = MAX_COLOR-1
                
                pix[j, i] = color
            else:
                pix[j, i] = 0 # (white) i is row, j is column.

    img.save(file_name + '.png')

def image_create(file_name, dictionary, data, val_range, background):
    """Dump the matrix as a grey-scale bmp file.
    
    file_name  is the file to create.
    dictionary is the dictionary of terms.
    data       is the document-weight dictionary.
    val_range  is the value range, max - min.
    background is either 'white' or 'black'."""

    # Each column is a document within data
    # Each row is a term.

    # for greyscale.
    img = Image.new('L', (len(data), len(dictionary)))
    pix = img.load()
    
    if background == "white":
        backcolor = 255
    elif background == "black":
        backcolor = 0
    else:
        sys.stderr.write("invalid parameter\n")
        sys.exit(-3)
    
    #print "\twidth: %d; height: %d" % (len(data), len(dictionary)) 

    # This code is identical to the method used to create the text file.
    # Except because it's building bitmaps, I think it will be flipped. lol.
    sorted_docs = sorted(data.keys())  
    sorted_terms = sorted(dictionary)
    
    # val_range value is how far the minimum value and maximum value are apart 
    # from each other.
    # so val_range / color_range gives us a way of representing the values with 
    # shading. --> divisible.
    #
    # math.floor(val / divisible) -> shade.
    #
    # the lower the value, the closer to black -- so this will create images
    # that are black with light spots.
    shade_range = float(val_range / MAX_GREYSCALE)

    if shade_range == 0:
        sys.stderr.write("invalid shade_range\n")
        sys.exit(-3)
    
    #print "%f" % shade_range
    # my pictures really hm... maybe, I should halve the scale.

    # Print Term Rows
    # with L the pixel value is from 0 - 255 (black -> white)
    for i in range(len(sorted_terms)):
        for j in range(len(sorted_docs)):
            # for each row, for each column
            if sorted_terms[i] in data[sorted_docs[j]]:
                val = data[sorted_docs[j]][sorted_terms[i]]
                
                #print "%f" % val
                #print "%d" % math.floor(val / shade_range)
                
                # with floor and most values of mine very small; maybe it'll
                # set most to just 0 instead of a value when they shouldn't
                # really be zero.
                #color = math.floor(val / shade_range)
                
                # doing math.floor means you will have 0s for your low data --
                # which means there was no data point -- not what we want.
                #
                # could do pix[] = 255 - color to switch to white background.
                
                color = math.ceil(val / shade_range)
                
                # not bloodly likely (until i switched to ceil)
                if color > MAX_GREYSCALE-1:
                    color = MAX_GREYSCALE-1
                
                #print "color: %d" % color
                if backcolor == 0:
                    pix[j, i] = color
                else:
                    pix[j, i] = 255 - color
            else:
                pix[j, i] = backcolor # (white) i is row, j is column.

    img.save(file_name + '.png')
