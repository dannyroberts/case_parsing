from .exceptions import CreateCaseError, CaseIdError, CloseCaseError
from jsonobject import (
    DictProperty,
    JsonObject,
    ObjectProperty,
    StringProperty,
    BooleanProperty)

from .const import CASEXML_XMLNS
from .jsonobject_extensions import Base64Property, ISO8601Property


class StrictJsonObject(JsonObject):
    _allow_dynamic_properties = False
    _string_conversions = ()


class CreateBlock(StrictJsonObject):
    """
    <create>
        <case_type/> <!-- Exactly One: The ID for the type of case represented -->
        <owner_id/>  <!-- At Most One: The GUID of the current owner of this case -->
        <case_name/> <!-- Exactly One: A semantically meaningless but human readable name associated with the case -->
    </create>

    """

    case_type = StringProperty(required=True)
    owner_id = StringProperty()
    case_name = StringProperty(required=True)


class UpdateBlock(StrictJsonObject):
    """
    <update>
        <case_type/>   <!-- At Most One: Modifies the Case Type for the case -->
        <case_name/>   <!-- At Most One: A semantically meaningless but human  readable name associated with the case -->
        <date_opened/> <!-- At Most One: Modifies the Date the case was opened -->
        <owner_id/>    <!-- At Most One: Modifies the owner of this case -->
        <*/>           <!-- An Arbitrary Number: Creates or mutates a value  identified by the key provided -->
    </update>

    """

    _allow_dynamic_properties = True

    case_type = StringProperty(exclude_if_none=True)
    case_name = StringProperty(exclude_if_none=True)
    # why is this even a thing you'd want to modify?
    date_opened = ISO8601Property(exclude_if_none=True)
    owner_id = StringProperty(exclude_if_none=True)


class IndexItem(StrictJsonObject):
    """
    <index>
         <* case_type="" relationship="" /> <!-- At least one: A named element who's value is a GUID referring to another element -->
                                            <!-- @case_type: Exactly one: The case type of the indexed element -->
                                            <!-- @relationship[since 2.12]: At most one: Defines how this case and the parent case affect each other's "liveness" when syncing. One of:
                                                 "child" (default) - Denotes that this is a fully fledged case that depends on the indexed case. A child case will force the presence of a indexed case.
                                                 "extension"       - Denotes that this child extends the indexed case to provide additional data. An extension case will be removed from the user's scope if the indexed case is removed.
                                                  -->
    </index>

    """

    case_type = StringProperty(name='@case_type')
    relationship = StringProperty(name='@relationship', default="child",
                                  choices=['child', 'extension'])
    case_id = StringProperty(name='#text')


class AttachmentItem(StrictJsonObject):
    """
    <attachment>
            <* src="" from="" name=""/> <!-- At least one: A named element referring to an attachment. There are four valid states for this element.
                                    1) Named, no attributes, empty - This will remove the attachment.
                                    2) from="local". src must contain a uri which can be retrieved from the local form or environment. This attachment should be processed fully before the case transaction is committed.
                                    3) from="remote". src contains a uri. The URI should be globally accessible to the current user. This attachment can be processed asynchronously and does not need to be available before committing the transaction.
                                    4) from="inline". element must contain inline data (base64 encoded). @name must exist to provide a filetype. -->
                                    <!-- @src  - At most one: a reference to the location of this attachment. Either in the local environment or submission, or a remote location. -->
                                    <!-- @from - At most one: one of [local, remote, inline] specifying  whether this attachment is already present in the local environment, whether it must be retrieved asynchronously, or whether it is included in the attached element. -->
                                    <!-- @name - At most one: A specific name for this attachment. Mandatory if the attachment is attached as inline data. -->
    </attachment>

    """
    src = StringProperty(name='@src')
    src_type = StringProperty(name='@from',
                              choices=['local', 'remote', 'inline'],
                              required=True)
    name = StringProperty(name='@name')
    data = Base64Property(name='#text')


class CaseBlock(StrictJsonObject):
    """
    <case xmlns="http://commcarehq.org/case/transaction/v2" case_id="" user_id="" date_modified="" >
       <!-- user_id - At Most One: the GUID of the user responsible for this transaction -->
       <!-- case_id - Exactly One: The id of the abstract case to be modified (even in the case of creation) -->
       <!-- date_modified - Exactly One: The date and time of this operation -->
       <create/>         <!-- At Most One: Create action -->
       <update/>         <!-- At Most One: Updates data for the case -->
       <index/>          <!-- At Most One: Contains a set of referenced GUID's to other cases -->
       <attachment/>     <!-- (Since 2.5) At Most One: Contains pointers to binary attachments to include with this case -->
       <close/>          <!-- At Most One: Closes the case -->
    </case>

    """

    xmlns = StringProperty(name='@xmlns', choices=[CASEXML_XMLNS],
                           required=True)
    case_id = StringProperty(name='@case_id', required=True)
    user_id = StringProperty(name='@user_id')
    date_modified = ISO8601Property(name='@date_modified', required=True)
    create = ObjectProperty(CreateBlock, default=None)
    # update has four semantically relevant properties:
    # case_type, case_name, date_opened, owner_id
    update = ObjectProperty(UpdateBlock)
    index = DictProperty(IndexItem)
    attachment = DictProperty(AttachmentItem)
    close_ = StringProperty(name='close', choices=[u''])

    def _get_close(self):
        assert self.close_ in ('', None)
        return self.close_ == ''

    def _set_close(self, close):
        assert isinstance(close, bool)
        self.close_ = '' if close else None

    close = property(_get_close, _set_close)


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

    @classmethod
    def from_case_block(cls, case_block):
        assert isinstance(case_block, CaseBlock)
        b = case_block

        def extract_special(name):
            value = getattr(b.update, name, None)
            if value is not None:
                return value
            if b.create:
                value = getattr(b.create, name, None)
            return value

        self = cls(
            case_id=b.case_id,
            date_modified=b.date_modified,
            create=bool(b.create),
            close=b.close,

            case_type=extract_special('case_type'),
            owner_id=extract_special('owner_id'),
            case_name=extract_special('case_name'),
            date_opened=(getattr(b.update, 'date_opened', None)
                         or (b.date_modified if b.create else None)),
        )
        if b.update:
            self.update.update({
                attr: b.update[attr] for attr in b.update.keys()
                if attr not in self.SPECIAL_PROPERTIES
            })

        if b.index:
            self.index.update(b.index)

        if b.attachment:
            self.attachment.update(b.attachment)

        return self

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
