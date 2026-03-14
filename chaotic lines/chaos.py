import svgwrite
import random
import math

# Constants for A3 size in mm
A3_WIDTH_MM = 8400
A3_HEIGHT_MM = 8400

# Convert mm to pixels (assuming 96 DPI)
MM_TO_PX = 96 / 25.4
A3_WIDTH_PX = A3_WIDTH_MM * MM_TO_PX
A3_HEIGHT_PX = A3_HEIGHT_MM * MM_TO_PX

# Function to generate random lines
def generate_random_lines(dwg, num_lines, line_length, interstitial_size):
    for _ in range(num_lines):
        # Random start and end points
        x1 = random.uniform(0, A3_WIDTH_PX)
        y1 = random.uniform(0, A3_HEIGHT_PX)
        angle = random.uniform(0, 360)
        x2 = x1 + line_length * math.cos(math.radians(angle))
        y2 = y1 + line_length * math.sin(math.radians(angle))
        
        # Ensure lines go across the field of view
        if x2 < 0:
            x2 = 0
        elif x2 > A3_WIDTH_PX:
            x2 = A3_WIDTH_PX
        if y2 < 0:
            y2 = 0
        elif y2 > A3_HEIGHT_PX:
            y2 = A3_HEIGHT_PX
        
        # Draw the line
        dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke=svgwrite.rgb(10, 10, 16, '%')))

# Create an SVG drawing
dwg = svgwrite.Drawing('chaotic_lines.svg', profile='tiny', size=(A3_WIDTH_PX, A3_HEIGHT_PX))

# Parameters
num_lines = 400  # Number of lines
line_length = max(A3_WIDTH_PX, A3_HEIGHT_PX)  # Ensure lines go across the field of view
interstitial_size = 25 * MM_TO_PX  # Approximate size of interstitial shapes in pixels

# Generate random lines
generate_random_lines(dwg, num_lines, line_length, interstitial_size)

# Save the SVG file
dwg.save()
