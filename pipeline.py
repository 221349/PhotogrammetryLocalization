#!/usr/bin/env python

import os, sys, argparse, time

################################
## Config:                    ##
AV_DIR = "../Alice/Meshroom-2019.2.0/aliceVision/"
SFMDATA_FILENAME = "data"

D_VERBOSE_LEVEL = "info" #fatal, error, warning, info, debug, trace
D_LOG_DIR = "/tmp/AV_tmp/logs/"

## STEP 0: CameraInit         ##
D_FIELD_OF_VIEW = "56.0"
SENSOR_DB = AV_DIR + "share/aliceVision/cameraSensors.db"
## STEP 1: FeatureExtraction  ##
D_DESCRIBER_TYPE = "sift"
D_DESCRIBER_PRESET = "normal" # low, medium, normal, high, ultra
## STEP 2: ImageMatching      ##
VOCABULARY_TREE = AV_DIR + "share/aliceVision/vlfeat_K80L3.SIFT.tree"
D_MAX_DESCRIPTORS = "500"
D_N_MATCHES = "50"

################################
## Setup:                     ##
os.environ['LD_LIBRARY_PATH'] = AV_DIR + "lib/"

av = AV_DIR + "bin/aliceVision_"


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--input', '-i', default="")
arg_parser.add_argument('--describer_preset', '-p', default=D_DESCRIBER_PRESET)
arg_parser.add_argument('--max_descriptors', '-d', default=D_MAX_DESCRIPTORS)
arg_parser.add_argument('--n_matches', '-n', default=D_N_MATCHES)
arg_parser.add_argument('--skip_ImageMatching', '-s', action='store_true')
args = arg_parser.parse_args()

################################
## Run:                       ##
def run(name, cmd, v_level, log_dir):
    cmd += " -v " + v_level
    cmd += " &> " + log_dir + name
    print("STEP " + name)
    out = os.system(cmd)
    if out:
        print("ERROR: from " + name)
    return out

################################
## STEP 0: CameraInit         ##
def cameraInit(
 data_dir,
 cameraInit_file,
 fieldOfView = D_FIELD_OF_VIEW,
 v_level = D_VERBOSE_LEVEL,
 log_dir = D_LOG_DIR
):
    cmd = av + "cameraInit --imageFolder " + data_dir + " -o " + cameraInit_file
    cmd += " --defaultFieldOfView " + fieldOfView
    cmd += " --sensorDatabase " + SENSOR_DB
#    cmd += " --allowSingleView 1"
    return run("0_CameraInit", cmd, v_level, log_dir)

################################
## STEP 1: FeatureExtraction  ##
def featureExtraction(
 cameraInit_file,
 featureExtraction_dir,
 describerType = D_DESCRIBER_TYPE,
 describerPreset = D_DESCRIBER_PRESET,
 v_level = D_VERBOSE_LEVEL,
 log_dir = D_LOG_DIR
):
    cmd = av + "featureExtraction -i " + cameraInit_file + " -o " + featureExtraction_dir
    cmd += " -p " + describerPreset
    cmd += " -d " + describerType
    return run("1_FeatureExtraction", cmd, v_level, log_dir)

################################
## STEP 2: ImageMatching      ##
def imageMatching(
 cameraInit_file,
 featureExtraction_dir,
 imageMatching_file,
 maxDescriptors = D_MAX_DESCRIPTORS,
 matchNnumber = D_N_MATCHES,
 v_level = D_VERBOSE_LEVEL,
 log_dir = D_LOG_DIR
):
    cmd = av + "imageMatching -i " + cameraInit_file + " -o " + imageMatching_file
    cmd += " --featuresFolders " + featureExtraction_dir
    cmd += " --tree " + VOCABULARY_TREE
    cmd += " --maxDescriptors " + maxDescriptors
    cmd += " --nbMatches " + matchNnumber
    return run("2_ImageMatching", cmd, v_level, log_dir)

################################
## STEP 3: FeatureMatching    ##
def featureMatching(
 cameraInit_file,
 featureExtraction_dir,
 featureMatching_dir,
 imageMatching_file,
 v_level = D_VERBOSE_LEVEL,
 log_dir = D_LOG_DIR
):
    if not os.path.isdir(featureMatching_dir):
        os.mkdir(featureMatching_dir)

    cmd = av + "featureMatching -i " + cameraInit_file + " -o " + featureMatching_dir
    cmd += " --featuresFolders " + featureExtraction_dir
    if imageMatching_file:
        cmd += " --imagePairsList " + imageMatching_file
    return run("3_FeatureMatching", cmd, v_level, log_dir)

################################
## STEP 4: StructureFromMotion##
def structureFromMotion(
 cameraInit_file,
 featureExtraction_dir,
 featureMatching_dir,
 sfm_file,
 v_level = D_VERBOSE_LEVEL,
 log_dir = D_LOG_DIR
):
    cmd = av + "incrementalSfM -i " + cameraInit_file + " -o " + sfm_file
    cmd += " --featuresFolders " + featureExtraction_dir
    cmd += " --matchesFolders " + featureMatching_dir
    return run("4_StructureFromMotion", cmd, v_level, log_dir)


################################
## PIPELINE                   ##

def pipeline(input, preset, max_descriptors, n_matches, skip_ImageMatching = True):
    working_dir = "/tmp/AV_tmp/" + input
    if not os.path.isdir(working_dir):
        os.makedirs(working_dir, exist_ok=True)
    SfMData = working_dir + SFMDATA_FILENAME
    log_dir = working_dir + "logs/"
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    input = "/home/lev/stud/PD/PhotogrammetryLocalization/data/" + input

    cameraInit_file = SfMData + "CameraInit.sfm"
    cameraInit(data_dir = input, cameraInit_file = cameraInit_file, log_dir = log_dir)
    time.sleep(1)

    featureExtraction_dir = SfMData + "FeatureExtraction"
    featureExtraction(cameraInit_file = cameraInit_file, featureExtraction_dir = featureExtraction_dir, describerPreset = preset, log_dir = log_dir)
    time.sleep(1)

    if skip_ImageMatching:
        imageMatching_file = False
    else:
        imageMatching_file = SfMData + "ImageMatching.txt"
        imageMatching(cameraInit_file = cameraInit_file, featureExtraction_dir = featureExtraction_dir, imageMatching_file = imageMatching_file, maxDescriptors = max_descriptors, matchNnumber = n_matches, log_dir = log_dir)
        time.sleep(1)

    featureMatching_dir = SfMData + "FeatureMatching"
    featureMatching(cameraInit_file = cameraInit_file, featureExtraction_dir = featureExtraction_dir, imageMatching_file = imageMatching_file, featureMatching_dir = featureMatching_dir, log_dir = log_dir)
    time.sleep(5)

    sfm_file = SfMData + "StructureFromMotion.sfm"
    structureFromMotion(cameraInit_file = cameraInit_file, featureExtraction_dir = featureExtraction_dir, featureMatching_dir = featureMatching_dir, sfm_file = sfm_file, log_dir = log_dir)

pipeline(args.input, args.describer_preset, args.max_descriptors, args.n_matches, args.skip_ImageMatching)
