# from https://stackoverflow.com/questions/1165647/how-to-determine-if-a-list-of-polygon-points-are-in-clockwise-order
# since svg uses inverted Y-axis, negative is clockwise
def is_clockwise(polygon):
	result = 0
	for i in range(len(polygon)):
		start, end = (polygon[i], polygon[(i+1)%len(polygon)])
		result += (end[0] - start[0]) * (end[1] + start[1])
	return result < 0


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
