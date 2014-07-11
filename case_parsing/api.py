from jsonobject.exceptions import BadValueError, WrappingAttributeError

from .models import CaseBlock
from .exceptions import CaseParsingException
import xml2json


def parse_casexml_json(casexml_json):
    try:
        return CaseBlock(casexml_json)
    except (BadValueError, WrappingAttributeError) as e:
        raise CaseParsingException(unicode(e))


def parse_casexml_string(casexml_string):
    return parse_casexml_json(xml2json.xml2json(casexml_string))


def parse_casexml_etree(casexml_etree):
    return parse_casexml_json(xml2json.convert_xml_to_json(casexml_etree))


def parse_casexml(casexml):
    if isinstance(casexml, basestring):
        return parse_casexml_string(casexml)
    elif isinstance(casexml, xml2json.etree):
        return parse_casexml_etree(casexml)
    elif isinstance(casexml, dict):
        return parse_casexml_json(casexml)
    else:
        raise ValueError('casexml must be a string, etree, or dict')
