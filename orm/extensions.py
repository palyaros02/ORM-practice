from sqlalchemy.orm.exc import DetachedInstanceError

class Extension:
    def _repr(self, **fields) -> str:
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"

    def set_id_or_link(self, value, Class):
        attr = Class.__name__.lower()
        if isinstance(value, int):
            attr = f'{attr}_id'
        self.__setattr__(attr, value)
