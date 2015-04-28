# coding=utf-8
__author__ = 'nico'

import matplotlib.pyplot as plt
from random import shuffle


def parse_rr_file(rr_file):
    with open(rr_file, "rt") as f:
        rr_values = [int(l) for l in f]
        return rr_values


def parse_tag_file(tag_file):
    with open(tag_file, "rt") as f:
        tag_list = []
        next(f)  # Skipping header row
        for l in f:
            l = l.split()
            beg_list = map(float, l[0].split(":"))
            beg_seconds = beg_list[0] * 3600 + beg_list[1] * 60 + beg_list[2]
            name = l[1]
            duration_seconds = float(l[2])
            tag_list.append([beg_seconds, name, duration_seconds])
        return tag_list


def sum_up(l):
    for i in range(1, len(l)):
        l[i] += l[i - 1]
    return l


def paint(rr_file, tag_file):
    colors = ['orange', 'green', 'lightblue', 'grey', 'brown', 'red']
    shuffle(colors)
    rr_values = parse_rr_file(rr_file)
    hr_values = map(lambda x: 60 / (float(x) / 1000), rr_values)
    tag_values = parse_tag_file(tag_file)
    x = [x / 1000 for x in sum_up(rr_values)]
    y = hr_values
    plt.plot(x, y)

    for tag in tag_values:
        c = colors.pop()
        plt.axvspan(tag[0], tag[0] + tag[2], facecolor=c, alpha=.8, label=tag[1])

    plt.ylabel('Heart rate (bpm)')
    plt.xlabel('Time (s)')
    plt.ylim(ymin=min(min(y) - 10, 40), ymax=max(max(y) + 10, 150))
    plt.legend()
    plt.show()