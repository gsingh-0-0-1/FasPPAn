#* Copyright (C) Gurmehar Singh - All Rights Reserved
#* Unauthorized copying or distribution of this file, via any medium is strictly prohibited
#* Proprietary and confidential
#* Written by Gurmehar Singh <gurmehar@gmail.com>, November 2019
#*/

import numpy as np, random
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
import os
import scipy.stats
import time
import PIL
from PIL import Image
import shutil
import pygame
import pytesseract
import sys

#********#********#********#********#********#********#********#
#********#********#CLASS DEFINITIONS#********#********#********#
#********#********#********#********#********#********#********#

class neuron:
    def __init__(self, thresh):
        self.thresh = thresh
        self.val = None

    def reset(self):
        self.val = None

    def inp(self, val):
        self.val = val

    def pval(self):
        print(self.val)

class layer:
    def __init__(self, shape):
        self.shape = shape
        self.struc = np.zeros(shape)
        
    def regenerate(self):
        del self.struc
        self.struc = np.zeros(shape)

    def inp(self, arr):
        if np.shape(arr) == np.shape(self.struc):
            pass
        else:
            raise Exception("Shape of input is not same as shape of layer.")

        self.struc = arr

    def genthresh(self, thresh):
        self.thresh = np.full(self.shape, thresh)
            
        
def passvals(layer1, layer2, transformation): #layer1, layer2, then a list of transformations to find the index to pass the value to
    if len(transformation) == len(np.shape(layer1)):
        pass
    else:
        raise Exception("Length of transformations is not equal to number of dimensions in first array.")
    
    for idx in np.ndindex(np.shape(layer1.struc)):
        newind = []
        for ind in range(len(idx)):
            if transformation[ind] == None:
                continue
            else:
                newind += [int( eval( str(idx[ind]) + transformation[ind] ) )]

        newind = tuple(newind)
        if layer1.struc[idx] > layer1.thresh[idx]:
            layer2.struc[newind] += layer1.struc[idx]
            
        

#********#********#********#********#********#********#********#

startdir='images/'

args = sys.argv

subbandsetting = args[1]
thresh1 = 0
thresh2 = 40000
thresh3 = 40000
thresh4 = 40000
thresh5 = 0
thresh6 = 0
noise = 0

imgshape = [780, 582]

for fname in os.listdir(startdir):
    if fname[0] == '.' or fname == 'temp.png' or 'single' in fname:
        continue
    print(fname)

    #Open image, basic initial processing
    
    try:
        img = Image.open(startdir+fname)
        img.resize(imgshape)
        canvas = Image.new('RGBA', img.size, (255,255,255,255)) 
        canvas.paste(img, mask=img) 
        canvas.save(startdir+fname, format="PNG")
        img = cv2.imread(startdir+fname)
    except ValueError: #for alpha channel errors
        img = cv2.imread(startdir+fname)

    if subbandsetting == 'reg':
        y1 = 170
        y2 = 370
        x1 = 320
        x2 = 470
        origphasesubband = np.copy(img[y1:y2, x1:x2])
    if subbandsetting == 'none':
        origphasesubband = np.copy(img)

    phasesubband = np.sum(origphasesubband, axis=2)
    phasesubband = 765 - phasesubband

    #generate first layer, create thresholds, input
    layer1len = len(phasesubband)
    layer1wid = len(phasesubband[0])
    layer1 = layer([layer1len, layer1wid])
    layer1.genthresh(thresh1)
    layer1.inp(phasesubband)

    #generate the second layer
    layer2len = layer1wid
    layer2 = layer([layer2len])
    layer2.genthresh(thresh2)

    #generate the third layer
    layer3len = int(layer2len/2)
    layer3 = layer([layer3len])
    layer3.genthresh(thresh3)

    #generate the fourth layer
    layer4len = int(layer3len/3)
    layer4 = layer([layer4len])
    layer4.genthresh(thresh4)

    #generate the fifth layer
    layer5len = int(layer4len/5)
    layer5 = layer([layer5len])
    layer5.genthresh(thresh5)

    #generate the sixth layer
    layer6len = int(layer5len/5)
    layer6 = layer([layer6len])
    layer6.genthresh(thresh6)

    #connect the layers
    passvals(layer1, layer2, [None, '/1'])
    passvals(layer2, layer3, ['/2'])
    passvals(layer3, layer4, ['/3'])
    passvals(layer4, layer5, ['/5'])
    passvals(layer5, layer6, ['/6'])

    finalval = layer6.struc[0]

    if finalval == 0:
        shutil.move(startdir+fname, 'not_pulsar/'+fname)
    else:
        shutil.move(startdir+fname, 'pulsar/'+fname)