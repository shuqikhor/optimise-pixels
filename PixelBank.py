# This class is used to store pixels of the same color
# It will then split the pixels into chunks
class PixelBank:
	def __init__(self):
		self.pixels = set()
	
	def add_pixel(self, x, y):
		self.pixels.add((x, y))
	
	def group_pixels(self):
		groups = []

		# loop until all pixels are processed
		while len(self.pixels):
			# pop a random pixel then start flooding to all edges
			frontier = [self.pixels.pop()]
			group = set()

			# I'm using a queue here because BFS feels more like 'flooding'
			while len(frontier):
				head = frontier[0]
				frontier = frontier[1:]
				group.add(head)

				# add the pixel above and below to frontier
				for dy in [-1, 1]:
					neighbour = (head[0], head[1] + dy)
					if neighbour in self.pixels:
						frontier.append(neighbour)
						self.pixels.remove(neighbour)

				# trace left and right until boundary
				for dx in [-1, 1]:
					neighbour_x = (head[0] + dx, head[1])
					while neighbour_x in self.pixels:
						# add the pixel above and below to frontier
						for dy in [-1, 1]:
							neighbour_y = (neighbour_x[0], neighbour_x[1] + dy)
							if neighbour_y in self.pixels:
								frontier.append(neighbour_y)
								self.pixels.remove(neighbour_y)
						
						# move to group
						self.pixels.remove(neighbour_x)
						group.add(neighbour_x)

						# take another step to the neighbour_x
						neighbour_x = (neighbour_x[0] + dx, neighbour_x[1])

			groups.append(group)
		
		return groups