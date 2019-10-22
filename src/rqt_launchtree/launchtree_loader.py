#!/usr/bin/env python
import sys

from roslaunch.xmlloader import XmlLoader, loader
from xml.dom import Node as DomNode #avoid aliasing 
from rosgraph.names import get_ros_namespace

from rqt_launchtree.launchtree_context import LaunchtreeContext


class LaunchtreeLoader(XmlLoader):
	groupIndex = 0
	#def _pseudo_recurse_load(self, ros_config, tags, context, default_machine, is_core, verbose):
	#	x = self._recurse_load(ros_config, tags, context, default_machine, is_core, verbose) 
	#	return x

	def _recurse_load(self, ros_config, tags, context, default_machine, is_core, verbose): 
		#if(not self.PSEUDO):
		for tag in [t for t in tags if t.nodeType == DomNode.ELEMENT_NODE]: 
			name = tag.tagName 
			if name == 'group': 
				if True: 
					self._group_tag(tag, context, ros_config, default_machine, is_core, verbose)
			elif name == 'node': 
				n = self._node_tag(tag, context, ros_config, default_machine, verbose=verbose) 
				if n is not None: 
					ros_config.add_node(n, core=is_core, verbose=verbose) 
			elif name == 'test': 
				t = self._node_tag(tag, context, ros_config, default_machine, is_test=True, verbose=verbose) 
				if t is not None: 
					ros_config.add_test(t, verbose=verbose) 
			elif name == 'param': 
				self._param_tag(tag, context, ros_config, verbose=verbose) 
			elif name == 'remap': 
				try: 
					r = self._remap_tag(tag, context, ros_config) 
					if r is not None: 
						context.add_remap(r) 
				except RLException as e: 
					raise XmlParseException("Invalid <remap> tag: %s.\nXML is %s"%(str(e), tag.toxml())) 
			elif name == 'machine': 
				val = self._machine_tag(tag, context, ros_config, verbose=verbose) 
				if val is not None: 
					(m, is_default) = val 
					#if is_default: 
					default_machine = m 
					ros_config.add_machine(m, verbose=verbose) 
			elif name == 'rosparam': 
				self._rosparam_tag(tag, context, ros_config, verbose=verbose) 
			elif name == 'master': 
				pass #handled non-recursively 
			elif name == 'include': 
				val = self._include_tag(tag, context, ros_config, default_machine, is_core, verbose) 
				if val is not None: 
					default_machine = val 
			elif name == 'env': 
				self._env_tag(tag, pseudo_context, ros_config)
			elif name == 'arg': 
				#if(is_core):
				#	pseudo_context = context
				#	pseudo_config = ros_config
				#	self._arg_tag(tag, pseudo_context, pseudo_config, verbose=verbose) 
				#else:
				self._arg_tag(tag, context, ros_config, verbose=verbose) 
			else: 
				ros_config.add_config_error("unrecognized tag "+tag.tagName) 



		#else:
		#	for tag in [t for t in tags if t.nodeType == DomNode.ELEMENT_NODE]: 
		#		name = tag.tagName 
		#	
		#		#if name == 'include': 
		#		#	val = self._include_tag(tag, context, ros_config, default_machine, is_core, verbose) 
		#		#	if val is not None: 
		#		#		default_machine = val 
		#		if name == 'env': 
		#			self._env_tag(tag, context, ros_config) 
		#		elif name == 'arg': 
		#			self._arg_tag(tag, context, ros_config, verbose=verbose)
#
#		#	for tag in [t for t in tags if t.nodeType == DomNode.ELEMENT_NODE]: 
#		#		name = tag.tagName 
#		#		if name == 'machine': 
#		#			val = self._machine_tag(tag, context, ros_config, verbose=verbose) 
#		#			if val is not None: 
#		#				(m, is_default) = val 
#		#				default_machine = m 
		#				
		return default_machine 
   


	def _group_tag(self, tag, context, ros_config, default_machine, is_core, verbose):
		name = tag.tagName 
		self._check_attrs(tag, context, ros_config, XmlLoader.GROUP_ATTRS) 
		child_ns = self._ns_clear_params_attr(name, tag, context, ros_config) 
		groupName = "" % child_ns.ns if child_ns.ns != "/" else "[%s]" % LaunchtreeLoader.groupIndex 

		insertedLevel = ros_config.push_level(groupName)
		default_machine = self._recurse_load(ros_config, tag.childNodes, child_ns, default_machine, is_core, verbose) 
		groupName = "%s %s" % (ros_config._tree_stack[-1], default_machine.name)
		ros_config.pop_level()

#		ros_config._tree_stack[-1] = groupName
		#ros_config.tree[groupName] = ros_config.tree.pop(insertedLevel)
		#for k, v in ros_config.tree.items():
#
#			if(insertedLevel in k):
#				print("WTF %s" % k)
#				ros_config.tree[groupName] = ros_config.tree.pop(insertedLevel)
#			#if(isinstance(v, dict)):
#			#	if(insertedLevel in v.keys):
#			#		print("NUF %s" % v)
#		
#		print(ros_config.tree.keys())


		context.add_group(groupName, context, internalMachineInstance=default_machine)
		LaunchtreeLoader.groupIndex += 1

	def _include_tag(self, tag, context, ros_config, default_machine, is_core, verbose):
		inc_filename = self.resolve_args(tag.attributes['file'].value, context)
		#print("loading _include_tag %s" % inc_filename)
		ros_config.push_level(inc_filename, unique=True)
		#print(inc_filename, ros_config.machines.keys()[-1])
		#default_machine = ros_config.machines.keys()[-1]
		result = super(LaunchtreeLoader, self)._include_tag(tag, context, ros_config, default_machine, is_core, verbose)
		ros_config.pop_level()
		return result

	def _node_tag(self, tag, context, ros_config, default_machine, is_test=False, verbose=True):
		try: 
			if is_test: 
				self._check_attrs(tag, context, ros_config, XmlLoader.TEST_ATTRS) 
				(name,) = self.opt_attrs(tag, context, ('name',))  
				test_name, time_limit, retry = self._test_attrs(tag, context) 
				if not name: 
					name = test_name 
			else: 
				self._check_attrs(tag, context, ros_config, XmlLoader.NODE_ATTRS) 
				(name,) = self.reqd_attrs(tag, context, ('name',))
		except Exception as e:
			pass # will be handled in super

		ros_config.push_level(name)
		result = super(LaunchtreeLoader, self)._node_tag(tag, context, ros_config, default_machine, is_test, verbose)
		#print(result.machine)
		ros_config.pop_level()
		return result

	def _rosparam_tag(self, tag, context, ros_config, verbose):
		param_file = tag.attributes['file'].value \
			if tag.attributes.has_key('file') else ''
		if param_file != '': 
			param_filename = self.resolve_args(param_file, context)
			level_name = ros_config.push_level(param_filename, unique=True)
		result = super(LaunchtreeLoader, self)._rosparam_tag(tag, context, ros_config, verbose)
		if param_file != '': 
			ros_config.pop_level()
			context.add_rosparam(tag.attributes.get('command', 'load'), param_filename, level_name)
		return result

	def _load_launch(self, launch, ros_config, is_core=False, filename=None, argv=None, verbose=True):
		LaunchtreeLoader.groupIndex = 0
		if argv is None:
			argv = sys.argv
		self._launch_tag(launch, ros_config, filename)
		self.root_context = LaunchtreeContext(get_ros_namespace(), filename, config=ros_config)
		loader.load_sysargs_into_context(self.root_context, argv)

		if len(launch.getElementsByTagName('master')) > 0:
			print "WARNING: ignoring defunct <master /> tag"
		self._recurse_load(ros_config, launch.childNodes, self.root_context, None, is_core, verbose)

