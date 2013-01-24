from django.test import TestCase
from courseware import grades
from mock import MagicMock

# from __future__ import division

# import random
# import logging

from collections import defaultdict
from django.conf import settings
from django.contrib.auth.models import User

# from models import StudentModuleCache
from courseware.module_render import get_module as get_module
from courseware.module_render import get_instance_module as get_instance_module
# from xmodule import graders
from xmodule.capa_module import CapaModule


class test_grades(TestCase):

	def test_yield_module_descendents(self):
		mock_module = MagicMock()
		a = MagicMock()
		b = MagicMock()
		c = MagicMock()
		z = MagicMock()
		y = MagicMock()
		mock_module.get_display_items.return_value = [a, b, c]
		a.get_display_items.return_value = [y, z]  
		b.get_display_items.return_value = []
		c.get_display_items.return_value = []
		z.get_display_items.return_value = []
		y.get_display_items.return_value = []
		dummy = list(grades.yield_module_descendents(mock_module))
		self.assertEqual(dummy, [a,z,y,b,c])

	def test_yield_dynamic_descriptor_descendents(self):
		descriptor_true_mock = MagicMock()
		a = MagicMock()
		b = MagicMock()
		b.has_dynamic_children.return_value = False
		b.get_children.return_value = 'b'
		c = MagicMock()
		c.has_dynamic_children.return_value = False
		c.get_children.return_value = 'c'
		e = MagicMock()
		e.has_dynamic_children.return_value = False
		e.get_children.return_value = None

		descriptor_true_mock.return_value = a
		descriptor_true_mock.has_dynamic_children.return_value = True
		module_creator_mock = MagicMock()
		module_mock = MagicMock()
		module_creator_mock(descriptor_true_mock).return_value = module_mock
		child_locations_mock = MagicMock()
		module_mock.get_children_locations.__iter__.return_value = [b, c]
		print descriptor_true_mock.system.load_item(b)
		

		descriptor_true_mock.system.load_item(b).return_value = b
		descriptor_true_mock.system.load_item(c).return_value = c

		descriptor_false_mock = MagicMock()
		descriptor_false_mock.has_dynamic_children.return_value = False
		descriptor_false_mock.get_children.return_value = e

		true_descriptor_children_list = [descriptor_true_mock]
		self.assertEqual(list(grades.yield_dynamic_descriptor_descendents(descriptor_true_mock, module_creator_mock)),true_descriptor_children_list)					
		self.assertEqual(list(grades.yield_dynamic_descriptor_descendents(descriptor_false_mock, module_creator_mock)),[descriptor_false_mock])	

	def test_yield_problems(self):
		course_mock = MagicMock()
		# course = course_mock
		grading_context_mock = MagicMock()
		# mock for grading context
		course_mock.grading_context.return_value = grading_context_mock	

		# mock for course.id
		course_id_mock = MagicMock()
		course_mock.id.return_value = course_id_mock

		# mock for student
		student_mock = MagicMock()
		student = student_mock()

		grading_context_mock['all_descriptors'] = MagicMock()
		sec_form1 = MagicMock()
		sec_form2 = MagicMock()
		sec1 = MagicMock()
		sec1['section_descriptor'].return_value = "sec1 descriptor"
		sec2 = MagicMock()
		sec2['section_descriptor'].return_value = "sec2 descriptor"
		sec3 = MagicMock()
		sec3['section_descriptor'].return_value = "sec3 descriptor"
		sec4 = MagicMock()
		sec4['section_descriptor'].return_value = "sec4 descriptor"
		grading_context_mock['all_descriptors'].__iter__.return_value = [(sec_form1, [sec1, sec2]), (sec_form2, [sec3, sec4])]
		StudentModuleCache_mock = MagicMock()
		student_module_cache_mock = MagicMock()
		StudentModuleCache_mock(course_id_mock, student_mock, grading_context_mock['all_descriptors']).return_value = student_module_cache_mock
		
		sec1_xmod = MagicMock()
		sec2_xmod = MagicMock()
		sec3_xmod = MagicMock()
		sec4_xmod = MagicMock()
		sec1['xmoduledescriptors'].return_value = [sec1_xmod]
		sec2['xmoduledescriptors'].return_value = [sec2_xmod]
		sec3['xmoduledescriptors'].return_value = [sec3_xmod]
		sec4['xmoduledescriptors'].return_value = [sec4_xmod]
		sec1_xmod_category = MagicMock()			
		sec2_xmod_category = MagicMock()
		sec3_xmod_category = MagicMock()
		sec4_xmod_category = MagicMock()
		sec1_xmod.category.return_value = sec1_xmod_category
		sec2_xmod.category.return_value = sec2_xmod_category
		sec3_xmod.category.return_value = sec3_xmod_category
		sec4_xmod.category.return_value = sec4_xmod_category
		sec1_xmod_location_url = MagicMock()
		sec2_xmod_location_url = MagicMock()
		sec3_xmod_location_url = MagicMock()
		sec4_xmod_location_url = MagicMock()
		sec1_xmod.location.url.return_value = sec1_xmod_location_url
		sec2_xmod.location.url.return_value = sec2_xmod_location_url
		sec3_xmod.location.url.return_value = sec3_xmod_location_url
		sec4_xmod.location.url.return_value = sec4_xmod_location_url
		student_module_cache_mock.lookup(course_id_mock,sec1_xmod, sec1_xmod.location.url()).return_value = True
		student_module_cache_mock.lookup(course_id_mock,sec2_xmod, sec2_xmod.location.url()).return_value = True
		student_module_cache_mock.lookup(course_id_mock,sec3_xmod, sec3_xmod.location.url()).return_value = False
		student_module_cache_mock.lookup(course_id_mock,sec4_xmod, sec4_xmod.location.url()).return_value = False

		student_mock = MagicMock()
		request_mock = MagicMock()
		sec1_module_mock = MagicMock()
		sec2_module_mock = MagicMock()
		sec3_module_mock = MagicMock()
		sec4_module_mock = MagicMock()
		get_module_mock = MagicMock()
		get_module_mock(student_mock, request_mock, sec1_xmod.location, student_module_cache_mock, course_id_mock).return_value = sec1_module_mock
		get_module_mock(student_mock, request_mock, sec2_xmod.location, student_module_cache_mock, course_id_mock).return_value = sec2_module_mock
		get_module_mock(student_mock, request_mock, sec3_xmod.location, student_module_cache_mock, course_id_mock).return_value = sec3_module_mock
		get_module_mock(student_mock, request_mock, sec4_xmod.location, student_module_cache_mock, course_id_mock).return_value = sec4_module_mock
		prob1 = MagicMock()
		prob2 = MagicMock()
		prob3 = MagicMock()
		prob4 = MagicMock()
		prob5 = MagicMock()
		prob6 = MagicMock()
		prob7 = MagicMock()
		prob8 = MagicMock()
		yield_module_descendents_mock = MagicMock()
		yield_module_descendents_mock(sec1_module_mock).return_value = [prob1, prob2]
		yield_module_descendents_mock(sec2_module_mock).return_value = [prob3, prob4]
		yield_module_descendents_mock(sec3_module_mock).return_value = [prob5, prob6]
		yield_module_descendents_mock(sec4_module_mock).return_value = [prob7, prob8]

		self.assertEqual(list(grades.yield_problems(request_mock, course_mock, student_mock)), [])
		
	def test_answer_distributions(self):
		request_mock = MagicMock()
		course_mock = MagicMock()
		course_id_mock = MagicMock()
		course_mock.id.return_value = ('dummy')
		student1 = MagicMock()
		student2 = MagicMock()
		capa_module_mock2 = MagicMock()
		# capa_module_mock2.return_value = capa_module
		capa_module_mock = MagicMock()
		# capa_module_mock.__iter__ = [capa_module_mock2]
		# capa_module_mock2.return_value = [capa_module_mock]
		User.objects.filter(courseenrollment__course_id=course_id_mock).return_value = (student1, student2)
		# print enrolled_students

		grades.yield_problems(request_mock, course_mock, student1) = MagicMock()
		self.assertEqual(list(grades.yield_problems(request_mock, course_mock, student1)), []) # = MagicMock(return_value=iter([capa_module_mock]))

		
		id1 = MagicMock()
		id2 = MagicMock()
		capa_module_mock.lcp.student_answers_mock.return_value= [id1, id2]
		answer1 = MagicMock()
		answer2 = MagicMock()
		answer1.return_value = "answer1"
		answer2.return_value = "answer2"
		capa_module_mock.lcp.student_answers[id1].return_value = answer1
		capa_module_mock.lcp.student_answers[id2].return_value = answer2
		url_name_mock = MagicMock()
		display_name_mock = MagicMock()
		capa_module_mock.display_name.return_value = display_name_mock
		capa_module_mock.url_name = url_name_mock

		d = defaultdict(lambda: defaultdict(int))
		e = defaultdict(lambda: defaultdict(int))
		d[(url_name_mock, display_name_mock, id1)][answer1] = 1
		d[(url_name_mock, display_name_mock, id2)][answer2] = 1
		self.assertEqual(grades.answer_distributions(request_mock, course_mock),e)


		# defaultdict(<function <lambda> at 0x104d7f6e0>, {}) != 
		# defaultdict(<function <lambda> at 0x104d7f398>, {(<MagicMock name='mock.url_name' id='4376250000'>, <MagicMock name='mock.display_name()' id='4376254736'>, <MagicMock id='4376207312'>): 
		# 	defaultdict(<type 'int'>, {<MagicMock name='mock.lcp.student_answers.__getitem__()()' id='4376226384'>: 1}), (<MagicMock name='mock.url_name' id='4376250000'>, <MagicMock name='mock.display_name()' id='4376254736'>, <MagicMock id='4376202576'>): defaultdict(<type 'int'>, {<MagicMock name='mock.lcp.student_answers.__getitem__()()' id='4376221584'>: 1})})