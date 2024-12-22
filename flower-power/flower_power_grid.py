"""
Make a "flower power" SVG
Original code from Robin Yu can be found here:
https://github.com/robincyu/flower/blob/master/flower.py
"""

import math

petals = 12
petal_thickness = 80
gravity = 140
word_length = 5
font_size = 14
number_margin = 5
CANVAS_SIZE = 500
MARGIN_SIZE = 10
PRECISION = 10000

# Squared distance between two points
def squared_dist(x0, y0, x1, y1):
    return (x0-x1)*(x0-x1) + (y0-y1)*(y0-y1)

# Rotate point about origin
def rotate(x, y, theta):
    s = math.sin(theta)
    c = math.cos(theta)
    x_new = x*c - y*s
    y_new = x*s + y*c
    return x_new, y_new

# Split bezier curve into two parts, and return the first part
def split_bezier_curve_first(x0, y0, x1, y1, x2, y2, z):
    return x0, y0, (1-z)*x0 + z*x1, (1-z)*y0 + z*y1, (1-z)*(1-z)*x0 + 2*(1-z)*z*x1 + z*z*x2, (1-z)*(1-z)*y0 + 2*(1-z)*z*y1 + z*z*y2

# Find the z at the intersection of two intersecting petals. Too lazy to do the math, just walk the curves
def calculate_z(a_x0, a_y0, a_x1, a_y1, a_x2, a_y2, b_x0, b_y0, b_x1, b_y1, b_x2, b_y2, precision=PRECISION):
    best_z = -1
    best_dist = 2000000
    for z in range(precision+1):
        if z < precision/100 or z > precision - precision/100: # skip edges
            continue
        _, _, _, _, a_x, a_y = split_bezier_curve_first(a_x0, a_y0, a_x1, a_y1, a_x2, a_y2, z/precision)
        _, _, _, _, b_x, b_y = split_bezier_curve_first(b_x0, b_y0, b_x1, b_y1, b_x2, b_y2, z/precision)
        if squared_dist(a_x, a_y, b_x, b_y) < best_dist:
            best_dist = squared_dist(a_x, a_y, b_x, b_y)
            best_z = z
    return best_z/precision

def start(x, y):
    return "<path d=\"M " + str(x) + " " + str(y)

def bezier_through_to(s, vx, vy, x, y):
    return s + " Q " + str(vx) + " " + str(vy) + " " + str(x) + " " + str(y)

def reset(s):
    return s + " Z"

def end(s, color = "black", fill = "transparent", stroke_width = "1"):
    return s + "\" stroke=\"" + color + "\" fill=\"" + fill + "\" stroke-width=\"" + stroke_width + "\"/>"

def create_flower_power_svg(petals, word_length, petal_thickness, gravity, \
                            font_size, number_margin, canvas_size=CANVAS_SIZE, \
                            margin_size=MARGIN_SIZE):
    ret = ''
    ret += "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<svg width=\"" + str(canvas_size+margin_size) + "\" height=\"" + str(canvas_size+margin_size) + "\" viewBox=\"" + str(-(canvas_size+margin_size)/2) + " " + str(-(canvas_size+margin_size)/2) + " " + str(canvas_size+margin_size) + " " + str(canvas_size+margin_size) + "\" xmlns=\"http://www.w3.org/2000/svg\">\n"
    ret += "<style>text {font: " + str(font_size) + "px sans-serif; text-anchor: middle; dominant-baseline: middle;}</style>"
    
    # Prepare petals and other constants
    end_x, end_y = 0, -canvas_size/2
    left_x, left_y = -petal_thickness*canvas_size/200, -canvas_size/4 + gravity
    right_x, right_y = petal_thickness*canvas_size/200, -canvas_size/4 + gravity
    
    border_end_x, border_end_y = 0, -canvas_size/2 - 2
    border_left_x, border_left_y = -petal_thickness*canvas_size/200, -canvas_size/4 + gravity - 2
    border_right_x, border_right_y = petal_thickness*canvas_size/200, -canvas_size/4 + gravity - 2
    
    outer_points = []
    border_outer_points = []
    for i in range(petals+word_length+1):
        outer_points.extend([left_x, left_y, end_x, end_y, right_x, right_y])
        border_outer_points.extend([border_left_x, border_left_y, border_end_x, border_end_y, border_right_x, border_right_y])
        left_x, left_y = rotate(left_x, left_y, 2*math.pi/petals)
        end_x, end_y = rotate(end_x, end_y, 2*math.pi/petals)
        right_x, right_y = rotate(right_x, right_y, 2*math.pi/petals)
        border_left_x, border_left_y = rotate(border_left_x, border_left_y, 2*math.pi/petals)
        border_end_x, border_end_y = rotate(border_end_x, border_end_y, 2*math.pi/petals)
        border_right_x, border_right_y = rotate(border_right_x, border_right_y, 2*math.pi/petals)
    z = calculate_z(0, 0, outer_points[4], outer_points[5], outer_points[2], outer_points[3], 0, 0, outer_points[6*word_length], outer_points[6*word_length+1], outer_points[6*word_length+2], outer_points[6*word_length+3])
    z_inner = calculate_z(0, 0, outer_points[4], outer_points[5], outer_points[2], outer_points[3], 0, 0, outer_points[6*(word_length+1)], outer_points[6*(word_length+1)+1], outer_points[6*(word_length+1)+2], outer_points[6*(word_length+1)+3])
    
    print(i)
    
    _, _, _, _, circle_limit_x, circle_limit_y = split_bezier_curve_first(0, 0, outer_points[6*i+4], outer_points[6*i+5], outer_points[6*i+2], outer_points[6*i+3], z_inner)
    radius = math.sqrt(squared_dist(0, 0, circle_limit_x, circle_limit_y))
    h = calculate_z(outer_points[2], outer_points[3], outer_points[4], outer_points[5], 0, 0, outer_points[6+2], outer_points[6+3], outer_points[6], outer_points[6+1], 0, 0)
    
    # Draw petals
    path = start(0, 0)
    for i in range(petals):
        path = bezier_through_to(path, outer_points[6*i+0], outer_points[6*i+1], outer_points[6*i+2], outer_points[6*i+3])
        path = bezier_through_to(path, outer_points[6*i+4], outer_points[6*i+5], 0, 0)
    path = end(path, "black", "transparent", "2")
    ret += path + "\n"
    
    # Shade inside for word length
    path = start(0, 0)
    for i in range(petals):
        _, _, a_x, a_y, b_x, b_y = split_bezier_curve_first(0, 0, outer_points[6*i+4], outer_points[6*i+5], outer_points[6*i+2], outer_points[6*i+3], z)
        d_x, d_y, c_x, c_y, _, _ = split_bezier_curve_first(0, 0, outer_points[6*(i+word_length)], outer_points[6*(i+word_length)+1], outer_points[6*(i+word_length)+2], outer_points[6*(i+word_length)+3], z)
        path = bezier_through_to(path, a_x, a_y, b_x, b_y)
        path = bezier_through_to(path, c_x, c_y, d_x, d_y)
    path = end(path, "transparent", "black")
    ret += path + "\n"
    
    # Make outside of petal thicker
    path = start(border_outer_points[2], border_outer_points[3])
    for i in range(petals+1): # +1 here to close the top of the flower properly
        _, _, a_x, a_y, b_x, b_y = split_bezier_curve_first(border_outer_points[6*i+2], border_outer_points[6*i+3], border_outer_points[6*i+4], border_outer_points[6*i+5], 0, 0, h)
        d_x, d_y, c_x, c_y, _, _ = split_bezier_curve_first(border_outer_points[6*(i+1)+2], border_outer_points[6*(i+1)+3], border_outer_points[6*(i+1)], border_outer_points[6*(i+1)+1], 0, 0, h)
        path = bezier_through_to(path, a_x, a_y, b_x, b_y)
        path = bezier_through_to(path, c_x, c_y, d_x, d_y)
    path = end(path, "black", "transparent", "5")
    ret += path + "\n"
    
    # White circle
    ret += "<circle cx=\"0\" cy=\"0\" r=\"" + str(radius) + "\" stroke=\"transparent\" fill=\"white\"/>\n"
    
    # Numbering
    x, y = outer_points[2], outer_points[3]+font_size+number_margin
    for i in range(petals):
        ret += "<text x=\"" + str(x) + "\" y=\"" + str(y) + "\">" + str(i+1) + "</text>\n"
        x, y = rotate(x, y, 2*math.pi/petals)
    
    ret += "</svg>"
    
    return ret
#END make flower power
