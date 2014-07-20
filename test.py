import datetime

import unittest2

from case_parsing.exceptions import CaseParsingException
import xml2json
from case_parsing import parse_casexml_json, CASEXML_XMLNS, get_case_delta
from case_parsing.delta import CaseDelta


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

CASE_XML_1_DELTA = CaseDelta(
    case_id='3F2504E04F8911D39A0C0305E82C3301',
    create=True,
    date_modified=datetime.datetime(2014, 1, 15, 18, 12, 33, 139000),

    date_opened=datetime.datetime(2014, 1, 15, 18, 12, 33, 139000),
    case_type='houshold_rollout_ONICAF',
    case_name='Smith',
    owner_id='9R3504E04F8911D39A0C0305E82C3301',
    update={
        'household_id': '24/F23/3',
        'primary_contact_name': 'Tom Smith',
        'visit_number': '1',
    },
    close=False,
)

CASE_XML_2 = """
<case xmlns="http://commcarehq.org/case/transaction/v2" case_id="3F2504E04F8911D39A0C0305E82C3301" date_modified="2014-01-15T13:12:34.000-05" user_id="9R3504E04F8911D39A0C0305E82C3301">
    <update>
        <visit_number>2</visit_number>
        <my_date>2014-01-15T13:12:33.139-05</my_date>
    </update>
</case>
"""

CASE_XML_2_DELTA = CaseDelta(
    case_id='3F2504E04F8911D39A0C0305E82C3301',
    create=False,
    date_modified=datetime.datetime(2014, 1, 15, 18, 12, 34),

    date_opened=None,
    case_type=None,
    case_name=None,
    update={
        'my_date': '2014-01-15T13:12:33.139-05',
        'visit_number': '2',
    },
    close=False,
)

DELTA_1_PLUS_2 = CaseDelta(
    case_id='3F2504E04F8911D39A0C0305E82C3301',
    create=True,
    date_modified=datetime.datetime(2014, 1, 15, 18, 12, 34),

    date_opened=datetime.datetime(2014, 1, 15, 18, 12, 33, 139000),
    case_type='houshold_rollout_ONICAF',
    case_name='Smith',
    owner_id='9R3504E04F8911D39A0C0305E82C3301',
    update={
        'household_id': '24/F23/3',
        'primary_contact_name': 'Tom Smith',
        'visit_number': '2',
        'my_date': '2014-01-15T13:12:33.139-05',
    },
    close=False,
)


CASE_XML_3 = """
<case xmlns="http://commcarehq.org/case/transaction/v2" case_id="3F2504E04F8911D39A0C0305E82C3301" user_id="9R3504E04F8911D39A0C0305E82C3301" date_modified="2014-01-15T13:12:35-05">
    <close/>
</case>
"""

CASE_XML_3_DELTA = CaseDelta(
    case_id='3F2504E04F8911D39A0C0305E82C3301',
    create=False,
    date_modified=datetime.datetime(2014, 1, 15, 18, 12, 35),
    close=True,
)


DELTA_1_PLUS_2_PLUS_3 = CaseDelta(
    case_id='3F2504E04F8911D39A0C0305E82C3301',
    create=True,
    date_modified=datetime.datetime(2014, 1, 15, 18, 12, 35),

    date_opened=datetime.datetime(2014, 1, 15, 18, 12, 33, 139000),
    case_type='houshold_rollout_ONICAF',
    case_name='Smith',
    owner_id='9R3504E04F8911D39A0C0305E82C3301',
    update={
        'household_id': '24/F23/3',
        'primary_contact_name': 'Tom Smith',
        'visit_number': '2',
        'my_date': '2014-01-15T13:12:33.139-05',
    },
    close=True,
)

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
        self.assertEqual(block.update.to_json(), {
            'household_id': '24/F23/3',
            'primary_contact_name': 'Tom Smith',
            'visit_number': '1',
        })
        self.assertFalse(block.close)
        self.assertEqual(len(block.index), 0)
        self.assertEqual(len(block.attachment), 0)

    def test_case_xml_2(self):
        block = self._get_case_block(CASE_XML_2)
        # no conversions!
        self.assertEqual(block.update.to_json(), {
            'my_date': '2014-01-15T13:12:33.139-05',
            'visit_number': '2',
        })
        self.assertIsNone(block.create)
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

    def test_case_delta_1(self):
        block = self._get_case_block(CASE_XML_1)
        delta = block.to_case_delta()
        self.assertEqual(
            delta.to_json(),
            CASE_XML_1_DELTA.to_json(),
        )

    def test_case_delta_2(self):
        block = self._get_case_block(CASE_XML_2)
        delta = block.to_case_delta()
        self.assertDictEqual(
            delta.to_json(),
            CASE_XML_2_DELTA.to_json(),
        )

    def test_case_delta_3(self):
        block = self._get_case_block(CASE_XML_3)
        delta = block.to_case_delta()
        self.assertDictEqual(
            delta.to_json(),
            CASE_XML_3_DELTA.to_json(),
        )

    def test_case_delta_1_plus_2(self):
        block1 = self._get_case_block(CASE_XML_1)
        block2 = self._get_case_block(CASE_XML_2)
        delta1 = block1.to_case_delta()
        delta2 = block2.to_case_delta()
        self.assertDictEqual(
            (delta1 + delta2).to_json(),
            DELTA_1_PLUS_2.to_json(),
        )

    def test_case_delta_1_plus_2_plus_3(self):
        block1 = self._get_case_block(CASE_XML_1)
        block2 = self._get_case_block(CASE_XML_2)
        block3 = self._get_case_block(CASE_XML_3)
        delta1 = block1.to_case_delta()
        delta2 = block2.to_case_delta()
        delta3 = block3.to_case_delta()
        self.assertDictEqual(
            (delta1 + delta2 + delta3).to_json(),
            DELTA_1_PLUS_2_PLUS_3.to_json(),
        )
        self.assertDictEqual(
            (delta1 + (delta2 + delta3)).to_json(),
            DELTA_1_PLUS_2_PLUS_3.to_json(),
        )
        self.assertDictEqual(
            ((delta1 + delta2) + delta3).to_json(),
            DELTA_1_PLUS_2_PLUS_3.to_json(),
        )


class CaseDeltaTest(unittest2.TestCase):
    maxDiff = None

    def test_get_case_delta(self):
        self.assertDictEqual(
            get_case_delta("""
            <case xmlns="http://commcarehq.org/case/transaction/v2"
                  case_id="A" date_modified="2014-01-15T13:12:33.139-05"
                  user_id="X">
                <create>
                    <owner_id>X</owner_id>
                    <case_name>john</case_name>
                    <case_type>test</case_type>
                </create>
                <update>
                    <owner_id>Y</owner_id>
                    <age>7</age>
                    <date_opened>2013-01-01T12:00:00-05</date_opened>
                </update>
            </case>
            """).to_json(),
            CaseDelta(
                create=True,
                close=False,
                case_id='A',
                date_modified=datetime.datetime(2014, 1, 15, 18, 12, 33, 139000),
                date_opened=datetime.datetime(2013, 1, 1, 17, 0, 0),
                owner_id='Y',
                case_name="john",
                case_type='test',
                update={'age': '7'}
            ).to_json(),
        )


if __name__ == '__main__':
    unittest2.main()
