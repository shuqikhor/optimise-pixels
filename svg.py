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