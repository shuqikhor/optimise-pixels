# from https://stackoverflow.com/questions/1165647/how-to-determine-if-a-list-of-polygon-points-are-in-clockwise-order
# since svg uses inverted Y-axis, negative is clockwise
def is_clockwise(polygon):
	result = 0
	for i in range(len(polygon)):
		start, end = (polygon[i], polygon[(i+1)%len(polygon)])
		result += (end[0] - start[0]) * (end[1] + start[1])
	return result < 0


class EdgeMap:
	def __init__(self, from_pixels):
		self.lines = list()
		for pixel in from_pixels:
			x, y = pixel

			points = [
				(x  , y  ),
				(x+1, y  ),
				(x+1, y+1),
				(x  , y+1)
			]

			# the points in these lines are arranged in top-down left-to-right manner
			lines = [
				[points[0], points[1]],
				[points[1], points[2]],
				[points[3], points[2]],
				[points[0], points[3]]
			]

			for line in lines:
				# if not found, add
				# if found, delete
				# this will cancel out overlapped lines
				if line in self.lines:
					self.lines.remove(line)
				else:
					self.lines.append(line)
	
	# this is to illustrate the outcome, for debugging purpose
	def print(self):
		points = [l[0] for l in self.lines] + [l[1] for l in self.lines]
		x = [p[0] for p in points]
		y = [p[1] for p in points]
		width = max(x) + 1
		height = max(y) + 1
		print(f"width x height: {width} x {height}")

		for y in range(height):
			row = ""
			for x in range(width):
				row += "---" if [(x, y), (x+1, y)] in self.lines else "   "
			print(row)
			row = ""
			for x in range(width):
				row += "|  " if [(x, y), (x, y+1)] in self.lines else "   "
			print(row)

	# trace the lines to generate polygons from the chunk
	def generate_polygon(self):
		lines = self.lines
		
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
