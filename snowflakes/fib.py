import drawSvg as draw
import math
import flake

scale = 2
spacing = 20

d = draw.Drawing(1270, 1780, origin='center', displayInline=False)

def dot():
	return draw.Circle(x*scale, y*scale, 1, fill='red', stroke_width=0, stroke='black')

for i in range (1000):
   theta = math.pi * (3- math.sqrt(5))*(i)
   r = math.sqrt(i+1) * spacing
   x = r * math.cos(theta)
   y = r * math.sin(theta)
   d.append(flake.random_flake(x,y))

# Draw an irregular polygon
#d.append(draw.Lines(-80, -45,
#                    70, -49,
#                    95, 49,
#                    -90, 40,
#                    close=False,
#            fill='#eeee00',
#            stroke='black'))


# Draw a circle
#d.append(draw.Circle(0, 0, 3,
#            fill='red', stroke_width=0, stroke='black'))

# Draw an arbitrary path (a triangle in this case)
#p = draw.Path(stroke_width=2, stroke='lime',
#              fill='black', fill_opacity=0.2)
#p.M(-10, 20)  # Start path at point (-10, 20)
#p.C(30, -10, 30, 50, 70, 20)  # Draw a curve to (70, 20)
#d.append(p)


d.setPixelScale(1)  # Set number of pixels per geometry unit
d.saveSvg('/mnt/c/Users/frank/Downloads/fib.svg')
