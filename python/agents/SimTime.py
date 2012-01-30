'''
Created on Jan 20, 2012

@author: marek
'''

import time as default_time
from threading import Lock


class SimTime(object):
    def __init__(self, initialSpeed=1.0):
        self.__lock = Lock()
        
#        with self.__lock:
        self.reset()
        self.__speed = initialSpeed
        
    def setSpeed(self, speed):
        with self.__lock:
            now = default_time.time()
            self.__elapsed += self.__speed * (now - self.__lastSpeedChange)
            self.__lastSpeedChange = now
            self.__speed = speed

    def reset(self):
        with self.__lock:
            self.__start = default_time.time()
            self.__lastSpeedChange = self.__start
            self.__elapsed = 0

    def time(self):
        with self.__lock:
            return self.__elapsed + self.__speed * (default_time.time() - self.__lastSpeedChange) 

time = SimTime()

