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

		colour = None
		if "fill" in attr:
			colour = attr["fill"].upper()
		elif "class" in attr:
			colour = css_classes[attr["class"]]
		elif "style" in attr:
			fill_search = re.search(r"fill\s*:\s*(#[A-Fa-f\d]{6})", attr["style"])
			if fill_search != None:
				colour = fill_search.group(1).upper()
		if colour == None:
			continue

		if not colour in pixel_groups:
			pixel_groups[colour] = set()
		pixel_groups[colour].add((x, y))

	# convert PixelBanks to chunks of pixels
	for colour in pixel_groups:
		pixel_groups[colour] = group_pixels(pixel_groups[colour])

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
				tag = get_svg_rect(**chunk[0], colour=colour)

			# otherwise, convert to <path />
			else:
				tag = get_svg_path(chunk, colour)

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


# from https://stackoverflow.com/questions/1165647/how-to-determine-if-a-list-of-polygon-points-are-in-clockwise-order
# since svg uses inverted Y-axis, negative is clockwise
def is_clockwise(polygon):
	result = 0
	for i in range(len(polygon)):
		start, end = (polygon[i], polygon[(i+1)%len(polygon)])
		result += (end[0] - start[0]) * (end[1] + start[1])
	return result < 0


# This function splits the pixels into chunks
def group_pixels(pixels):
	groups = []

	# loop until all pixels are processed
	while len(pixels):
		# pop a random pixel then start flooding to all edges
		frontier = [pixels.pop()]
		group = set()

		# I'm using a queue here because BFS feels more like 'flooding'
		while len(frontier):
			head = frontier[0]
			frontier = frontier[1:]
			group.add(head)

			# add the pixel above and below to frontier
			for dy in [-1, 1]:
				neighbour = (head[0], head[1] + dy)
				if neighbour in pixels:
					frontier.append(neighbour)
					pixels.remove(neighbour)

			# trace left and right until boundary
			for dx in [-1, 1]:
				neighbour_x = (head[0] + dx, head[1])
				while neighbour_x in pixels:
					# add the pixel above and below to frontier
					for dy in [-1, 1]:
						neighbour_y = (neighbour_x[0], neighbour_x[1] + dy)
						if neighbour_y in pixels:
							frontier.append(neighbour_y)
							pixels.remove(neighbour_y)
					
					# move to group
					pixels.remove(neighbour_x)
					group.add(neighbour_x)

					# take another step to the neighbour_x
					neighbour_x = (neighbour_x[0] + dx, neighbour_x[1])

		groups.append(group)
	
	return groups


class EdgeMap:
	# todo: instead of generating an edge map, convert to a bunch of lines directly
	def __init__(self, from_pixels):
		# find dimension (from 0,0)
		self.width = max([pixel[0] for pixel in from_pixels]) + 1
		self.height = max([pixel[1] for pixel in from_pixels]) + 1

		# since this is an edge map, it will be 1 col & row bigger than a pixel map
		self.grid = []
		for row in range(self.height + 1):
			edge_row = []
			for col in range(self.width + 1):
				# (edge-rightwards, edge-downwards) of a corner
				edge_row.append((False, False))
			self.grid.append(edge_row)
		
		"""
		current state (assume it's from 2x2 pixels, then it will be a 3x3 grid):
			self.grid = [
				[ (edge-rightwards, edge-downwards) * 3 ],
				[ (edge-rightwards, edge-downwards) * 3 ],
				[ (edge-rightwards, edge-downwards) * 3 ]
			]
		which means at the right-most column, the "edge-rightwards" is always False
		"""

		# it's a bit awkward when plotting but let's just do it
		# here we flip the state of all 4 edges of a pixel
		# overlapping edges (edges between 2 pixels) will cancel each other in the process
		for pixel in from_pixels:
			x, y = pixel

			# top left corner
			self.grid[y][x] = (not self.grid[y][x][0], not self.grid[y][x][1])

			# top right corner
			self.grid[y][x+1] = (self.grid[y][x+1][0], not self.grid[y][x+1][1])

			# bottom left corner
			self.grid[y+1][x] = (not self.grid[y+1][x][0], self.grid[y+1][x][1])
	
	# this is to illustrate the outcome, for debugging purpose
	def print(self):
		print("width x height:", self.width, self.height)

		for y in range(self.height+1):
			row = ""
			for x in range(self.width+1):
				row += "---" if self.grid[y][x][0] else "   "
			print(row)
			row = ""
			for x in range(self.width+1):
				row += "|  " if self.grid[y][x][1] else "   "
			print(row)

	# trace the lines to generate polygons from the chunk
	def generate_polygon(self):

		# convert all edges to lines ((x1,y1), (x2,y2))
		lines = set()
		for y in range(self.height + 1):
			for x in range(self.width + 1):
				if self.grid[y][x][0]:
					line = (
						(x, y),
						(x+1, y)
					)
					lines.add(line)
				if self.grid[y][x][1]:
					line = (
						(x, y),
						(x, y+1)
					)
					lines.add(line)
		
		# start depth first search
		polygons = list()
		explored_dots = set()
		frontier = []
		while len(lines):
			current_line = list(lines)[0]
			node = {
				"start": current_line[0],
				"end": current_line[1],
				"line": current_line,
				"parent": None
			}
			frontier = [node]
			explored_dots.add(node["start"])

			while len(frontier):
				node = frontier[0]
				frontier = frontier[1:]

				# skip if line no longer exist in lines set
				if node["line"] not in lines:
					continue
				lines.remove(node["line"])

				# when hit the start or the middle of the path, trace back and generate a path
				dot = node["end"]
				if dot in explored_dots:
					polygon = [node["start"]]

					node_header = node
					while node_header["parent"] != None and node_header["start"] != dot:
						node_header = node_header["parent"]
						polygon = [node_header["start"]] + polygon
					
					if is_clockwise(polygon):
						polygon.reverse()
					polygons.append(polygon)
					explored_dots.remove(dot)
					continue

				# add the next connecting-line to frontier
				for line in lines:
					if line[0] != dot and line[1] != dot:
						continue
					start = line[0] if line[0] == dot else line[1]
					end = line[1] if line[0] == dot else line[0]
					new_node = {
						"start": start,
						"end": end,
						"line": line,
						"parent": node
					}
					frontier = [new_node] + frontier

				explored_dots.add(dot)

		return polygons
	

def get_svg_path(polygons, colour):
	left_most = min([p["left"] for p in polygons])
	top_most = min([p["top"] for p in polygons])

	polygons.sort(key=lambda x:x["left"])

	paths = []
	for polygon in polygons:
		points = polygon["points"]

		# reverse points (make it counter-clockwise) if it's a cutout
		if polygon["left"] != left_most or polygon["top"] != top_most:
			points.reverse()

		path = ""
		last_point = points[-1]
		for i in range(len(points)):
			point = points[i]
			next_point = points[(i+1)%len(points)]

			if point[0] == next_point[0] and point[0] == (last_point[0] if last_point != None else False):
				continue

			if point[1] == next_point[1] and point[1] == (last_point[1] if last_point != None else False):
				continue

			if path == "":
				path += f"M{point[0]},{point[1]}"
			else:
				dx = point[0] - last_point[0]
				dy = point[1] - last_point[1]

				if dx == 0:
					# path += f"v{dy}"
					path += f"V{point[1]}"
				elif dy == 0:
					# path += f"h{dx}"
					path += f"H{point[0]}"
				else:
					# path += f"l{dx},{dy}"
					path += f"L{point[0]},{point[1]}"

			last_point = point
		path += "z"
		paths.append(path)
	svg_path = " ".join(paths)
	return f'<path fill="{colour}" d="{svg_path}"/>'

def get_svg_rect(colour, left, top, width, height, points = []):
	return f'<rect fill="{colour}" x="{left}" y="{top}" width="{width}" height="{height}"/>'


if __name__ == "__main__":
    main()


exit(0)