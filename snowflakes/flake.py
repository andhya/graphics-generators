import drawSvg as draw
import math
from random import random

scale = 2
stroke = 1
start = 0
middle = 10
end = 2
size = 3
angle = math.radians(60)

def hex_points(columns, width):

    tip = 0.5*width / math.tan(angle)
    points = [(start,0)]

    prev = points[0][1]
    x = points[0][0]

    for height in columns:
        if not height == prev:
            points.append((x+0.5*height,height))
            y_tip = height + tip
            x_tip = x + 0.5*y_tip + (0.5*width)
            points.append((x_tip , y_tip))
        points.append((x++0.5*height+width,height))
        prev = height
        x = x+width

    points.append((x,0))

    return points

def rotate(points, radians, origin=(0,0)):
    new_points = []
    for xy in points:
	    x, y = xy
	    offset_x, offset_y = origin
	    adjusted_x = (x - offset_x)
	    adjusted_y = (y - offset_y)
	    cos_rad = math.cos(radians)
	    sin_rad = math.sin(radians)
	    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
	    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y
	    new_points.append((qx,qy))
    return new_points

def translate(points, trans):
    new_points = []
    dx, dy = trans
    for xy in points:
            x, y = xy
            x = x + dx
            y = y + dy
            new_points.append((x,y))
    return new_points

def reflect_y(points):
    new_points = []
    for xy in points:
           x, y = xy
           new_points.append((x,-y))
    return new_points

def core():
    core_y = 0.5 * stroke / math.tan(angle)
    core_x = 0.5 * stroke
    return (core_x, core_y)

def populate_columns():
    columns = []
    columns.append(0)

    for x in range(middle):
        columns.append(random()*size)

    return columns

def random_flake(x,y):
	p = draw.Path(stroke_width=0, stroke='black',
	              fill='black', fill_opacity=1)

	og = core()
	p.M(og[0]+x,og[1]+y)


	columns = populate_columns()
	points = hex_points(columns,stroke)

	points = translate(points,core())
	mirror = points.copy()
	mirror.reverse()
	mirror.append((og[0],og[1]))
	mirror = reflect_y(mirror)
	points.append((start+middle+end,0))
	points.extend(mirror)

	for i in range(6):
	    points.extend(rotate(points,angle))

	for point in points:
	    p.L(point[0]+x,point[1]+y)

	return p

if __name__ == "__main__":
	d = draw.Drawing(127, 178, origin='center', displayInline=False)
	p = random_flake(0,0)
	d.append(p)
	d.setPixelScale(3)  # Set number of pixels per geometry unit
	d.saveSvg('/mnt/c/Users/frank/Downloads/flake.svg')
