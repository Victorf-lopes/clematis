import numpy as np

class ModelGeneratorNS:
	# model reponsible for generating factory floor acyclic directed graphs
	# parameters:
	# n -> number of nodes/work stations
	# s -> number of production steps required
	#
	# every step in the production have at least one node/work station
	#
	# every node placed in production-step i is supplied from all the nodes in production-step i-1
	# and supplies for all the nodes in production-step i+1
	#
	# other parameter that can be supplied to the model is the number of machines in the first
	# and last production step
	#
	# that is to say: the model has no restrictions of raw material or demand of finished products
	#
	# node attributes: production_rate; failure_rate; buffer_size
	# edge attributes: 
	#
	#
	# in the basic version, the node and edge attributes will be the same for all the network elements
	
	def __init__(self, n, s, first_step = -1, last_step = -1, failure_rate=0.1, buffer_size=1, production_rate=1, production_level="constant", production_delta=0.1):
		# network parameters
		self.n = n
		self.p_steps = s
		self.failure_rate = failure_rate
		self.buffer_size = buffer_size
		self.production_rate = production_rate
		self.first_step = first_step
		self.last_step = last_step
		self.production_level = production_level # constant || uniform || decrescent
		self.production_delta = production_delta

	def generate_graph(self):

		# create a index for naming the nodes as they are being assigned to productions steps
		node_index = 0

		# create a dictionary of list of nodes for every step
		work_stations = {}

		# create vertex attribute dictionary
		vertex_attr = {}
		# create lists for vertex attributes:
		failure_rate_list = []
		production_rate_list = []
		buffer_size_list = []
		label_list = []
		production_step_list = []

		for step in range(self.p_steps):

			# create a empty node_list
			node_list = []

			# if first step and assigned a specific number of machines to this step
			if (step==0 and self.first_step!=-1):

				for node in range(self.first_step):
					# append one node to the list
					node_list.append(node_index)

					# update the node_index and the vertex attribute list
					label_list.append(node_index)
					node_index = node_index	+ 1
					failure_rate_list.append(self.failure_rate)
					production_rate_list.append(self.production_rate)
					buffer_size_list.append(self.buffer_size)
					production_step_list.append(step)
				
				# append the list into the work stations dictionary
				work_stations[step] = node_list
				continue

			# if last step and assigned a specific number of machines to this step
			if (step==(self.p_steps-1) and self.last_step!=-1):

				for node in range(self.last_step):
					# append one node to the list
					node_list.append(node_index)
					print('here')

					# update the node_index and the vertex attribute list
					label_list.append(node_index)
					node_index = node_index	+ 1
					failure_rate_list.append(self.failure_rate)
					production_rate_list.append(self.production_rate)
					buffer_size_list.append(self.buffer_size)
					production_step_list.append(step)
				
				# append the list into the work stations dictionary
				work_stations[step] = node_list
				continue

			# append one node to the list
			node_list.append(node_index)
			# append the list into the work stations dictionary
			work_stations[step] = node_list

			# update the node_index and the vertex attribute list
			label_list.append(node_index)
			node_index = node_index	+ 1
			failure_rate_list.append(self.failure_rate)
			production_rate_list.append(self.production_rate)
			buffer_size_list.append(self.buffer_size)
			production_step_list.append(step)

		# now while there are node not yet assigned to any production step
		# assign them with uniform distribution

		while (node_index < self.n):

			# if a specif number of machines were assigned to the first and last layer
			# don't assign more nodes to them
			if self.first_step != -1 and self.last_step != -1:
				# draw a sample from the uniform distribution
				r_uniform = np.random.default_rng().uniform(1,self.p_steps-1,1)
			elif self.first_step != -1:
				# draw a sample from the uniform distribution
				r_uniform = np.random.default_rng().uniform(1,self.p_steps,1)
			elif self.last_step != -1:
				r_uniform = np.random.default_rng().uniform(0,self.p_steps-1,1)
			else:
				# draw a sample from the uniform distribution
				r_uniform = np.random.default_rng().uniform(0,self.p_steps,1)

			# the production step for the next node will be the floor of the sample
			ws_next_node = int(np.floor(r_uniform))
			# append the new node to the respective node list
			work_stations[ws_next_node].append(node_index)
			# update node index and attribute lists
			label_list.append(node_index)
			node_index = node_index	+ 1
			failure_rate_list.append(self.failure_rate)
			production_rate_list.append(self.production_rate)
			buffer_size_list.append(self.buffer_size)
			production_step_list.append(ws_next_node)

		# a node from production step i need to receive supplies from
		# all nodes in the preceding production step, and supply for all node in the
		# sucedding production step

		# create array of edges
		production_edges = []
		# range(p_steps-1) because it is creating edges between the present step and the next
		# and the last production step does not have a next step
		for step in range(self.p_steps-1):
			for node in work_stations[step]:
				for next_node in work_stations[step+1]:
					production_edges.append([node, next_node])

		# check if the production level has any special characteristic
		if self.production_level == "uniform":
			print("[INFO] production level uniform for all production steps selected...")
			for step in range(self.p_steps):
				# number of machines in that step
				n_machines = len(work_stations[step])
				# production rate for each machine in that step
				p_rate = self.production_rate / n_machines

				for node in work_stations[step]:
					# update production rate for that node
					production_rate_list[node] = p_rate
		
		elif self.production_level == "decrescent":
			print("[INFO] decrescent production level selected...")
			# calculate initial production rate and delta production rate
			initial_prod_rate = self.production_rate * (1+self.production_delta)
			delta_prod_rate = initial_prod_rate - self.production_rate

			for step in range(self.p_steps):
				# number of machines in that step
				n_machines = len(work_stations[step])
				# calculate production rate for the production step
				p_rate = initial_prod_rate - (step*delta_prod_rate)/(self.p_steps-1)
				p_rate = p_rate / n_machines

				for node in work_stations[step]:
					# update production rate for that node
					production_rate_list[node] = p_rate

		# update the vertex attribute dictionary
		vertex_attr["failure_rate"] = failure_rate_list
		vertex_attr["production_rate"] = production_rate_list
		vertex_attr["label"] = label_list
		vertex_attr["buffer_size"] = buffer_size_list
		vertex_attr["production_step"] = production_step_list

		return work_stations, production_edges, vertex_attr