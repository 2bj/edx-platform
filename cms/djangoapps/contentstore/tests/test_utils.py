""" Tests for utils. """
import collections
import copy
import mock
import time
from contentstore import utils

from django.test import TestCase

from student.tests.factories import UserFactory
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase


class LMSLinksTestCase(TestCase):
    """ Tests for LMS links. """
    def about_page_test(self):
        """ Get URL for about page. """
        location = 'i4x', 'mitX', '101', 'course', 'test'
        utils.get_course_id = mock.Mock(return_value="mitX/101/test")
        link = utils.get_lms_link_for_about_page(location)
        self.assertEquals(link, "//localhost:8000/courses/mitX/101/test/about")

    def lms_link_test(self):
        """ Tests get_lms_link_for_item. """
        location = 'i4x', 'mitX', '101', 'vertical', 'contacting_us'
        utils.get_course_id = mock.Mock(return_value="mitX/101/test")
        link = utils.get_lms_link_for_item(location, False)
        self.assertEquals(link, "//localhost:8000/courses/mitX/101/test/jump_to/i4x://mitX/101/vertical/contacting_us")
        link = utils.get_lms_link_for_item(location, True)
        self.assertEquals(
            link,
            "//preview/courses/mitX/101/test/jump_to/i4x://mitX/101/vertical/contacting_us"
        )


class UrlReverseTestCase(ModuleStoreTestCase):
    """ Tests for get_url_reverse """
    def test_course_page_names(self):
        """ Test the defined course pages. """
        course = CourseFactory.create(org='mitX', number='666', display_name='URL Reverse Course')

        self.assertEquals(
            '/manage_users/i4x://mitX/666/course/URL_Reverse_Course',
            utils.get_url_reverse('ManageUsers', course)
        )

        self.assertEquals(
            '/mitX/666/settings-details/URL_Reverse_Course',
            utils.get_url_reverse('SettingsDetails', course)
        )

        self.assertEquals(
            '/mitX/666/settings-grading/URL_Reverse_Course',
            utils.get_url_reverse('SettingsGrading', course)
        )

        self.assertEquals(
            '/mitX/666/course/URL_Reverse_Course',
            utils.get_url_reverse('CourseOutline', course)
        )

        self.assertEquals(
            '/mitX/666/checklists/URL_Reverse_Course',
            utils.get_url_reverse('Checklists', course)
        )

    def test_unknown_passes_through(self):
        """ Test that unknown values pass through. """
        course = CourseFactory.create(org='mitX', number='666', display_name='URL Reverse Course')
        self.assertEquals(
            'foobar',
            utils.get_url_reverse('foobar', course)
        )
        self.assertEquals(
            'https://edge.edx.org/courses/edX/edX101/How_to_Create_an_edX_Course/about',
            utils.get_url_reverse('https://edge.edx.org/courses/edX/edX101/How_to_Create_an_edX_Course/about', course)
        )


class ExtraPanelTabTestCase(TestCase):
    """ Tests adding and removing extra course tabs. """

    def get_tab_type_dicts(self, tab_types):
        """ Returns an array of tab dictionaries. """
        if tab_types:
            return [{'tab_type': tab_type} for tab_type in tab_types.split(',')]
        else:
            return []

    def get_course_with_tabs(self, tabs=[]):
        """ Returns a mock course object with a tabs attribute. """
        course = collections.namedtuple('MockCourse', ['tabs'])
        if isinstance(tabs, basestring):
            course.tabs = self.get_tab_type_dicts(tabs)
        else:
            course.tabs = tabs
        return course

    def test_add_extra_panel_tab(self):
        """ Tests if a tab can be added to a course tab list. """
        for tab_type in utils.EXTRA_TAB_PANELS.keys():
            tab = utils.EXTRA_TAB_PANELS.get(tab_type)

            # test adding with changed = True
            for tab_setup in ['', 'x', 'x,y,z']:
                course = self.get_course_with_tabs(tab_setup)
                expected_tabs = copy.copy(course.tabs)
                expected_tabs.append(tab)
                changed, actual_tabs = utils.add_extra_panel_tab(tab_type, course)
                self.assertTrue(changed)
                self.assertEqual(actual_tabs, expected_tabs)

            # test adding with changed = False
            tab_test_setup = [
                [tab],
                [tab, self.get_tab_type_dicts('x,y,z')],
                [self.get_tab_type_dicts('x,y'), tab, self.get_tab_type_dicts('z')],
                [self.get_tab_type_dicts('x,y,z'), tab]]

            for tab_setup in tab_test_setup:
                course = self.get_course_with_tabs(tab_setup)
                expected_tabs = copy.copy(course.tabs)
                changed, actual_tabs = utils.add_extra_panel_tab(tab_type, course)
                self.assertFalse(changed)
                self.assertEqual(actual_tabs, expected_tabs)

    def test_remove_extra_panel_tab(self):
        """ Tests if a tab can be removed from a course tab list. """
        for tab_type in utils.EXTRA_TAB_PANELS.keys():
            tab = utils.EXTRA_TAB_PANELS.get(tab_type)

            # test removing with changed = True
            tab_test_setup = [
                [tab],
                [tab, self.get_tab_type_dicts('x,y,z')],
                [self.get_tab_type_dicts('x,y'), tab, self.get_tab_type_dicts('z')],
                [self.get_tab_type_dicts('x,y,z'), tab]]

            for tab_setup in tab_test_setup:
                course = self.get_course_with_tabs(tab_setup)
                expected_tabs = [t for t in course.tabs if t != utils.EXTRA_TAB_PANELS.get(tab_type)]
                changed, actual_tabs = utils.remove_extra_panel_tab(tab_type, course)
                self.assertTrue(changed)
                self.assertEqual(actual_tabs, expected_tabs)

            # test removing with changed = False
            for tab_setup in ['', 'x', 'x,y,z']:
                course = self.get_course_with_tabs(tab_setup)
                expected_tabs = copy.copy(course.tabs)
                changed, actual_tabs = utils.remove_extra_panel_tab(tab_type, course)
                self.assertFalse(changed)
                self.assertEqual(actual_tabs, expected_tabs)


class GenerateCourseSecretTestCase(TestCase):
    def test_with_different_courses(self):
        """
        Different courses should have different secrets, even if
        they're created at the exact same time.
        """
        course_ids = ('edX/toy/2012_Fall', 'edx/full/6.002_Spring_2012')
        time.gmtime = mock.Mock(return_value=time.gmtime())
        s1, s2 = (utils.generate_secret_for_course(c_id) for c_id in course_ids)
        self.assertNotEqual(s1, s2)

