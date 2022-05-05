import sys
import numpy as np
from igraph import *

class DynamicManufacturing:

	def __init__(self, network, seed):
		# Parameters
		# network: igraph.Graph

		self.network = network
		self.time = 0

		self.buffer = np.array([0.0 for i in range(network.vcount())])
		self.buffer_occupation = np.array([0.0 for i in range(network.vcount())])
		self.state = np.array(["starved" for i in range(network.vcount())])
		self.last_state = np.array([0 for i in range(network.vcount())])  # array used to check if the nodes are changing state
		self.state_id = np.array([0 for i in range(network.vcount())]) 
		# 0 -> starved / 1 -> blocked / 2 -> working

		# calculate the topological sorting only once
		self.sorted_nodes_list = self.network.topological_sorting()

		# random number generator
		# the numbers generated are smaller than 1
		self.rng = np.random.default_rng(seed=seed)

	def iterate(self, output, write2file=False):
		# output is a file to output data from the simulation

		# initialize production
		total_production = 0

		# write the header to the file
		if self.time == 0:
			#output.write("time,vertex,state,state_id,buffer_occupation,production_step\n")
			output.write("time,starved,blocked,working\n")

		# increase time
		self.time = self.time + 1

		ids = self.network.vs["label"]
		prate = np.array(self.network.vs["production_rate"])
		frate = np.array(self.network.vs["failure_rate"])
		buffer_size = np.array(self.network.vs["buffer_size"])
		production_step = np.array(self.network.vs["production_step"])

		# initialize state array, with all nodes working
		state_array = np.array([2.0 for i in range(np.max(production_step)+1)])

		# initialize the count of starved, blocked and working nodes
		zero_count = 0
		one_count = 0
		two_count = 0

		# loop through the nodes in the network sorted in
		# topological order
		for i in self.sorted_nodes_list:
			# calculate the in and out edges of node i
			# and make a list of in and out nodes linked to the node
			in_nodes = [self.network.get_edgelist()[edge.index][0] for edge in self.network.vs[i].in_edges()]
			out_nodes = [self.network.get_edgelist()[edge.index][1] for edge in self.network.vs[i].out_edges()]

			# check if any of the elements feeded by node i has space to receive
			# materials. If any node has possibility to recceive materials, node i
			# can produce them.
			if len(out_nodes) > 0 and np.all(self.buffer[out_nodes] >= buffer_size[out_nodes]):
				# if all nodes receiving from i are full, i is blocked
				self.state[i] = "blocked"
				self.state_id[i] = 1
				# 0 -> starved / 1 -> blocked / 2 -> working
				if (state_array[production_step[i]] == 2):
					# change it only if it's was working, to blocked
					state_array[production_step[i]] = 1;

			# if it is a node in the first production step, it is not starved
			elif len(in_nodes) == 0:
				self.state[i] = "working"
				self.state_id[i] = 2
				# 0 -> starved / 1 -> blocked / 2 -> working

			# if it does not have any raw materials, it is starved
			elif self.buffer[i] == 0:
				self.state[i] = "starved"
				self.state_id[i] = 0
				# 0 -> starved / 1 -> blocked / 2 -> working
				state_array[production_step[i]] = 0;

			else:
				self.state[i] = "working"
				self.state_id[i] = 2
				# 0 -> starved / 1 -> blocked / 2 -> working

			# update the count of the node state
			if self.state_id[i] == 0:
				zero_count = zero_count + 1
			elif self.state_id[i] == 1:
				one_count = one_count + 1
			elif self.state_id[i] == 2:
				two_count = two_count + 1

			# check if the machine is working and does not experience failure
			if self.state[i] == "working" and self.rng.random() > frate[i]:

				# calculate production
				production = prate[i]

				# if it has incoming edges, it can make the production rate
				# only if it has enough material on its buffer
				if len(in_nodes) > 0:
					production = min(production, self.buffer[i])

				# its production can be at maximum the amount available in the
				# buffers of the nodes ahead
				if len(out_nodes) > 0:
					production = min(production, np.max(buffer_size[out_nodes]-self.buffer[out_nodes]))

				# produce!
				# decrease its own buffer by the amount of product it make
				if len(in_nodes) > 0:
					self.buffer[i] = self.buffer[i] - production

				# increase the amount of product in the buffer of the node it is providing
				if len(out_nodes) > 0:
					# find the out_node with minimum occupation on its buffer
					index = np.argmin(self.buffer[out_nodes])
					node_to_feed = out_nodes[index]
					self.buffer[node_to_feed] = np.minimum(buffer_size[node_to_feed], self.buffer[node_to_feed]+production)
				# if the node does not have outgoing edges, the production is
				# the production of the whole process
				else:
					total_production = total_production + production

				self.buffer_occupation[i] = self.buffer[i]/buffer_size[i]

		# write status to file
		if write2file:
			output.write("{},{},{},{}\n".format(self.time, zero_count, one_count, two_count))
			#output.write("{},{},{},{},{},{}\n".format(self.time, ids[i], self.state[i], self.state_id[i], self.buffer_occupation[i], production_step[i]))

		# check how many nodes changed their ID
		#zero_count = self.state_id.tolist().count(0)
		#one_count = self.state_id.tolist().count(1)
		#two_count = self.state_id.tolist().count(2)

		#return total_production, zero_count, one_count, two_count, state_array
		return total_production, zero_count, one_count, two_count, state_array



