#!/usr/bin/env python

import pipeline
import os, argparse, json
import numpy as np
import matplotlib.pyplot as plt
from numpy import savetxt
from numpy import loadtxt

D_CSV_FILE = "/measure.csv"
D_ATTEMPTS = 10
PRESETS = ["low", "medium", "normal", "high", "ultra"]
D_PRESETS = PRESETS[0:5]
D_BASE = "/tmp/BATCH_tmp/"

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--data', '-d', nargs='+')
arg_parser.add_argument('--ses', '-s', default="session_d/")
arg_parser.add_argument('--plot', '-p')
args = arg_parser.parse_args()

pipeline.silent=True


def check_poses(w_dir):
    sfm_json = w_dir + "/dataStructureFromMotion.sfm"
    dci_json = w_dir + "/dataCameraInit.sfm"
    if os.path.isfile(sfm_json):
        with open(sfm_json, "r") as read_file:
            data = json.load(read_file)
        view = len(data['views'])
        if os.path.isfile(dci_json):
            with open(dci_json, "r") as read_file:
                data = json.load(read_file)
            out = view / len(data['views'])
        else:
            out = -1
    else:
        out = 0
    return out

def plot_data(data = None, dir = None):
    if not data:
        csv = D_BASE + "session_d/" + dir + D_CSV_FILE
        if os.path.isfile(csv):
            data = loadtxt(csv, delimiter=',')
        else:
            print(csv, ": not found")
            return
    presets = D_PRESETS
    time = data[0]
    res = data[1] * 100
    pose = data[2] * 100

    fig, ax1 = plt.subplots()
#    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(12, 10)
    txtt_size = 19
    txt_size = 16
    txtl_size = 13
    line_size = 2
    marker_size = 8
    color = '#880000'
    color1 = '#2222aa'
    color2 = '#000000'
#    ax1.set_yscale('log')

    ax1.set_title(dir, fontsize=txtt_size)
    ax1.set_xlabel('Preset', fontsize=txt_size)
    ax1.set_ylabel('Time (s)', color=color, fontsize=txt_size)
    p_time = ax1.plot(presets, time, marker="s", ms=marker_size/2, color=color, lw=line_size)
    ax1.tick_params(axis='y', labelcolor=color, labelsize=txtl_size)
    ax1.tick_params(axis='x', labelsize=txtl_size)

    ax2 = ax1.twinx()
    ax2.set_ylabel('%', color=color1, fontsize=txt_size)
    p_pose = ax2.plot(presets, pose, marker="*", ms=marker_size, color=color1, lw=line_size)
    p_res =  ax2.plot(presets, res, marker=".", ms=marker_size, color=color2, lw=line_size, linestyle="--")
    ax2.tick_params(axis='y', labelcolor=color1, labelsize=txtl_size)

#    fig.legend((p_time, p_pose, p_res), ("czas wykonania", "procent wykrytych pozycji", "procent powodzenia"))
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()

def batch_run(
    data = [],
    n_attempts = D_ATTEMPTS,
    presets = D_PRESETS,
    base = D_BASE + "session_d/"
):
    for img in data:
        i_res = []
        i_time = []
        i_pose = []
        for preset in presets:
            p_res = []
            p_time = []
            p_pose = []
            print(img + "/" + preset + ": ", end = '', flush=True)
            for attempt in range(0,n_attempts):
                w_dir = base + img + "/" + preset + "/att_" + str(attempt) + "/"
                res, time_m = pipeline.pipeline(input = img, working_dir = w_dir, preset = preset)
                p_pose.append(check_poses(w_dir))
                p_res.append(int(res[4]))
                p_time.append(sum(time_m))
                print("#", end = '', flush=True)
            print("")
            i_res.append(sum(p_res)/n_attempts)
            i_time.append(sum(p_time)/n_attempts)
            i_pose.append(sum(p_pose)/n_attempts)
        data = [i_time, i_res, i_pose]
#        print("time: ", i_time)
#        print("res: ", i_res)
#        print("pose: ", i_pose)
        savetxt(base + img + D_CSV_FILE, data, delimiter=', ')

def all_f():
    data = os.listdir(D_BASE + "session_d/")
    for img in data:
        plot_data(dir=img)


if args.data:
    batch_run(data = args.data, base = D_BASE + args.ses)

if args.plot:
    plot_data(dir = args.plot)

else:
    all_f()
