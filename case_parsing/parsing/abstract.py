from ..delta import CaseDelta, AttachmentItem, IndexItem


class CaseBlock(object):
    def to_case_delta(self):
        def extract_special(name):
            value = getattr(self.update, name, None)
            if value is not None:
                return value
            if self.create:
                value = getattr(self.create, name, None)
            return value

        delta = CaseDelta(
            case_id=self.case_id,
            date_modified=self.date_modified,
            create=bool(self.create),
            close=self.close,

            case_type=extract_special('case_type'),
            owner_id=extract_special('owner_id'),
            case_name=extract_special('case_name'),
            date_opened=(getattr(self.update, 'date_opened', None)
                         or (self.date_modified if self.create else None)),
        )
        if self.update:
            delta.update.update({
                attr: self.update[attr] for attr in self.update.keys()
                if attr not in delta.SPECIAL_PROPERTIES
            })

        if self.index:
            delta.index.update({
                attr: IndexItem(
                    case_type=item.case_type,
                    relationship=item.relationship,
                    case_id=item.case_id,
                )
                for attr, item in self.index.items()
            })

        if self.attachment:
            delta.attachment.update({
                attr: AttachmentItem(
                    src=item.src,
                    src_type=item.src_type,
                    name=item.name,
                    data=item.data,
                )
                for attr, item in self.attachment.items()
            })

        return delta
