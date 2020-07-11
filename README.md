# osmnx-color-roads
Quickly generate maps of road networks coloured by words in road names

## What it does

* Gets the OSM graph for a given place
* Finds the most common words used in the graph
* Generates a colour scheme based on the common words
* Tries to ensure that the most common words have visually distinct colours
* Allows for stop words (TODO: Improve this system)
* Allows for a single line query to generate a map and allows for osmnx optional
  parameters, e.g. dpi, etc.

## Installation

`osmnx-color-roads` requires `osmnx` which has a long list of dependencies. The fastest way to get started is to use [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html) to manage your Python environment and dependencies for osmnx.

1. Install conda
2. ```
   conda config --prepend channels conda-forge
   conda create -n ox --strict-channel-priority osmnx
   ```
3. 
   `conda activate ox`
4. Run your python program that imports osmnx-color-roads

*Warning: conda will clash with Pyenv - [this StackOverflow can help](https://stackoverflow.com/questions/57640272/how-can-i-install-anaconda-aside-an-existing-pyenv-installation-on-osx)* 

## Example usage:
```
from  osmnx_color_roads import generate_image

generate_image('Oahu, Mililani, Honolulu County, Hawaii, United States of America', query_type='string', key_size=9, line_width=0.5)
```

## Inspiration
Inspiration and original code from Giuseppe Sollazzo @puntofisso
-> https://twitter.com/puntofisso/status/1213135545121099777?s=20

Building on work by Cédric Scherer @CedScherer and @erdavis

#mapgeek #gis #osmnx #opensource #visualization #python #mapvisualization

https://twitter.com/gboeing
https://twitter.com/openstreetmap

