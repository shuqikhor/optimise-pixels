# workflow:
# - extract all pixel blocks (1x1 rect) from SVG
# - group them by colour (this is for performance optimisation)
# - detect boundaries and separate into chunks
# - plot chunk edges
# - plot paths from the edges (some chunks may have >1 paths if there's a hole in them)
# - find out whether is the chunk a rectangle
#    - if rect, convert it to <rect />
#    - if not, convert it to <path />
#       - determine path direction (clockwise for outer shape, ccw for cutouts)
#       - write SVG path
# - sort svg tags by "x" and "y" coordinates
# - enclose with SVG opening/closing tags

import sys
import os.path
import xml.etree.ElementTree as ET 
import re
from PixelBank import PixelBank
from EdgeMap import EdgeMap
import SVGhelper as SVG

def main():
	filename = get_filename()
	tree = ET.parse(filename)
	root = tree.getroot()
	pixel_groups = {}
	
	# extract all pixels
	# group them by colour as PixelBank object
	ns_array = {
		'svg': 'http://www.w3.org/2000/svg', 
		'xlink': 'http://www.w3.org/1999/xlink'
	}

	css_classes = {}
	for item in root.findall(".//svg:style", ns_array):
		style_text = item.text.split("\n")
		current_class = None
		current_colour = None
		for line in style_text:
			css_search = re.search(r"\.(\w+)", line)
			if css_search != None:
				current_class = css_search.group(1)
			
			fill_search = re.search(r"fill:\s*(#[A-Fa-f\d]{6})", line)
			if fill_search != None:
				current_colour = fill_search.group(1).upper()

			if current_class != None and current_colour != None:
				css_classes[current_class] = current_colour
				current_colour = None
				current_class = None

	for item in root.findall(".//svg:rect", ns_array):
		attr = item.attrib
		x = int(attr["x"] if "x" in attr else 0)
		y = int(attr["y"] if "y" in attr else 0)

		if "fill" in attr:
			colour = attr["fill"].upper()
		elif "class" in attr:
			colour = css_classes[attr["class"]]

		if not colour in pixel_groups:
			pixel_groups[colour] = PixelBank()
		pixel_groups[colour].add_pixel(x, y)

	# convert PixelBanks to chunks of pixels
	for colour in pixel_groups:
		chunks = pixel_groups[colour].group_pixels()
		pixel_groups[colour] = chunks

	# setup edge map
	edge_maps = {}
	for colour in pixel_groups:
		edge_maps[colour] = list()

		for chunk in pixel_groups[colour]:
			# here we will get a list of paths
			edge_map = EdgeMap(chunk)
			polygons = edge_map.generate_polygon()

			# precalculate left, top, width, height of the path
			polygons = list(map(lambda polygon: precalculate(polygon), polygons))
			edge_maps[colour].append(polygons)

		# sort the chunks by y then x (to appear nicely in svg)
		edge_maps[colour].sort(key=lambda chunk:min([polygon["left"] for polygon in chunk]))
		edge_maps[colour].sort(key=lambda chunk:min([polygon["top"] for polygon in chunk]))

	"""
	current state:
		edge_maps = {
			"#XXXXXX": [                                                                                   # a colour group
				[                                                                                          # a chunk with a hole
					{ left:int, top:int, width:int, height:int, points:array<tuple (x,y)>},                # a polygon
					{ left:int, top:int, width:int, height:int, points:array<tuple (x,y)>}                 # a hole polygon
				],
				[                                                                                          # another chunk
					{ left:int, top:int, width:int, height:int, points:array<tuple (x,y)>}                 # a polygon
				]
			]
		}
	"""

	tags = list()
	for colour in edge_maps:
		for chunk in edge_maps[colour]:
			# if chunk is a rectangle, convert to <rect />
			if len(chunk) == 1 and is_rect(chunk[0]["points"]):
				tag = SVG.get_svg_rect(**chunk[0], colour=colour)

			# otherwise, convert to <path />
			else:
				tag = SVG.get_svg_path(chunk, colour)

			tags.append(tag)

	svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 9">\n'
	for tag in tags:
		svg_content += f"\t{tag}\n"
	svg_content += "</svg>"
	print(svg_content)

	# overwrite file
	svg_rewrite = open(filename, "w")
	svg_rewrite.write(svg_content)


def get_filename():
	filename = sys.argv[1] if len(sys.argv) == 2 else input("File name? ")
	if not filename.endswith(".svg"):
		filename = filename + ".svg"
	
	if not os.path.isfile(filename):
		print("File not found")
		exit(1)

	return filename


def precalculate(polygon):
	x = [p[0] for p in polygon]
	y = [p[1] for p in polygon]
	return {
		"left": min(x),
		"top": min(y),
		"width": max(x) - min(x),
		"height": max(y) - min(y),
		"points": polygon
	}


# first, remove unnecessary points (middle points in a straight line)
# then check whether are there only 4 points left
def is_rect(polygon):
	optimised = []
	last_point = polygon[-1]
	for i in range(len(polygon)):
		this_point = polygon[i]
		next_point = polygon[(i+1) % len(polygon)]
		if last_point[0] == this_point[0] and this_point[0] == next_point[0]:
			continue
		if last_point[1] == this_point[1] and this_point[1] == next_point[1]:
			continue
		optimised.append(polygon[i])
		last_point = this_point
	
	return len(optimised) == 4


if __name__ == "__main__":
    main()


exit(0)