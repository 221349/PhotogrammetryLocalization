#!/usr/bin/env python
from mpl_toolkits.mplot3d import Axes3D

import os, sys
import json

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import numpy as np

#JSON_FILE = "/tmp/AV_tmp/ex.json"
JSON_FILE = "/tmp/AV_tmp/dataStructureFromMotion.sfm"

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
#ax.set_aspect('equal')

def add_camera(
 name = "cam",
 scale = 1,
 position = [0, 0, 0],
 rotation = [1, 0, 0, 0, 1, 0, 0, 0, 1],
 elong = 4
 ):
    r_matrix = np.array([rotation[0:3], rotation[3:6], rotation[6:9]])
    v = np.array([[-1, -1, 0], [1, -1, 0], [1, 1, 0],  [-1, 1, 0], [0, 0, -elong]])
    a = np.array([[1, 0, 0], [0, -1, 0], [0, 0, elong]])
    origin = np.array([0, 0, -elong])
    txt_pos = np.array([0, 0, -elong - 1])

    v = np.array([np.dot(r_matrix, item) for item in v]) * scale + position
    a = np.array([np.dot(r_matrix, item) for item in a]) * scale
    origin = np.dot(r_matrix, origin) * scale + position
    txt_pos = np.dot(r_matrix, txt_pos) * scale + position

    cam = [ [v[0],v[1],v[4]], [v[0],v[3],v[4]], [v[2],v[1],v[4]], [v[2],v[3],v[4]]]
    cam_face = [[v[0],v[1],v[2],v[3]]]

    ax.quiver(*origin, a[:,0], a[:,1], a[:,2], color='b')
    ax.scatter3D(v[:, 0], v[:, 1], v[:, 2], marker='None')
    ax.add_collection3d(Poly3DCollection(cam, facecolors='#00ff00', linewidths=1, edgecolors='r', alpha=.25))
    ax.add_collection3d(Poly3DCollection(cam_face, facecolors='#ffff00', linewidths=1, edgecolors='r', alpha=.5))
    ax.text(*txt_pos, name, color='#cc0000')



with open(JSON_FILE, "r") as read_file:
    data = json.load(read_file)

xs = [float(item['X'][0]) for item in data['structure']]
ys = [float(item['X'][1]) for item in data['structure']]
zs = [float(item['X'][2]) for item in data['structure']]
cs = [[float(col_item)/256 for col_item in item['color'] ] for item in data['structure']]

ax.scatter(xs, ys, zs, marker='o', c=cs)

names = {}
for item in data['views']:
    names[item['poseId']] = os.path.basename(item['path'])

for camera in data['poses']:
    rot = [float(item) for item in camera['pose']['transform']['rotation']]
    pos = [float(item) for item in camera['pose']['transform']['center']]
    id = camera['poseId']
    add_camera(scale = 0.2, position = pos, rotation = rot, name = names[id])


ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

plt.show()
