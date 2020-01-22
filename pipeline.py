#!/usr/bin/env python

import os, sys
#import matplotlib.image as mpimg
#import matplotlib.pyplot as plt
#import numpy as np
#import math

################################
## Config:                    ##

AV_DIR = "../Alice/Meshroom-2019.2.0/aliceVision/"
WORKING_DIR = "/tmp/AV_tmp/"
DC_DIR = "data/"
DATA_DIR = DC_DIR + "p1/"
CALIBRATION_DIR = DC_DIR + "c0/"
SFMDATA_FILENAME = "data"
CAM_SENSOR_DB = "share/aliceVision/cameraSensors.db"

################################
## Setup:                     ##

os.environ['LD_LIBRARY_PATH'] = AV_DIR + "lib/"



if not os.path.isdir(WORKING_DIR):
    os.mkdir(WORKING_DIR)


av = AV_DIR + "bin/aliceVision_"
SfMData = WORKING_DIR + SFMDATA_FILENAME
sensor_db = AV_DIR + CAM_SENSOR_DB

FeatureMatching_out = SfMData + "FeatureMatching"
if not os.path.isdir(FeatureMatching_out):
    os.mkdir(FeatureMatching_out)

CameraLocalization_debug = WORKING_DIR + "CameraLocalization_debug"
if not os.path.isdir(CameraLocalization_debug):
    os.mkdir(CameraLocalization_debug)

################################
## CALIBRATION                ##

CameraCalibration_out = SfMData + "CameraCalibration.json"

def calibrate(out_file):
    print("Calibration..")
    cmd = av + "cameraCalibration -i " + CALIBRATION_DIR
    cmd += " -p CHESSBOARD"
    cmd += " -s 7 7"
    cmd += " -o " + out_file
    os.system(cmd)

if len(sys.argv) == 2:
    if sys.argv[1] == "--calibrate":
        calibrate(CameraCalibration_out)
        sys.exit()

    if sys.argv[1] == "--clean":
        os.system("rm -fr " + WORKING_DIR)
        sys.exit()

################################
## STEP 0: CameraInit         ##
CameraInit_out = SfMData + "CameraInit.sfm"

def cameraInit():
    print("STEP 0: CameraInit")

    cmd = av + "cameraInit --imageFolder " + DATA_DIR + " -o " + CameraInit_out
    cmd += " --defaultFieldOfView 45.0"
    cmd += " --sensorDatabase " + sensor_db
    cmd += " --allowSingleView 1"
    os.system(cmd)

################################
## STEP 1: FeatureExtraction  ##
FeatureExtraction_out = SfMData + "FeatureExtraction"

def featureExtraction():
    print("\nSTEP 1: FeatureExtraction")
    cmd = av + "featureExtraction -i " + CameraInit_out + " -o " + FeatureExtraction_out
    os.system(cmd)

################################
## STEP 2: ImageMatching      ##
ImageMatching_out = SfMData + "ImageMatching.txt"

def imageMatching():
    print("\nSTEP 2: ImageMatching")
    cmd = av + "imageMatching -i " + CameraInit_out + " -o " + ImageMatching_out
    cmd += " --featuresFolders " + FeatureExtraction_out
    cmd += " --tree /home/lev/stud/PD/Alice/Meshroom-2019.2.0/aliceVision/share/aliceVision/vlfeat_K80L3.SIFT.tree"
    os.system(cmd)

################################
## STEP 3: FeatureMatching    ##

def featureMatching():
    print("\nSTEP 3: FeatureMatching")
    cmd = av + "featureMatching -i " + CameraInit_out + " -o " + FeatureMatching_out
    cmd += " --featuresFolders " + FeatureExtraction_out
    cmd += " --imagePairsList " + ImageMatching_out
    os.system(cmd)

################################
## STEP 4: StructureFromMotion##
StructureFromMotion_out = SfMData + "StructureFromMotion.sfm"

def structureFromMotion():
    print("\nSTEP 4: StructureFromMotion")
    cmd = av + "incrementalSfM -i " + CameraInit_out + " -o " + StructureFromMotion_out
    cmd += " --featuresFolders " + FeatureExtraction_out
    cmd += " --matchesFolders " + FeatureMatching_out
    os.system(cmd)


################################
## STEP 5: CameraLocalization ##
CameraLocalization_out = SfMData + "CameraLocalization.json"
CameraLocalization_abc = SfMData + "CameraLocalization.abc"

def cameraLocalization():
    print("\nSTEP 5: CameraLocalization")

    if not os.path.isfile(CameraCalibration_out):
        calibrate(CameraCalibration_out)

    cmd = av + "cameraLocalization"
    cmd += " --sfmdata " + CameraInit_out
    #cmd += " --visualDebug " + CameraLocalization_debug
    cmd += " --mediafile " + DATA_DIR
    # + "img_1.jpg"
    cmd += " --outputAlembic " + CameraLocalization_abc
    cmd += " --outputJSON " + CameraLocalization_out
    cmd += " --voctree /home/lev/stud/PD/Alice/Meshroom-2019.2.0/aliceVision/share/aliceVision/vlfeat_K80L3.SIFT.tree"
    cmd += " --calibration " + CameraCalibration_out
    cmd += " --descriptorPath " + FeatureExtraction_out
    os.system(cmd)


################################
## PIPELINE                   ##

pipeline = [
    cameraInit,
    featureExtraction,
    imageMatching,
    featureMatching,
    structureFromMotion,
    cameraLocalization
]

if len(sys.argv) > 2:
    if sys.argv[1] == "--pipeline":
        if len(sys.argv) > 3:
            for i in range(int(sys.argv[2]), int(sys.argv[3]) + 1):
                pipeline[i]()
            sys.exit()

        if len(sys.argv) == 3:
            pipeline[ int(sys.argv[2]) ]()
            sys.exit()

#for i in range(0, 5):
#    pipeline[i]()

for ff in pipeline:
    ff()
