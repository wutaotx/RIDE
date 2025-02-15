#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import unittest
from utest.resources import datafilereader
from nose.tools import assert_equal
from robotide.usages.commands import FindResourceUsages
from robotide.publish import PUBLISHER


class ResourceUsageTests(unittest.TestCase):

    # NOTE! The data is shared among tests
    # This is for performance reasons but be warned when you add tests!
    @classmethod
    def setUpClass(cls):
        PUBLISHER.unsubscribe_all()
        cls.ctrl = datafilereader.construct_project(datafilereader.SIMPLE_TEST_SUITE_PATH)
        cls.ts1 = datafilereader.get_ctrl_by_name('TestSuite1', cls.ctrl.datafiles)
        cls.ts2 = datafilereader.get_ctrl_by_name('TestSuite2', cls.ctrl.datafiles)
        cls.resu = datafilereader.get_ctrl_by_name(datafilereader.SIMPLE_TEST_SUITE_RESOURCE_NAME, cls.ctrl.datafiles)

    @classmethod
    def tearDownClass(cls):
        cls.ctrl.close()

    def test_resource_import_knows_imported_resource_controller(self):
        assert_equal(self.resu, self.ts1.imports[0].get_imported_controller())
        assert_equal(self.resu, self.ts2.imports[0].get_imported_controller())

    def test_resource_usages_finding(self):
        usages = list(self.resu.execute(FindResourceUsages()))
        self._verify_length(2, usages)
        self._verify_that_contains(self.ts1, usages)
        self._verify_that_contains(self.ts2, usages)

    def _verify_length(self, expected, usages):
        assert_equal(len(usages), expected)

    def _verify_that_contains(self, item, usages):
        for u in usages:
            if u.item == item.imports:
                if item.display_name != u.name:
                    raise AssertionError('Name "%s" was not expected "%s"!' % (u.name, item.display_name))
                return
        raise AssertionError('Item %r not in usages %r!' % (item, usages))

    def test_import_in_resource_file(self):
        inner_resu = self.resu.imports[0].get_imported_controller()
        usages = list(inner_resu.execute(FindResourceUsages()))
        self._verify_length(1, usages)
        self._verify_that_contains(self.resu, usages)

    def test_none_existing_import(self):
        imp = self.ts1.imports.add_resource('this_does_not_exists.robot')
        assert_equal(imp.get_imported_controller(), None)


if __name__ == '__main__':
    unittest.main()
