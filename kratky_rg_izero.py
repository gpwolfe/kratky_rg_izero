#!/usr/bin/env python3
"""
Created on Mon Feb 15 14:02:58 2021
@authors: Alisha Jones, Ph.D., Gregory Wolfe and Brian Wolfe, Ph.D.
Put your .out files from the distance distribution in one folder.
This plots all data from one directory to a single Kratky plot.

Run from command line example:
>>> python3 rg_and_io.py path/to/datafiles -o save/to/dir/plotname -c red blue
"""

from argparse import ArgumentParser
import os
import sys

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd


def gather_files_legend(data_dir):
    """Populate lists of file names and names for plot legend.

    Parameters
    ----------
    data_dir : string
        Path to directory containing files to be plotted.

    Returns
    -------
    fns : list
        List of file names.
    legend_names : list
        List of names for plot legend.
    """
    fns = []
    legend_names = []
    for fn in os.listdir(data_dir):
        if fn.endswith(".out"):
            legend_names.append('_'.join(fn.split('_')[:3]))
    for fn in os.listdir(data_dir):
        if fn.endswith(".out"):
            fns.append(os.path.join(data_dir, fn))
    return fns, legend_names


def get_s_i(fn):
    """Extract 'S' and 'J EXP' columns from data file.

    Parameters
    ----------
    fn : string
        Filename to pull 'S' and 'J EXP' columns from.

    Returns
    -------
    s_i_data : pandas.DataFrame
        Dataframe with columns of data from 'S' and 'J EXP'.

    """
    data_find = pd.read_table(fn, names=['data'], sep='\n',
                              skip_blank_lines=False).dropna()
    stop = data_find[data_find.data.str.contains(
        pat='\s*Real\s*Space', case=True)].index.to_list()[0] - 2
    start = (data_find[data_find.data.str.contains(
        pat='\s*S\s*J EXP\s*(ERROR)', case=True)].index.to_list()[0] + 1)
    s_i_data = pd.read_fwf(fn, engine='python',
                           skiprows=start, nrows=stop-start,
                           names=['S', 'J EXP', 'ERROR', 'J REG', 'I REG'])
    s_i_data = s_i_data[['S', 'J EXP']].astype('float')
    return s_i_data


def real_space_rg(fn):
    """Extract Rg value from data file.

    Parameters
    ----------
    fn : string
        Filename to pull Real Space Rg data from.

    Returns
    -------
    rg : float
        Rg value from data file.

    """
    with open(fn) as f:
        for line in f:
            if 'Real space Rg' in line:
                rg = float(line.split()[3])
                return rg


def real_space_io(fn):
    """Extract Real Space I(0) data from data file.

    Parameters
    ----------
    fn : string
        Filename to pull Real Space I(0) data from.

    Returns
    -------
    i0 : float
        I(0) value from data file.

    """
    with open(fn) as f:
        for line in f:
            if 'Real space I(0)' in line:
                i0 = float(line.split()[3])
                return i0


def plot_rg_io(data_dir, outfile, colors):
    """Create scatterplot of overlaid values from all data files in directory.

    Pass filepath to which plot should be saved, excluding extension. Plot
    will be saved as .PDF.
    Pass colors as a list of strings. Can be any color values recognized by
    matplotlib, including standard colors (e.g. ['red', 'blue']) or
    hexadecimal values (e.g. ['#4daf4a', '#377eb8'].

    Parameters
    ----------
    data_dir: string
        Path to directory containing data files.
    outfile : string
        Filepath to save plot, excluding extension.
    colors : list of strings
        List of colors to pass to scatterplot function.

    Returns
    -------
    None.

    """
    rgs = []
    i0s = []
    dataframes = []
    patches = []
    fns, legend_names = gather_files_legend(data_dir)

    for filename in fns:
        i0 = real_space_io(filename)
        i0s.append(i0)
        rg = real_space_rg(filename)
        rgs.append(rg)
        df_s_i = get_s_i(filename)
        df_s_i['new_column'] = (
            df_s_i['S'] * rg)**2 * (df_s_i['J EXP'] / i0)
        # df_s_i['new_column2'] = df_s_i['new_column'] / i0
        df_s_i['new_column3'] = df_s_i['S'] * rg
        dataframes.append(df_s_i)
    fig, ax = plt.subplots(figsize=(8, 8))

    for name, df, color in zip(legend_names, dataframes, colors):
        l, = ax.plot(df['new_column3'], df['new_column'],
                     linestyle="", marker="o", color=color)
        patches.append(mpatches.Patch(color=color, label=name))
        # ax.set_xlim(0,25)
        # plt.plot(df['new_column3'], df['new_column2'],
        # linestyle="",marker="o")
    plt.legend(handles=patches)
    plt.hlines(y=1.1, xmin=0, xmax=1.7, colors='cyan', linestyles='--', lw=2)
    plt.vlines(x=1.7, ymin=0, ymax=1.1, colors='cyan', linestyles='--', lw=2)
    plt.savefig(outfile + '.pdf')


def rg_i0(argv):
    """Run data file reading and plotting from command line.

    Example use:
    >>> python3 RG_and_IO.py my/data/dir -o save/to/file -c red blue
    """
    parser = ArgumentParser(description="Create scatterplot of data.")
    parser.add_argument('mydir', metavar='DIR',
                        help='Path to directory containing data',
                        default=os.getcwd())
    parser.add_argument('--outfile', '-o',
                        help='Filepath including filename for plot, no ext.')
    parser.add_argument('--colors', '-c', nargs='+',
                        help="Colors for scatterplot",
                        default=['#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
                                 '#984ea3', '#ffff33'])
    args = parser.parse_args(argv)
    mydir = args.mydir
    outfile = args.outfile
    colors = args.colors
    plot_rg_io(mydir, outfile, colors)


if __name__ == '__main__':
    rg_i0(sys.argv[1:])
