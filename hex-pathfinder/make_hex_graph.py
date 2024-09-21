# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 2024

@author: Alex Boisvert
"""

import networkx as nx

# Parameters
ROW_LENGTHS = list(range(8, 16)) + list(range(14, 7, -1))  # Number of hexagons per row


# Function to determine if a hexagon is black
def is_black_hex(row, col):
    black_pattern_offset = [2, 1, 0]  # Pattern offset for black hexagons per row
    if row <= 7:
        return (col - black_pattern_offset[row % 3]) % 3 == 0
    else:
        return (col - black_pattern_offset[::-1][row % 3]) % 3 == 0

# Function to find the coordinates of the upper-right neighbor
def get_ur_neighbor(row, col):
    if row == 0:
        return None
    r1 = row - 1
    if row <= 7:
        c1 = col
    else:
        c1 = col + 1
    if is_black_hex(r1, c1):
        return None
    elif c1 >= ROW_LENGTHS[r1]:
        return None
    else:
        return (r1, c1)

# Function to find the coordinates of the upper-left neighbor
def get_ul_neighbor(row, col):
    if row == 0:
        return None
    r1 = row - 1
    if row <= 7:
        c1 = col - 1
        if c1 < 0:
            return None
    else:
        c1 = col
    if is_black_hex(r1, c1):
        return None
    else:
        return (r1, c1)

# Node location to node ID
def loc_to_id(row, col):
    pass

def create_hex_graph():
    # Initialize the graph
    G = nx.Graph()

    # initialize hex positions
    hex_positions = {}

    # Create the grid of hexagons
    for row in range(len(ROW_LENGTHS)):
        row_len = ROW_LENGTHS[row]
        for col in range(row_len):
            node_id = (row, col)
            if not is_black_hex(row, col):  # Only add white hexagons as nodes
                hex_positions[node_id] = (col, row)  # Storing position for drawing
                G.add_node(node_id)

                # Add edges to neighboring hexagons (if they exist)
                if col > 0 and not is_black_hex(row, col - 1):  # Left neighbor
                    G.add_edge(node_id, (row, col-1))
                if row > 0:  # Upper neighbors
                    # upper-right neighbor
                    upper_right_node = get_ur_neighbor(row, col)
                    if upper_right_node:
                        G.add_edge(node_id, upper_right_node)
                    # upper-left neighbor
                    upper_left_node = get_ul_neighbor(row, col)
                    if upper_left_node:
                        G.add_edge(node_id, upper_left_node)
    return G
