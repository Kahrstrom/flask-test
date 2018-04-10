import enum


class EnumBase(enum.Enum):
    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class UserType(EnumBase):
    admin = 1
    super_user = 2
    user = 3


class EducationType(EnumBase):
    education = 'EDUCATION'
    course = 'COURSE'
    internal_course = 'INTERNAL_COURSE'


class ResponseType(EnumBase):
    empty = 'EMPTY'
    interested = 'INTERESTED'
    proposed = 'PROPOSED'
    accepted = 'ACCEPTED'
    rejected = 'REJECTED'
