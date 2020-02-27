import os
import sys
CURRENTPATH = os.path.abspath(os.path.dirname(__file__))
ROOTPATH = os.path.split(CURRENTPATH)[0]
sys.path.append(ROOTPATH)