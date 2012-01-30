'''
Created on Dec 15, 2011

@author: Marek Skrajnowski
'''

import random
import logging
from agents.Application import application

if __name__ == '__main__':
    #logging.basicConfig(level=logging.CRITICAL)
    logging.basicConfig(level=logging.DEBUG)
    random.seed()
    app = application()
    
