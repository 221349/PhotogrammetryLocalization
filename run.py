#!/usr/bin/env python

import pipeline
import argparse


################################
## Config:                    ##
D_DESCRIBER_TYPE = "sift"
"""
    * sift:         Scale-invariant feature transform.
    * sift_float:   SIFT stored as float.
    * sift_upright: SIFT with upright feature.
    * akaze:        A-KAZE with floating point descriptors.
    * akaze_liop:   A-KAZE with Local Intensity Order Pattern descriptors.
    * akaze_mldb:   A-KAZE with Modified-Local Difference Binary descriptors.
    * cctag3:       Concentric circles markers with 3 crowns.
    * cctag4:       Concentric circles markers with 4 crowns.
    * akaze_ocv:    OpenCV implementation of A-KAZE describer.
"""
D_DESCRIBER_PRESET = "normal" # low, medium, normal, high, ultra
D_MAX_DESCRIPTORS = "500"
D_N_MATCHES = "50"


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--input', '-i')
arg_parser.add_argument('--describer_preset', '-p', default=D_DESCRIBER_PRESET)
arg_parser.add_argument('--describer_type', '-t', default=D_DESCRIBER_TYPE)
arg_parser.add_argument('--max_descriptors', '-d', default=D_MAX_DESCRIPTORS)
arg_parser.add_argument('--n_matches', '-n', default=D_N_MATCHES)
arg_parser.add_argument('--skip_ImageMatching', '-s', action='store_true')
args = arg_parser.parse_args()

if args.input:
    pipeline.pipeline(
     input = args.input,
     preset = args.describer_preset,
     max_descriptors = args.max_descriptors,
     n_matches = args.n_matches,
     skip_ImageMatching = args.skip_ImageMatching,
     describer_type = args.describer_type
    )
