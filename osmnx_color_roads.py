"""
Generate map images against OSM travel network graphs.
* Finds the most common words used in the graph
* Generates a colour scheme based on the common words
* Ensures that the most common words have visually distinct colours
* Allows for stop words (TODO: Improve this system)
* Allows for a single line query to generate a map and allows for optional
  parameters, e.g. dpi, etc.

10 July 2020 - Tim Fernando
Inspiration and original code from Giuseppe Sollazzo @puntofisso
-> https://twitter.com/puntofisso/status/1213135545121099777?s=20

Building on work by Cédric Scherer @CedScherer and @erdavis

#mapgeek #gis #osmnx #opensource #visualization #python #mapvisualization

https://twitter.com/gboeing
https://twitter.com/openstreetmap

Example usage:

generate_image('Oahu, Mililani, Honolulu County, Hawaii, United States of America', query_type='string', key_size=9, line_width=0.5)
"""

import json
from collections import Counter, defaultdict

import osmnx as ox
import seaborn as sns

ox.config(log_console=True, use_cache=True)

"""
TODO: Come up with a more elegant way of handling stop words
"""
STOP_WORDS = [
                'the', 'le',
                # Hong Kong
                'hong', 'west', 'central', 'wan', 'tai', 'shing', 'tung',
                'wong', 'man', 'fu', 'queen\'s', 'kong', 'hing', 'mount',
                # Sri Lanka
                'sri', 'galle', 'de', 'perera', 'marine',
                # Barbados
                'main', 'hall', 'park', 'gap', 'no', 'rock', 'land',
                'tenantry', 'view', 'village', 'bay',
                # Havana
                'del',
                # Numbers
                '1er', '5ta',  # Havana
                '1st', '2nd', '3rd', '4th', '5th',
                '1ro', '2do', '3ro', '4to', '5to',
                '1º', '2º', '3º', '4º', '5º',
                'san', 'market',
                'kamehameha',  # Hawaii,
                'tuas', 'bukit',  # Singapore,
                'mission',  # San Francisco
             ]


def palette_generator(items):
    """
    Generate a list of colors against 'husl' color separation
    against the number of keys given
    """
    palette = sns.husl_palette(len(items))
    # Convert colors from decimal to 0-255
    rgb_palette = [tuple(int(255 * channel) for channel in color)
                   for color in palette]
    # Convert to hex code and return
    hex_palette = ['#%02x%02x%02x' % color for color in rgb_palette]

    # Add distance between the colours by splitting the list and zipping them
    middle_index = len(items) // 2
    keys = []
    item_keys = list(items.keys())
    for i in range(middle_index):
        keys.append(item_keys[i])
        keys.append(item_keys[middle_index + i])
    if len(items) % 2:
        keys.append(item_keys[-1])

    print(items)
    palette_key = dict(zip(keys, hex_palette))
    print(palette_key)
    return palette_key


def color_for_road(road_name, palette_key):
    """
    Take a road string, the language and return a color
    """
    road_name = str(road_name).lower()
    # Check if any of the palette keys are present in the road name
    for key in palette_key:
        if key in road_name:
            return palette_key[key]
    return "#c6c6c6"  # Default color


def find_common_words(edges):
    """
    Find the most common words in the graph
    Return a dictionary with word: number of occurences
    """
    # Get all the words in the given edges
    occurrences = defaultdict(int)
    for _, row in edges.iterrows():
        # We seem to get 'NaN' for empty fields in this data
        # ignoring floats as a result
        if type(row['name']) is float:
            continue
        words = str(row['name']).split(' ')
        valid_words = (word.lower() for word in words
                       if word.lower() not in STOP_WORDS and
                       len(word) > 1 and
                       not word.isdigit())
        for word in valid_words:
            occurrences[word] += 1
    return occurrences


def get_data_point(lat_lon, radius, network_type):
    """
    Get the graph for a given lat, lon and radius
    Keep trying different results incase no Polygons returned
    """
    graph = ox.graph_from_point(lat_lon, dist=radius,
                                network_type=network_type,
                                clean_periphery=True, retain_all=True)
    return graph


def get_data(place, which_result, network_type):
    """
    Get the graph for a given place
    Keep trying different results incase no Polygons returned
    """
    graph = None
    while graph is None:
        try:
            print(f'Place name query using which_result={which_result}')
            graph = ox.graph_from_place(place, network_type=network_type,
                                        which_result=which_result,
                                        clean_periphery=True, retain_all=True)
        except (TypeError, KeyError):
            if which_result > 9:
                raise TypeError
            print(f'Failed to get result with which_result={which_result}')
            #  The result isn't a polygon or multipolygon,
            #  try using a different result
            #  NB This is pretty crude and due to the fact that osmnx doesn't
            #  seem to allow a smarter way of searching using this API
            which_result += 1
    return graph


def generate_image(place, **kwargs):
    """
    Generate an image and palette key for a given place
    * Get data for given name
    * Find most common words in road names (e.g. 'street')
    * Generate a palette and key for the most common words
    * Generate a colorized map with road names
    """
    which_result = kwargs.get('which_result', 1)
    key_size = kwargs.get('key_size', 6)
    query_type = kwargs.get('query_type', 'string')
    line_width = kwargs.get('line_width', 1)
    dpi = kwargs.get('dpi', 300)
    network_type = kwargs.get('network_type', 'all')

    # Convert place name to valid filenames
    if query_type == 'place':
        place_name = " ".join(place.values())
    elif query_type == 'point':
        # We're expecting a tuple of ('Place name', (lat, lon), radius)
        place_name = place[0]
    else:  # String
        place_name = place

    filename = "".join([c for c in place_name
                        if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    image_filename = f'output/{filename}.png'
    palette_filename = f'output/{filename}.json'

    if query_type == 'point':
        graph = get_data_point(place[1], place[2], network_type)
    else:
        graph = get_data(place, which_result, network_type)

    # Get the metadata from the graph edges
    edge_attributes = ox.graph_to_gdfs(graph, nodes=False)

    # Find the most popular words in the names,
    # these should be things like 'road', 'street' etc
    popular_words = find_common_words(edge_attributes)
    top = dict(Counter(popular_words).most_common(key_size))
    print(f'Top words: {top}')

    palette_key = palette_generator(top)
    edge_colors = [color_for_road(row['name'], palette_key)
                   for _, row in edge_attributes.iterrows()]

    # Draw the plot
    fig, ax = ox.plot_graph(graph, bgcolor='white', node_size=0,
                            node_color='w', node_edgecolor='gray',
                            node_zorder=2, edge_color=edge_colors,
                            edge_linewidth=line_width, edge_alpha=0.98,
                            figsize=(20, 20), dpi=dpi, save=True,
                            filepath=image_filename)

    # Save the palette key
    with open(palette_filename, 'w+') as out:
        json.dump(palette_key, out)

    return top, popular_words, palette_key
