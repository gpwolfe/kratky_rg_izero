# kratky_rg_izero
Create overlaid Kratky plots from a directory of SAXS data from [PRIMUS analysis software](https://www.embl-hamburg.de/biosaxs/primus.html),
using RG and I(0) values.
  
A part of the paper: Cotranscriptional folding of the lncRNA Xist A-repeats indicates a modular structure https://doi.org/10.1101/2022.07.26.501616
  
## Requirements
Python 3 (created using Python 3.8)

Libraries: matplotlib, pandas

Installation: pip3 install kratky_rg_izero

## Usage
Intended for use with .out files produced by PRIMUS.

Place all files for a single Kratky plot in one directory with no other .out files.

Run from command line examples:

``` bash
python3 rg_and_io.py path/to/datafiles -o save/to/dir/plotname -c red blue
```

```bash
python3 rg_and_io.py user1/saxs/exp_1 -o user1/saxs/exp_1/exp_1_kratky -c red blue
```

Output path should not include file extension. Plots will be saved in .pdf format.

If no path to data directory is given, defaults to current working directory.

Color list (`--color` or `-c`) should contain at least as many colors as there are files to be plotted. There is a default list of up to six colors that will
be used if no color list is given.
