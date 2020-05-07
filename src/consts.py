import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


def cmap(n, base='tab20'):
    base = plt.cm.get_cmap(base)
    cmaplist = base(np.linspace(0, 1, n))
    return mcolors.LinearSegmentedColormap.from_list(None, cmaplist, n)


topics = [
    'Pandemic',
    'Health',
    'Economics',
    'Politics',
    'Religion',
    'Education',
    'Entertainment'
]

colormap = cmap(len(topics))
colors = {t: colormap(i) for i, t in enumerate(topics)}
