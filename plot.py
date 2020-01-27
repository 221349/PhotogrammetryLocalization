#!/usr/bin/env python
from mpl_toolkits.mplot3d import Axes3D

import os, sys
import argparse
import json
import string

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import numpy as np

import scene

################################
## DEFAULTS:                  ##

JSON_FILE = "/tmp/AV_tmp/dataStructureFromMotion.sfm"
CAM_SCALE = 0.1
CAM_ELONG = 4
MARKES_SIZE = 10

MIN_VIEWS_PER_FEATURE = 2

select_pose = False
positions = []

################################
## ARGS:                      ##

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--input', '-i', default=JSON_FILE)
arg_parser.add_argument('--select_pose', nargs='+')
arg_parser.add_argument('--cam_scale', default=CAM_SCALE)
arg_parser.add_argument('--cam_elong', default=CAM_ELONG)
arg_parser.add_argument('--marker_size', default=MARKES_SIZE)

args = arg_parser.parse_args()

if args.input: input_json = args.input
if args.cam_scale: cam_scale = args.cam_scale
if args.cam_elong: cam_elong = args.cam_elong
if args.marker_size: marker_size = args.marker_size
if args.select_pose:
    select_pose = True
    positions = args.select_pose


################################
## SETUP:                     ##

with open(input_json, "r") as read_file:
    data = json.load(read_file)

################################
## :                     ##

class Feature:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.pos = [0, 0, 0]
        self.color = [0, 0, 0]
        self.views = []
        self.views_pos = []

    def print(self):
        print("id: ", self.id)
        print("name: ", self.name)
        print("pos: ", self.pos)
        print("color: ", self.color)
        print("views: ", self.views)
        print("views_pos: ", self.views_pos)


class Camera:
    def __init__(self, sfm_pose):
        self.id = sfm_pose['poseId']
        self.rot = [float(item) for item in sfm_pose['pose']['transform']['rotation']]
        self.pos = [float(item) for item in sfm_pose['pose']['transform']['center']]
        for item in data['views']:
            if item['poseId'] == self.id:
                self.path = item['path']
                self.name = os.path.basename(self.path)
                break

class Views:
    cameras = []
    def __init__(self):
        for item in data['poses']:
            camera = Camera(item)
            if select_pose:
                if any(pose_name in camera.name for pose_name in positions):
                    self.cameras.append(camera)
            else:
                self.cameras.append(camera)

    def select_by_name(self, name):
        for item in self.cameras:
            if name in item.name:
                return item

    def select_by_id(self, id):
        for item in self.cameras:
            if id in item.id:
                return item

    def plot_cameras(self):
        for item in self.cameras:
            scene.add_camera(
             scale = cam_scale,
             elong = cam_elong,
             position = item.pos,
             rotation = item.rot,
             name = item.name
            )

views = Views()

class Features():
    features = []
    def __init__(self, number = 1, min_views = MIN_VIEWS_PER_FEATURE):
        for item in data['structure']:
            view = 0
            feature = Feature()
            for observation in item['observations']:
                if views.select_by_id(observation['observationId']):
                    view = view + 1
                    feature.views.append(observation['observationId'])
                    feature.views_pos.append([float(x) for x in observation['x']] )
            if view >= min_views:
                feature.id = item['landmarkId']
                feature.name = string.ascii_uppercase[len(self.features)]
                feature.pos = [float(x) for x in item['X']]
                feature.color = [float(col_item)/256 for col_item in item['color'] ]
                self.features.append(feature)
            if len(self.features) >= number:
                break

    def plot_features(self):
        for item in self.features:
            cameras = []
            for cam in item.views:
                cameras.append( views.select_by_id(cam).pos )
            scene.add_feature(
             cam_pos = cameras,
             f_pos = item.pos,
             color = item.color,
             name = item.name,
             point_size = marker_size * 10)

features = Features(number = 2, min_views = 2)

features.plot_features()



def add_rays(
 f_number
):
    z = [0, 1]
    print(z)
    ax.plot(z, z, z)


################################
## PLOT:                      ##

features = scene.Points()
features.xs = [float(item['X'][0]) for item in data['structure']]
features.ys = [float(item['X'][1]) for item in data['structure']]
features.zs = [float(item['X'][2]) for item in data['structure']]
features.cs = [[float(col_item)/256 for col_item in item['color'] ] for item in data['structure']]

scene.add_points(points = features, point_size=marker_size)

views.plot_cameras()

scene.draw()
