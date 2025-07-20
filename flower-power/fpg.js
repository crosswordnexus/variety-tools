/*
Make a "flower power" SVG
Original code from Robin Yu can be found here:
https://github.com/robincyu/flower/blob/master/flower.py
*/
var CANVAS_SIZE, MARGIN_SIZE, PRECISION;
CANVAS_SIZE = 750;
MARGIN_SIZE = 10;
PRECISION = 10000;

function squared_dist(x0, y0, x1, y1) {
  return (x0 - x1) * (x0 - x1) + (y0 - y1) * (y0 - y1);
}

function rotate(x, y, theta) {
  var c, s, x_new, y_new;
  s = Math.sin(theta);
  c = Math.cos(theta);
  x_new = x * c - y * s;
  y_new = x * s + y * c;
  return [x_new, y_new];
}

function split_bezier_curve_first(x0, y0, x1, y1, x2, y2, z) {
  return [x0, y0, (1 - z) * x0 + z * x1, (1 - z) * y0 + z * y1, (1 - z) * (1 - z) * x0 + 2 * (1 - z) * z * x1 + z * z * x2, (1 - z) * (1 - z) * y0 + 2 * (1 - z) * z * y1 + z * z * y2];
}

function calculate_z(a_x0, a_y0, a_x1, a_y1, a_x2, a_y2, b_x0, b_y0, b_x1, b_y1, b_x2, b_y2, precision = PRECISION) {
  var _, a_x, a_y, b_x, b_y, best_dist, best_z;

  best_z = -1;
  best_dist = 2000000;

  for (var z = 0, _pj_a = precision + 1; z < _pj_a; z += 1) {
    if (z < precision / 100 || z > precision - precision / 100) {
      continue;
    }

    [_, _, _, _, a_x, a_y] = split_bezier_curve_first(a_x0, a_y0, a_x1, a_y1, a_x2, a_y2, z / precision);
    [_, _, _, _, b_x, b_y] = split_bezier_curve_first(b_x0, b_y0, b_x1, b_y1, b_x2, b_y2, z / precision);

    if (squared_dist(a_x, a_y, b_x, b_y) < best_dist) {
      best_dist = squared_dist(a_x, a_y, b_x, b_y);
      best_z = z;
    }
  }

  return best_z / precision;
}

function start(x, y) {
  return "<path d=\"M " + x.toString() + " " + y.toString();
}

function bezier_through_to(s, vx, vy, x, y) {
  return s + " Q " + vx.toString() + " " + vy.toString() + " " + x.toString() + " " + y.toString();
}

function reset(s) {
  return s + " Z";
}

function end(s, color = "black", fill = "transparent", stroke_width = "1") {
  return s + "\" stroke=\"" + color + "\" fill=\"" + fill + "\" stroke-width=\"" + stroke_width + "\"/>";
}

function create_flower_power_svg(petals, word_length, petal_thickness, gravity,
                                font_size, number_margin, canvas_size = CANVAS_SIZE,
                                margin_size = MARGIN_SIZE, inner_numbers = true) {
  var _, a_x, a_y, b_x, b_y, border_end_x, border_end_y, border_left_x, border_left_y, border_outer_points, border_right_x, border_right_y, c_x, c_y, circle_limit_x, circle_limit_y, d_x, d_y, end_x, end_y, h, left_x, left_y, outer_points, path, radius, ret, right_x, right_y, x, y, z, z_inner;

  ret = "";
  ret += "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<svg id=\"svgElement\" width=\"" + (canvas_size + margin_size).toString() + "\" height=\"" + (canvas_size + margin_size).toString() + "\" viewBox=\"" + (-(canvas_size + margin_size) / 2).toString() + " " + (-(canvas_size + margin_size) / 2).toString() + " " + (canvas_size + margin_size).toString() + " " + (canvas_size + margin_size).toString() + "\" xmlns=\"http://www.w3.org/2000/svg\">\n";
  ret += "<style>text {font: " + font_size.toString() + "px sans-serif; text-anchor: middle; dominant-baseline: middle;}</style>";
  [end_x, end_y] = [0, -canvas_size / 2];
  [left_x, left_y] = [-petal_thickness * canvas_size / 200, -canvas_size / 4 + gravity];
  [right_x, right_y] = [petal_thickness * canvas_size / 200, -canvas_size / 4 + gravity];
  [border_end_x, border_end_y] = [0, -canvas_size / 2 - 2];
  [border_left_x, border_left_y] = [-petal_thickness * canvas_size / 200, -canvas_size / 4 + gravity - 2];
  [border_right_x, border_right_y] = [petal_thickness * canvas_size / 200, -canvas_size / 4 + gravity - 2];
  outer_points = [];
  border_outer_points = [];

  for (var i = 0, _pj_a = petals + word_length + 1; i < _pj_a; i += 1) {
    outer_points.push(...[left_x, left_y, end_x, end_y, right_x, right_y]);
    border_outer_points.push(...[border_left_x, border_left_y, border_end_x, border_end_y, border_right_x, border_right_y]);
    [left_x, left_y] = rotate(left_x, left_y, 2 * Math.PI / petals);
    [end_x, end_y] = rotate(end_x, end_y, 2 * Math.PI / petals);
    [right_x, right_y] = rotate(right_x, right_y, 2 * Math.PI / petals);
    [border_left_x, border_left_y] = rotate(border_left_x, border_left_y, 2 * Math.PI / petals);
    [border_end_x, border_end_y] = rotate(border_end_x, border_end_y, 2 * Math.PI / petals);
    [border_right_x, border_right_y] = rotate(border_right_x, border_right_y, 2 * Math.PI / petals);
  }

  z = calculate_z(0, 0, outer_points[4], outer_points[5], outer_points[2], outer_points[3], 0, 0, outer_points[6 * word_length], outer_points[6 * word_length + 1], outer_points[6 * word_length + 2], outer_points[6 * word_length + 3]);
  z_inner = calculate_z(0, 0, outer_points[4], outer_points[5], outer_points[2], outer_points[3], 0, 0, outer_points[6 * (word_length + 1)], outer_points[6 * (word_length + 1) + 1], outer_points[6 * (word_length + 1) + 2], outer_points[6 * (word_length + 1) + 3]);

  // calculate the limits of the circle
  var i1 = petals + word_length;
  [_, _, _, _, circle_limit_x, circle_limit_y] = split_bezier_curve_first(0, 0, outer_points[6 * i1 + 4], outer_points[6 * i1 + 5], outer_points[6 * i1 + 2], outer_points[6 * i1 + 3], z_inner);

  // calculate the radius of the circle
  radius = Math.sqrt(squared_dist(0, 0, circle_limit_x, circle_limit_y));

  h = calculate_z(outer_points[2], outer_points[3], outer_points[4], outer_points[5], 0, 0, outer_points[6 + 2], outer_points[6 + 3], outer_points[6], outer_points[6 + 1], 0, 0);
  path = start(0, 0);

  for (var i = 0, _pj_a = petals; i < _pj_a; i += 1) {
    path = bezier_through_to(path, outer_points[6 * i + 0], outer_points[6 * i + 1], outer_points[6 * i + 2], outer_points[6 * i + 3]);
    path = bezier_through_to(path, outer_points[6 * i + 4], outer_points[6 * i + 5], 0, 0);
  }

  path = end(path, "black", "transparent", "2");
  ret += path + "\n";
  path = start(0, 0);

  for (var i = 0, _pj_a = petals; i < _pj_a; i += 1) {
    [_, _, a_x, a_y, b_x, b_y] = split_bezier_curve_first(0, 0, outer_points[6 * i + 4], outer_points[6 * i + 5], outer_points[6 * i + 2], outer_points[6 * i + 3], z);
    [$x, $y, c_x, c_y, _, _] = split_bezier_curve_first(0, 0, outer_points[6 * (i + word_length)], outer_points[6 * (i + word_length) + 1], outer_points[6 * (i + word_length) + 2], outer_points[6 * (i + word_length) + 3], z);
    path = bezier_through_to(path, a_x, a_y, b_x, b_y);
    path = bezier_through_to(path, c_x, c_y, $x, $y);
  }

  path = end(path, "transparent", "black");
  ret += path + "\n";
  path = start(border_outer_points[2], border_outer_points[3]);

  for (var i = 0, _pj_a = petals + 1; i < _pj_a; i += 1) {
    [_, _, a_x, a_y, b_x, b_y] = split_bezier_curve_first(border_outer_points[6 * i + 2], border_outer_points[6 * i + 3], border_outer_points[6 * i + 4], border_outer_points[6 * i + 5], 0, 0, h);
    [$x, $y, c_x, c_y, _, _] = split_bezier_curve_first(border_outer_points[6 * (i + 1) + 2], border_outer_points[6 * (i + 1) + 3], border_outer_points[6 * (i + 1)], border_outer_points[6 * (i + 1) + 1], 0, 0, h);
    path = bezier_through_to(path, a_x, a_y, b_x, b_y);
    path = bezier_through_to(path, c_x, c_y, $x, $y);
  }

  path = end(path, "black", "transparent", "5");
  ret += path + "\n";

  ret += "<circle cx=\"0\" cy=\"0\" r=\"" + radius.toString() + "\" stroke=\"transparent\" fill=\"white\"/>\n";
  [x, y] = [outer_points[2], outer_points[3] + font_size + number_margin];

  // Numbering
  for (var i = 0, _pj_a = petals; i < _pj_a; i += 1) {
    ret += "<text x=\"" + x.toString() + "\" y=\"" + y.toString() + "\">" + (i + 1).toString() + "</text>\n";
    [x, y] = rotate(x, y, 2 * Math.PI / petals);
  }

  // Inner numbers
  // Note: this doesn't quite work yet
  if (inner_numbers) {
    let inner_radius = radius + 2 * (font_size + number_margin);
    let x_in = 0, y_in = -inner_radius;
    for (var i = 0; i < petals; i++) {
      let [x_i, y_i] = rotate(x_in, y_in, 2 * Math.PI * i /petals);
      ret += `<text x='${x_i}' y='${y_i}'>${petals + i + 1}</text>\n`;
    }
  }

  ret += "</svg>";
  return ret;
}
