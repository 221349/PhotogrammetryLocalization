import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import numpy as np

################################
## DEFAULTS:                  ##

CAM_SCALE = 0.1
CAM_ELONG = 4
MARKES_SIZE = 10
LINE_SIZE = 2


################################
## SETUP:                     ##

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X', fontsize=14)
ax.set_ylabel('Y', fontsize=14)
ax.set_zlabel('Z', fontsize=14)


################################
## OBJECTS:                   ##

class Points:
    xs = []
    ys = []
    zs = []
    cs = [[]]


################################
## TOOLS:                     ##

def add_points(
 point_size = MARKES_SIZE,
 points = Points()
):
    ax.scatter(points.xs, points.ys, points.zs, marker='o', c=points.cs, s=point_size)


def add_camera(
 name = "cam",
 scale = CAM_SCALE,
 position = [0, 0, 0],
 rotation = [1, 0, 0, 0, 1, 0, 0, 0, 1],
 elong = CAM_ELONG
):
    r_matrix = np.array([rotation[0:3], rotation[3:6], rotation[6:9]])
    v = np.array([[-1, -1, elong], [1, -1, elong], [1, 1, elong],  [-1, 1, elong], [0, 0, 0]])
    a = np.array([[1, 0, 0], [0, -1, 0], [0, 0, elong]])
    origin = np.array([0, 0, 0])
    txt_pos = np.array([0, 0, - 1])

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
    ax.text(*txt_pos, " " + name, color='#cc0000', fontsize=14)

def add_feature(
 name = "?",
 point_size = MARKES_SIZE * 10,
 cam_pos = [[0, 0, 0]],
 f_pos = [0, 0, 0],
 linestyle = '--',
 linewidth = 1,
 color = [0, 0, 0]
):
    for cam in cam_pos:
        txt_pos = f_pos
        ax.plot([cam[0], f_pos[0]],[cam[1], f_pos[1]],[cam[2], f_pos[2]], linestyle = linestyle, color=color, linewidth = linewidth)
        ax.scatter([f_pos[0]],[f_pos[1]],[f_pos[2]], marker='*', c=[color], s=point_size)
        ax.text(*txt_pos, " " + name, color='#cc00cc', fontsize=14)

def draw():
    plt.show()
    a = 0

def image(
 name = "",
 path = "",
 points = [[]],
 p_names = []
):
    img =  plt.imread(fname=path)
    figure = plt.figure()
    out = figure.add_subplot()
    plt.title(name)
    for i in range(0,len(points)):
        out.plot(points[i][0], points[i][1], marker='+', markersize=15, c='#000000', markeredgewidth=2)
        out.plot(points[i][0], points[i][1], marker='+', markersize=15, c='#ff00ff', markeredgewidth=1)
        out.plot(points[i][0], points[i][1], marker='o', markersize=15, c='#000000', markeredgewidth=2, fillstyle='none')
        out.plot(points[i][0], points[i][1], marker='o', markersize=15, c='#ff00ff', fillstyle='none')
        txt = out.text(*points[i], "  " + p_names[i], color='#ff00ff', fontsize=14, weight='light')
        txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='#000000')])
    out.imshow(img)
