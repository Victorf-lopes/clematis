import numpy as np

class ModelGenerator:
	# model reponsible for generating factory floor acyclic directed graphs
	# parameters:
	# n -> number of nodes/work stations
	# s -> level of seriality of the factory flow
	# 		s = 1 - (Henry Ford style) the flow of products is totally serial, and the work-stations
	# 		are placed one after another, in a single chain
	#		s = 0 - the flow of products is 0% serial, and all the workstations are placed in
	#		parallel, doing the same job
	#		when s in between 0 and 1, the flow of products is in between the extreme situations
	#
	# p_steps = np.floor(n*s) -> number of steps in the prodution process
	#		p_steps = n if s = 1
	#		p_steps = 1 if s = 0
	# every step in the production have at least one node/work station
	#
	# every node placed in production-step i is supplied from all the nodes in production-step i-1
	# and supplies for all the nodes in production-step i+1
	#
	# the model have a "raw_material" node that supplies the nodes in production-step 0 with
	# infinite supply of raw material
	# and it has a "finished_material" node that is supplied from the last production-step, which
	# can receive an infinite amount of finished products 
	# that is to say: the model has no restrictions of raw material or demand of finished products
	#
	# node attributes: production_rate; failure_rate
	# edge attributes: buffer_size
	#
	# in the basic version, the node and edge attributes will be the same for all the network elements
	# production rate = (p_steps/n)

	def __init__(self, n, s, failure_rate=0.1, buffer_size=1):
		# network parameters
		self.n = n
		self.s = s
		self.failure_rate = failure_rate
		self.buffer_size = buffer_size
		self.production_rate = 0

	def generate_graph(self):
		# calculate the number of production steps in the network
		p_steps = np.floor(self.n * self.s)
		# if p_steps is smaller than one, we will have only one production step
		if (p_steps < 1):
			p_steps	= 1

		# update production rate
		self.production_rate = p_steps / self.n

		# create a index for naming the nodes as they are being assigned to productions steps
		node_index = 0

		# create a dictionary of list of nodes for every step
		work_stations = {}

		# create vertex attribute dictionary
		vertex_attr = {}
		# create lists for vertex attributes:
		failure_rate_list = []
		production_rate_list = []
		label_list = []

		for step in range(int(p_steps)):

			# create a empty node_list
			node_list = []
			# append one node to the list
			node_list.append(node_index)
			# append the list into the work stations dictionary
			work_stations[step] = node_list

			# update the node_index and the vertex attribute list
			label_list.append(node_index)
			node_index = node_index	+ 1
			failure_rate_list.append(self.failure_rate)
			production_rate_list.append(self.production_rate)

		# now while there are node not yet assigned to any production step
		# assign the with uniform distribution

		while (node_index < self.n):

			# draw a sample from the uniform distribution
			r_uniform = np.random.default_rng().uniform(0,p_steps,1)
			# the production step for the next node will be the floor of the sample
			ws_next_node = int(np.floor(r_uniform))
			# append the new node to the respective node list
			work_stations[ws_next_node].append(node_index)
			# update node index and attribute lists
			label_list.append(node_index)
			node_index = node_index	+ 1
			failure_rate_list.append(self.failure_rate)
			production_rate_list.append(self.production_rate)

		# update the vertex attribute dictionary
		vertex_attr["failure_rate"] = failure_rate_list
		vertex_attr["production_rate"] = production_rate_list
		vertex_attr["label"] = label_list

		# a node from production step i need to receive supplies from
		# all nodes in the preceding production step, and supply for all node in the
		# sucedding production step

		# create a dictionary of edge attributes
		edge_attr = {}
		# create an attribute list
		attr = []

		# create array of edges
		production_edges = []
		# range(p_steps-1) because it is creating edges between the present step and the next
		# and the last production step does not have a next step
		for step in (range(int(p_steps)-1)):
			for node in work_stations[step]:
				for next_node in work_stations[step+1]:
					production_edges.append([node, next_node])
					# for every edge created, append the buffer size
					# to the attr list
					attr.append(self.buffer_size)

		edge_attr["buffer_size"] = attr

		return work_stations, production_edges, edge_attr, vertex_attr