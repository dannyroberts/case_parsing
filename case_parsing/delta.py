from .exceptions import CreateCaseError, CaseIdError, CloseCaseError
from jsonobject import (
    DictProperty,
    StringProperty,
    BooleanProperty,
)

from .jsonobject_extensions import (
    Base64Property,
    ISO8601Property,
    StrictJsonObject,
)


class IndexItem(StrictJsonObject):
    case_type = StringProperty()
    relationship = StringProperty(default="child",
                                  choices=['child', 'extension'])
    case_id = StringProperty()


class AttachmentItem(StrictJsonObject):
    src = StringProperty()
    src_type = StringProperty(choices=['local', 'remote', 'inline'],
                              required=True)
    name = StringProperty()
    data = Base64Property()


class CaseDelta(StrictJsonObject):
    case_id = StringProperty(required=True)
    date_modified = ISO8601Property(required=True)
    create = BooleanProperty(required=True)
    close = BooleanProperty(required=True)

    # updatable properties
    SPECIAL_PROPERTIES = ('case_type', 'case_name', 'date_opened', 'owner_id')
    case_type = StringProperty()
    case_name = StringProperty()
    date_opened = ISO8601Property()
    owner_id = StringProperty()

    update = DictProperty(basestring)
    index = DictProperty(IndexItem)
    # todo: need to deal with attachments in a way
    # todo: that includes access to the context in the case of from="local"
    attachment = DictProperty(AttachmentItem)

    def __iadd__(self, other):
        assert isinstance(other, CaseDelta)
        if other.case_id != self.case_id:
            raise CaseIdError()
        if other.create:
            raise CreateCaseError()
        if self.close:
            raise CloseCaseError()

        self.date_modified = other.date_modified
        self.close = other.close

        # updatable properties
        for attr in self.SPECIAL_PROPERTIES:
            if getattr(other, attr) is not None:
                setattr(self, attr, getattr(other, attr))

        self.update.update(other.update)
        self.index.update(other.index)
        self.attachment.update(other.attachment)
        return self

    def __add__(self, other):
        result = self.__class__.wrap(self.to_json())
        result += other
        return result
