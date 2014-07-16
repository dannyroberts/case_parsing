import datetime

import unittest2

from case_parsing.exceptions import CaseParsingException
import xml2json
from case_parsing import parse_casexml_json, CASEXML_XMLNS


CASE_XML_1 = """
<case xmlns="http://commcarehq.org/case/transaction/v2" case_id="3F2504E04F8911D39A0C0305E82C3301" date_modified="2014-01-15T13:12:33.139-05" user_id="9R3504E04F8911D39A0C0305E82C3301">
    <create>
        <case_type>houshold_rollout_ONICAF</case_type>
        <case_name>Smith</case_name>
        <owner_id>9R3504E04F8911D39A0C0305E82C3301</owner_id>
    </create>
    <update>
        <household_id>24/F23/3</household_id>
        <primary_contact_name>Tom Smith</primary_contact_name>
        <visit_number>1</visit_number>
    </update>
 </case>
"""

CASE_XML_2 = """
<case xmlns="http://commcarehq.org/case/transaction/v2" case_id="3F2504E04F8911D39A0C0305E82C3301" date_modified="2014-01-15T13:12:33.139-05" user_id="9R3504E04F8911D39A0C0305E82C3301">
    <update>
        <visit_number>2</visit_number>
        <my_date>2014-01-15T13:12:33.139-05</my_date>
    </update>
</case>
"""

CASE_XML_3 = """
<case xmlns="http://commcarehq.org/case/transaction/v2" case_id="3F2504E04F8911D39A0C0305E82C3301" user_id="9R3504E04F8911D39A0C0305E82C3301" date_modified="2014-01-15T13:12:33.139-05">
    <close/>
</case>
"""

NO_BODY = """
<case xmlns="http://commcarehq.org/case/transaction/v2" case_id="3F2504E04F8911D39A0C0305E82C3301" user_id="9R3504E04F8911D39A0C0305E82C3301" date_modified="2014-01-15T13:12:33.139-05"/>
"""

NO_XMLNS = """
<case case_id="3F2504E04F8911D39A0C0305E82C3301" user_id="9R3504E04F8911D39A0C0305E82C3301" date_modified="2014-01-15T13:12:33.139-05"/>
"""

NO_CASE_ID = """
<case xmlns="http://commcarehq.org/case/transaction/v2" user_id="9R3504E04F8911D39A0C0305E82C3301" date_modified="2014-01-15T13:12:33.139-05"/>
"""

EXTRA_ATTRIBUTE = """
<case foo="bar" xmlns="http://commcarehq.org/case/transaction/v2" case_id="3F2504E04F8911D39A0C0305E82C3301" user_id="9R3504E04F8911D39A0C0305E82C3301" date_modified="2014-01-15T13:12:33.139-05"/>
"""

SUBCASE = """
<case xmlns="http://commcarehq.org/case/transaction/v2" case_id="SADF2343223I4IU43A0C0305E82C3301" date_modified="2014-01-15T13:12:33.139-05" user_id="9R3504E04F8911D39A0C0305E82C3301">
    <create>
        <case_type>houshold_ONICAF_referral</case_type>
        <case_name>illness</case_name>
    </create>
    <update>
        <followup_date>11/17/09</followup_date>
    </update>
    <index>
        <household_case case_type="houshold_rollout_ONICAF">3F2504E04F8911D39A0C0305E82C3301</household_case>
    </index>
</case>
"""

ATTACHMENT = """
<case xmlns="http://commcarehq.org/case/transaction/v2" case_id="83789c75-9587-4df0-bf4a-8c81e6b64c0b" user_id="f8025f339922d82a9abb2a340b0a4ce3" date_modified="2013-03-07T15:00:37.026-05" xmlns:n0="http://commcarehq.org/case/transaction/v2">
    <attachment>
        <photo src="1362686433763.jpg" from="local"/>
    </attachment>
</case>
"""


class BasicParsing(unittest2.TestCase):

    def _get_case_block(self, xml):
        _, json = xml2json.xml2json(xml)
        return parse_casexml_json(json)

    def test_case_xml_1(self):
        block = self._get_case_block(CASE_XML_1)
        self.assertEqual(block.xmlns, CASEXML_XMLNS)
        self.assertEqual(block.case_id, '3F2504E04F8911D39A0C0305E82C3301')
        self.assertEqual(block.date_modified,
                         datetime.datetime(2014, 1, 15, 18, 12, 33, 139000))
        self.assertEqual(block.user_id, '9R3504E04F8911D39A0C0305E82C3301')
        self.assertEqual(block.create.case_type, 'houshold_rollout_ONICAF')
        self.assertEqual(block.create.case_name, 'Smith')
        self.assertEqual(block.create.owner_id,
                         '9R3504E04F8911D39A0C0305E82C3301')
        self.assertEqual(block.update.household_id, '24/F23/3')
        self.assertEqual(block.update.primary_contact_name, 'Tom Smith')
        self.assertEqual(block.update.visit_number, '1')
        self.assertFalse(block.close)
        self.assertEqual(len(block.index), 0)
        self.assertEqual(len(block.attachment), 0)

    def test_case_xml_2(self):
        block = self._get_case_block(CASE_XML_2)
        # no conversions!
        self.assertEqual(block.update.my_date, '2014-01-15T13:12:33.139-05')
        self.assertFalse(block.close)

    def test_case_xml_3(self):
        block = self._get_case_block(CASE_XML_3)
        self.assertTrue(block.close)

    def test_no_body(self):
        block = self._get_case_block(NO_BODY)
        self.assertFalse(block.close)

    def test_no_xmlns(self):
        with self.assertRaisesRegexp(CaseParsingException,
                                     r'Property @xmlns is required\.'):
            self._get_case_block(NO_XMLNS)

    def test_no_case_id(self):
        with self.assertRaisesRegexp(CaseParsingException,
                                     r'Property @case_id is required.'):
            self._get_case_block(NO_CASE_ID)

    def test_extra_attribute(self):
        with self.assertRaisesRegexp(
                CaseParsingException,
                r"can't set attribute corresponding to u'@foo' "
                r"on a <class '.*CaseBlock'> while wrapping {.*}"):
            self._get_case_block(EXTRA_ATTRIBUTE)

    def test_subcase(self):
        block = self._get_case_block(SUBCASE)
        self.assertEqual(len(block.index), 1)
        self.assertIn('household_case', block.index)
        item = block.index['household_case']
        self.assertEqual(item.case_type, 'houshold_rollout_ONICAF')
        self.assertEqual(item.case_id, '3F2504E04F8911D39A0C0305E82C3301')
        self.assertEqual(item.relationship, 'child')

    def test_attachment(self):
        block = self._get_case_block(ATTACHMENT)
        self.assertEqual(len(block.attachment), 1)
        self.assertIn('photo', block.attachment)
        item = block.attachment['photo']
        self.assertEqual(item.src, '1362686433763.jpg')
        self.assertEqual(item.src_type, 'local')
        self.assertEqual(item.data, None)


if __name__ == '__main__':
    unittest2.main()
