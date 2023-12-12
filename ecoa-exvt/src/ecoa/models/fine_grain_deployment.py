# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict


class Physical_Core:
	"""Describes a physical core

	Attributes:
		node_name     (str): name of node
		platfome_name (str): name of platform
		core_id       (int): id of core on this node
	"""
	def __init__(self, node_name, platform_name, core_id):
		self.node_name = node_name
		self.platform_name = platform_name
		self.core_id = core_id

	def __eq__(self, other):
		return self.node_name == other.node_name and \
			   self.platform_name == other.platform_name and \
			   self.core_id == other.core_id

class Deployed_Module_Affinity:
	"""Describe CPU affinity of a deployed module

	Attributes:
		name           (str): name of the module
		component name (str): name of the module's component
		core_ids       (set): set of ID (int) of cores on which module can run
	"""
	def __init__(self, name, component_name):
		self.name = name
		self.component_name = component_name
		self.core_ids=set()

	def add_core(self, id):
		self.core_ids.add(id)

class PD_Deployment:
	"""Describe deployment properties of Protection Domain:

	Attributes:
		name              (str): name of protection domain
		node_name         (str): name of executing node of protection domain
		plaform_name      (str): name of platform of protection domain
		scheduling_policy (str): scheduling policy of protection domain process (FIFO, RR, BATCH, IDLE, OTHER)
		default_cores	  (set): default set of IDs (int) of cores on which modules can run
		deployed_modules_affinity (list):list of :class:`.Deployed_Module_Affinity` to describe CPU affinity of deployed modules
	"""
	def __init__(self, name, node_name, platform_name, sched_policy):
		self.name = name
		self.node_name = node_name
		self.platform_name = platform_name
		self.scheduling_policy = sched_policy
		self.default_cores = set()
		self.deployed_modules_affinity = []

	def add_deployed_module_affinity(self, new_module):
		self.deployed_modules_affinity.append(new_module)

	def add_default_core(self, id):
		self.default_cores.add(id)

	def find_module_affinity(self, mod_name, comp_name):
		"""Find :class:`.Deployed_Module_Affinity` of deployed module

		Args:
			mod_name  (str): deployed module name
			comp_name (str): component name of module

		return:
			(:class:`.Deployed_Module_Affinity`): None if deployed module is not found
		"""
		for dep_mod in self.deployed_modules_affinity:
			if mod_name == dep_mod.name and comp_name == dep_mod.component_name:
				return dep_mod

		return None

class Fine_Grain_Deployment:
	"""Describe fine grain deployment of an LDP platform
	"""
	def __init__(self):
		self.technical_cores=[]
		self.protection_domain_deployment=OrderedDict()

	def add_technical_core(self, node_name, platform_name, core_id):
		"""Add a physical core for technical threads

		Args:
			node_name     (str): The node name
			platform_name (str): The platform name
			core_id       (int): The core ID
		"""
		new_core = Physical_Core(node_name, platform_name, core_id)

		# avoid double
		if new_core not in self.technical_cores:
			self.technical_cores.append(new_core)

	def add_protection_domain(self, protection_domain, name):
		self.protection_domain_deployment[name] = protection_domain

	def get_protection_domain(self,pd_name):
		if pd_name in self.protection_domain_deployment:
			return self.protection_domain_deployment[pd_name]
		else:
			return None

	def get_PD_sched_policy(self, pd_name):
		if pd_name in self.protection_domain_deployment:
			return self.protection_domain_deployment[pd_name].scheduling_policy
		else:
			return "OTHER"
