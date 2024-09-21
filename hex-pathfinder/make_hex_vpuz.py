# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 15:41:28 2024

@author: Alex Boisvert
"""

import matplotlib.pyplot as plt
import numpy as np
import math
import io
import base64
from PIL import Image
from collections import Counter

# Helper function to convert original Cartesian coordinates to axial
def cartesian_to_axial(row, col):
    # Row is easy: 0 -> 7, 14 -> -7
    q = 7 - row
    if row <= 7:
        r = col - 7
    else:
        r = col + (row - 14)
    return (q, r)

#END cartesian_to_axial()

# Helper function to get the direction from a path
def path_to_direction(path):
    path0, path1 = path[0], path[1]
    ax1, ax2 = cartesian_to_axial(*path0), cartesian_to_axial(*path1)
    directions = {
      (1, 0): "NE", (0, 1): "E", (-1, 1): "SE", (-1, 0): "SW", (0, -1): "W", (1, -1): "NW"
    }
    dq = ax2[0] - ax1[0]
    dr = ax2[1] - ax1[1]

    direction_vector = (dq, dr)

    return directions.get(direction_vector)

def plot_hexagon_of_hexagons(hex_radius=1, hex_grid_size=8, numbered_hexes={}, dpi=80):
    # Increase DPI and figure size for higher resolution
    fig, ax = plt.subplots(figsize=(8, 8), dpi=dpi)  # Set figure size and DPI
    ax.set_aspect('equal')

    # Specify which hexagons to make black (using axial coordinates q, r)
    black_hexes = []
    for q in range(7, -8, -1):
        start_r = q - 12
        end_r = -q + 8
        for r in range(start_r, end_r, 3):
            black_hexes.append((q, r))

    # Constants for hexagon size and positioning
    hex_height = 2 * hex_radius  # height of the hexagon
    hex_width = math.sqrt(3) * hex_radius  # width of the hexagon

    def hex_corner(center, size, i):
        """Calculate the corners of a flat-sided hexagon"""
        angle_deg = 60 * i + 30  # Rotate the hexagon by 30 degrees
        angle_rad = np.radians(angle_deg)
        return [center[0] + size * np.cos(angle_rad), center[1] + size * np.sin(angle_rad)]

    def draw_hexagon(center, color='white', number=None):
        """Draw a single hexagon at the given center with a color and optionally a number."""
        corners = [hex_corner(center, hex_radius, i) for i in range(6)]
        hexagon = plt.Polygon(corners, edgecolor='black', facecolor=color)
        ax.add_patch(hexagon)

        # If number is provided, add it to the hexagon
        if number is not None:
            ax.text(center[0], center[1] + hex_radius * 0.45, str(number), fontsize=11, ha='center', va='center')

    # Create a hexagonal grid (hex_grid_size per side)
    for q in range(-hex_grid_size + 1, hex_grid_size):
        for r in range(-hex_grid_size + 1, hex_grid_size):
            if -q - r >= -hex_grid_size + 1 and -q - r <= hex_grid_size - 1:
                # Convert axial coordinates to cartesian coordinates
                x = hex_width * (r + q / 2)
                y = hex_height * (3/4 * q)

                # Determine if this hexagon should be black or numbered
                if (q, r) in black_hexes:
                    color = 'dimgray'
                else:
                    color = 'white'

                number = numbered_hexes.get((q, r), None)

                # Draw the hexagon
                draw_hexagon((x, y), color=color, number=number)

    #ax.autoscale()
    margin = -0.4
    ax.set_xlim(-hex_grid_size * hex_width - margin, hex_grid_size * hex_width + margin)
    ax.set_ylim(-hex_grid_size * hex_height * 0.75 - margin, hex_grid_size * hex_height * 0.75 + margin)

    ax.set_axis_off()
    plt.tight_layout()
    plt.show()

    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, format='png')
    buf.seek(0)

    ## Remove extraneous whitespace from the image ##
    # Open the image from the BytesIO buffer
    image = Image.open(buf)

    # Convert image to a NumPy array
    image_array = np.array(image)

    # Mask for non-white pixels (RGB channels only)
    non_white_mask = np.any(image_array[:, :, :3] != [255, 255, 255], axis=-1)

    # Find the bounding box of non-white pixels
    non_empty_columns = np.where(non_white_mask.max(axis=0))[0]
    non_empty_rows = np.where(non_white_mask.max(axis=1))[0]

    # Crop the bounding box around the non-empty rows and columns
    crop_box = (min(non_empty_columns) - 1, min(non_empty_rows) - 1, max(non_empty_columns) + 1, max(non_empty_rows) + 1)
    cropped_image = image.crop(crop_box)

    # Save or display the cropped image (using another BytesIO buffer)
    cropped_image_buffer = io.BytesIO()
    cropped_image.save(cropped_image_buffer, format='PNG')

    cropped_image_buffer.seek(0)

    #cropped_image.save('test.png', format='PNG')

    image_base64 = base64.b64encode(cropped_image_buffer.read()).decode('utf-8')

    return image_base64

#END plot_hexagon_of_hexagons()

# Plot the hexagon of hexagons with flat-sided hexagons, set DPI for higher resolution
#image_base64 = plot_hexagon_of_hexagons(hex_radius=1, hex_grid_size=8, numbered_hexes=numbered_hexes, dpi=80)

def make_vpuz(qxw_out, selected_paths, harder=False):
    """
    Make a vpuz object from the output of Qxw and the paths
    """
    # Convert string to array
    qxw_arr = qxw_out.strip().split('\n')

    # Extract words
    words = []
    for line in qxw_arr:
        if line.startswith('# '):
            words.append(line[2:])

    # The solution string is half of each letter
    ctr = Counter(''.join(words).upper())
    solution_string = ''
    for letter in sorted(ctr.keys()):
        num = ctr[letter] // 2
        solution_string += letter * num

    # Initialize the return object
    vpuz = {
      "author": "AUTHOR_GOES_HERE"
    , "title": "TITLE_HERE"
    , "copyright": "COPYRIGHT_HERE"
    , "solution-string": solution_string
    }

    # Associate cells to numbers
    cell_to_number = dict()
    num = 1
    for p in selected_paths:
        if p[0] not in cell_to_number.keys():
            cell_to_number[p[0]] = str(num)
            num += 1

    # If we're not making the "harder" version, add bullets to the end of paths
    if not harder:
        for p in selected_paths:
            cell_to_number[p[-1]] = cell_to_number.get(p[-1], '') + '•'

    # Set up clues
    clues = []
    for i, path in enumerate(selected_paths):
        entry = words[i]
        direction = path_to_direction(path)
        number = cell_to_number[path[0]].replace('•', '')
        clues.append([f"{number}{direction}", f"clue_for_{entry}"])

    vpuz['clues'] = {'Clues': clues}

    # Create and add the image
    numbered_hexes = dict((cartesian_to_axial(*k), v) for k, v in cell_to_number.items())
    image_base64 = plot_hexagon_of_hexagons(hex_radius=1, hex_grid_size=8, numbered_hexes=numbered_hexes, dpi=90)

    vpuz['puzzle-image'] = f"data:image/png;base64,{image_base64}"

    return vpuz
