#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      s6anloew
#
# Created:     15.09.2014
# Copyright:   (c) s6anloew 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class Internal_Math():
    def __init__(self):
        """This class provids tools to easiely access the mathematical opperations
            needed for the thesis"""
        pass


    def _add_(self, a, b):
        self.value = a + b
        return self.value


    def _minus_(self, a, b):
        self.value = a - b
        return self.value


    def _multi_(self, a, b):
        self.value = a * b
        return self.value

##    def _diverance_(self, a, b):
##        self.value = a/float(b)
##        return self.value
##

    def _bigger_(self, a, b):
        self.value = a > b
        return self.value


    def _bigger_equal(self, a, b):
        self.value = a >= b
        return self.value


    def _smaller_(self, a, b):
        self.value = a < b
        return self.value


    def _smaller_equal(self, a, b):
        self.value = a <= b
        return self.value

