import matplotlib.pylab as plt
import random


def plot_sample(sample, on_same_axis=False):
    '''Displays scatter plot for sample packets.
    on_same_axis controls if domain packets are grouped or not
    '''
    colors = ['b', 'g', 'r', 'c', 'y', 'k', 'm']

    groups = dict()
    for packet in sample['packets']:
        groups.setdefault(packet['domain'], []).append(packet)

    index = 0
    for group in groups.keys():
        group_items = groups[group]
        if not group_items:
            continue

        x_axis = [packet['datetime']['timestamp'] - sample['from_timestamp']
                  for packet in group_items]
        y_axis = [index] * len(group_items)

        plt.plot(x_axis, y_axis, f"{random.choice(colors)}.")
        if not on_same_axis:
            index += 1

    plt.grid()
    plt.show()
