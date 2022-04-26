#!/usr/bin/env python3
"""
@authors: Alisha Jones, Ph.D., Gregory Wolfe and Brian Wolfe, Ph.D.

Plot all .out file data from one directory to a single Kratky plot.

Place your .out files with distance distribution data into one folder before
running data extraction function or module from command line.

Run from command line example:
>>> python3 rg_and_io.py path/to/datafiles -o save/to/dir/plotname -c red blue
Saves plotname.pdf into directory save/to/dir.

Do not include extension in outfile filepath.
Plots will save in .pdf format.
If no data directory is given, defaults to current working directory.
A default list of plot colors is provided.

Minimal command line example (if module and data files in same directory):
Navigate to directory containing module and data files.
>>> python3 rg_and_io.py -o kratky_plot
Saves kratky_plot.pdf into current working directory.
"""

from argparse import ArgumentParser, ArgumentError
import io
import os
import re
import sys

import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd

EXP_DATA_TOP_RE = re.compile(r'\s*S\s*J EXP\s*(ERROR).*')
EXP_DATA_END_RE = re.compile(r'.*(Real\s*Space).*')
RG_RE = re.compile(
    r'\s*Real space Rg:\s+(?P<rg_val>\d+\.\d+E\+\d+)\s\+-.*')
I0_RE = re.compile(
    r'\s*Real space I\(0\):\s+(?P<i0_val>\d+\.\d+E\+\d+)\s\+-.*')


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
        if fn.endswith('.out'):
            legend_names.append('_'.join(fn.split('_')[:3]))
    for fn in os.listdir(data_dir):
        if fn.endswith('.out'):
            fns.append(os.path.join(data_dir, fn))
    return fns, legend_names


def extract_vals_data(fn):
    """Extract 'S' and 'J EXP' columns, Rg and I(0) values from data file.

    Parameters
    ----------
    fn : string
        Filename to pull 'S' and 'J EXP' columns from.

    Returns
    -------
    s_jexp_df : pandas.DataFrame
        Dataframe with 'S' and 'J EXP' columns from data file as float values.
    rg_val: float
        Value from 'Real space Rg' row of data file.
    i0_val: float
        Value from 'Real space I(0)' row of data file.
    """
    with open(fn, encoding='utf-8') as f:
        for line in f:
            rg_match_tmp = RG_RE.match(line)
            if rg_match_tmp:
                rg_match = rg_match_tmp
                break
        for line in f:
            i0_match_tmp = I0_RE.match(line)
            if i0_match_tmp:
                i0_match = i0_match_tmp
                break
        for line in f:
            if EXP_DATA_TOP_RE.match(line):
                break
        buffer = io.StringIO()
        for line in f:
            if EXP_DATA_END_RE.match(line):
                break
            buffer.write(line)

    buffer.seek(0)
    s_jexp_df = pd.read_fwf(buffer, names=['s', 'j_exp', 'error', 'j_reg',
                                           'i_reg']).dropna(how='all')[
                                               ['s', 'j_exp']].astype('float')
    rg_val = float(rg_match.group('rg_val'))
    i0_val = float(i0_match.group('i0_val'))
    return s_jexp_df, rg_val, i0_val


def plot_colors(color_str, sep=','):
    """
    Split comma-separated list of colors and check that they are valid colors.

    Raises
    ------
    ArgumentError
        Raised if color_str value is not valid.

    Returns
    -------
    values : List
        List of colors to be used for plot.

    """
    values = []
    for val in color_str.split(sep):
        if mcolors.is_color_like(val):
            values.append(val)
        else:
            raise ArgumentError(
                'Invalid color "{}". Must be a valid color.'.format(val))
    return values


def plot_rg_io(data_dir, outfile, colors):
    """Create scatterplot of overlaid values from all data files in directory.

    Pass path to directory of data to be plotted.
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
    dataframes = []
    patches = []
    fns, legend_names = gather_files_legend(data_dir)

    for filename in fns:
        s_jexp_df, rg, i0 = extract_vals_data(filename)
        s_jexp_df['j_exp_norm'] = (
            s_jexp_df['s'] * rg)**2 * (s_jexp_df['j_exp'] / i0)
        s_jexp_df['s_norm'] = s_jexp_df['s'] * rg
        dataframes.append(s_jexp_df)
    fig, ax = plt.subplots(figsize=(8, 8))

    for name, df, color in zip(legend_names, dataframes, colors):
        l, = ax.plot(df['s_norm'], df['j_exp_norm'],
                     linestyle='', marker='o', color=color)
        patches.append(mpatches.Patch(color=color, label=name))
    plt.legend(handles=patches)
    plt.hlines(y=1.1, xmin=0, xmax=1.7, colors='cyan', linestyles='--', lw=2)
    plt.vlines(x=1.7, ymin=0, ymax=1.1, colors='cyan', linestyles='--', lw=2)
    plt.savefig(outfile + '.pdf')


def rg_i0(argv):
    """Run data file reading and plotting from command line.

    Example use:
    >>> python3 RG_and_IO.py my/data/dir -o save/to/file -c red blue
    """
    parser = ArgumentParser(description='Create scatterplot of data.')
    parser.add_argument('mydir', nargs='?', metavar='DIR',
                        help='Path to directory containing data',
                        default=os.getcwd())
    parser.add_argument('--outfile', '-o',
                        help='Filepath including filename for plot, no ext.')
    parser.add_argument('--colors', '-c',
                        help='Comma-separated colors for scatterplot',
                        type=plot_colors,
                        default=['#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
                                 '#984ea3', '#ffff33'])
    args = parser.parse_args(argv)
    mydir = args.mydir
    outfile = args.outfile
    colors = args.colors
    plot_rg_io(mydir, outfile, colors)


if __name__ == '__main__':
    rg_i0(sys.argv[1:])
