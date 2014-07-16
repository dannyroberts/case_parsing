from jsonobject.exceptions import BadValueError, WrappingAttributeError

from .models import CaseBlock, CaseDelta
from .exceptions import CaseParsingException
import xml2json


def parse_casexml_json(casexml_json):
    try:
        return CaseBlock(casexml_json)
    except (BadValueError, WrappingAttributeError) as e:
        print casexml_json
        raise CaseParsingException(unicode(e))


def parse_casexml_string(casexml_string):
    _, casexml_json = xml2json.xml2json(casexml_string)
    return parse_casexml_json(casexml_json)


def parse_casexml_etree(casexml_etree):
    _, casexml_json = xml2json.convert_xml_to_json(casexml_etree)
    return parse_casexml_json(casexml_json)


def parse_casexml(casexml):
    if isinstance(casexml, basestring):
        return parse_casexml_string(casexml)
    elif isinstance(casexml, xml2json.etree):
        return parse_casexml_etree(casexml)
    elif isinstance(casexml, dict):
        return parse_casexml_json(casexml)
    else:
        raise ValueError('casexml must be a string, etree, or dict')


def get_case_delta(casexml):
    if isinstance(casexml, CaseBlock):
        case_block = casexml
    else:
        case_block = parse_casexml(casexml)

    return CaseDelta.from_case_block(case_block)
