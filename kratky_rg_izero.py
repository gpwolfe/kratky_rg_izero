#!/usr/bin/env python3
"""
Created on Mon Feb 15 14:02:58 2021
@authors: gregory wolfe, jonesy jones, and brian wolfe
Put your .out files from the distance distribution in one folder.
This plots all data from one directory to a single Kratky plot.

Run from command line example:
>>> python3 rg_and_io.py path/to/datafiles -o save/to/dir/plotname -c red blue
"""
from argparse import ArgumentParser
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys

LEGEND_NAMES = []
FILES = []


def gather_files_legend(mydir):
    """Populate lists of file names and names for plot legend.

    Parameters
    ----------
    mydir : string
        Path to directory containing files to be plotted.

    Returns
    -------
    None.

    """
    for file in os.listdir(mydir):
        if file.endswith(".out"):
            LEGEND_NAMES.append('_'.join(file.split('_')[:3]))
    for file in os.listdir(mydir):
        if file.endswith(".out"):
            FILES.append(os.path.join(mydir, file))


def S_I(filename):
    """Extract 'S' and 'J EXP' columns from data file.

    Parameters
    ----------
    filename : string
        Filename to pull 'S' and 'J EXP' columns from.

    Returns
    -------
    data : pandas.DataFrame
        Dataframe with columns of data from 'S' and 'J EXP'.

    """
    data_pre = pd.read_table(filename, names=['data'], sep='\n',
                             skip_blank_lines=False).dropna()
    stop = data_pre[data_pre.data.str.contains(
        pat='\s*Real\s*Space', case=True)].index.to_list()[0] - 2
    start = (data_pre[data_pre.data.str.contains(
        pat='\s*S\s*J EXP\s*(ERROR)', case=True)].index.to_list()[0] + 1)
    data = pd.read_fwf(filename, engine='python',
                       skiprows=start, nrows=stop-start,
                       names=['S', 'J EXP', 'ERROR', 'J REG', 'I REG'])
    data = data[['S', 'J EXP']].astype('float')
    return data


def real_space_Rg(filename):
    """Extract RG value from data file.

    Parameters
    ----------
    filename : string
        Filename to pull Real Space RG data from.

    Returns
    -------
    rg : float
        RG value from data file.

    """
    with open(filename) as f:
        for line in f:
            if 'Real space Rg' in line:
                rg = float(line.split()[3])
                return rg


def real_space_I0(filename):
    """Extract Real Space I(0) data from data file.

    Parameters
    ----------
    filename : string
        Filename to pull Real Space I(0) data from.

    Returns
    -------
    i0 : float
        I(0) value from data file.

    """
    with open(filename) as f:
        for line in f:
            if 'Real space I(0)' in line:
                i0 = float(line.split()[3])
                return i0


def plot_rg_io(o_file, colors):
    """Create scatterplot of overlaid values from all data files in directory.

    Pass filepath to which plot should be saved, excluding extension. Plot
    will be saved as .PDF.
    Pass colors as a list of strings. Can be any color values recognized by
    matplotlib, including standard colors (e.g. ['red', 'blue']) or
    hexadecimal values.

    Parameters
    ----------
    o_file : string
        Filepath to save plot, excluding extension.
    colors : list of strings
        List of colors to pass to scatterplot function.

    Returns
    -------
    None.

    """
    RGs = []
    I0s = []
    dataframes = []
    patches = []

    for filename in FILES:
        Iof0 = real_space_I0(filename)
        I0s.append(Iof0)
        Rg = real_space_Rg(filename)
        RGs.append(Rg)
        mydf = S_I(filename)
        mydf['new_column'] = (mydf['S'] * Rg)**2 * (mydf['J EXP'] / Iof0)
        # mydf['new_column2'] = mydf['new_column'] / Iof0
        mydf['new_column3'] = mydf['S'] * Rg
        dataframes.append(mydf)
    fig, ax = plt.subplots(figsize=(8, 8))

    for name, df, color in zip(LEGEND_NAMES, dataframes, colors):
        l, = ax.plot(df['new_column3'], df['new_column'],
                     linestyle="", marker="o", color=color)
        patches.append(mpatches.Patch(color=color, label=name))
        # ax.set_xlim(0,25)
        # plt.plot(df['new_column3'], df['new_column2'],
        # linestyle="",marker="o")
    plt.legend(handles=patches)
    plt.hlines(y=1.1, xmin=0, xmax=1.7, colors='cyan', linestyles='--', lw=2)
    plt.vlines(x=1.7, ymin=0, ymax=1.1, colors='cyan', linestyles='--', lw=2)
    plt.savefig(o_file + '.pdf')


def rg_i0(argv):
    """Run data file reading and plotting from command line.

    Example use:
    >>> python3 RG_and_IO.py my/data/dir -o save/to/file -c red blue
    """
    parser = ArgumentParser(description="Create scatterplot of data.")
    parser.add_argument('mydir', metavar='DIR',
                        help='Path to directory containing data',
                        default=os.getcwd())
    parser.add_argument('-outfile', '-o',
                        help='Filepath including filename for plot, no ext.')
    parser.add_argument('-colors', '-c', nargs='+',
                        help="Colors for scatterplot",
                        default=['#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
                                 '#984ea3', '#ffff33'])
    args = parser.parse_args(argv)
    mydir = args.mydir
    outfile = args.outfile
    colors = args.colors
    gather_files_legend(mydir)
    plot_rg_io(outfile, colors)


if __name__ == '__main__':
    rg_i0(sys.argv[1:])
