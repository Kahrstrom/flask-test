from marshmallow import fields

from ..models import (
    User,
    Education,
    WorkExperience,
    Role,
    Group,
    Project,
    ProjectResponse,
    Customer,
    Location,
    ContactPerson,
    Tag
)
from ..models.enums import EducationType, ResponseType
from project import ma
from .custom_fields import RelatedTo, RelatedFromQuery, RelatedFromList


class BaseSchema(ma.ModelSchema):
    id = fields.Integer(dump_to='_id')
    created = fields.DateTime(dump_only=True, dump_to='_created')
    timestamp = fields.DateTime(dump_only=True, dump_to='_timestamp')
    updated_by = RelatedTo(
        attribute='updated_by', dump_only=True, dump_to='_updated_by')
    created_by = RelatedTo(
        attribute='created_by', dump_only=True, dump_to='_created_by')
    _descriptive = fields.String(dump_only=True)


class ExtendedSchema(BaseSchema):
    user = RelatedTo(attribute='user')
    tags = fields.List(fields.Nested(
        'TagSchema', only=['title', 'id'], dump_only=True
    ))


class GroupSchema(ExtendedSchema):
    class Meta:
        model = Group

    users = ma.List(ma.HyperlinkRelated(
        'user.get_user_detail', external=True), dump_only=True)
    main_group = RelatedTo(attribute='main_group')
    subgroups = ma.List(ma.HyperlinkRelated(
        'group.get_group_detail', external=True), dump_only=True)
    _all_users = RelatedFromQuery(
        endpoint='user.get_user_detail', attribute='all_users_id')


class RoleSchema(ExtendedSchema):
    class Meta:
        model = Role
    _all_users = RelatedFromQuery(
        endpoint='user.get_user_detail', attribute='all_users_id')
    users = ma.List(ma.HyperlinkRelated(
        'user.get_user_detail'), dump_only=True)
    main_role = RelatedTo(attribute='main_role')
    subroles = ma.List(ma.HyperlinkRelated(
        'role.get_role_detail', external=True), dump_only=True)


class UserSchema(BaseSchema):
    class Meta:
        model = User
        exclude = ['password', 'updated_by', 'created_by']

    updated_by_user_id = fields.Integer(dump_to='updated_by', dump_only=True)
    created_by_user_id = fields.Integer(dump_to='created_by', dump_only=True)

    educations = RelatedFromList(
        endpoint_list='user.get_education_list',
        endpoint_details='education.get_education_detail',
        attribute='educations',
        dump_only=True)
    work_experience = RelatedFromList(
        endpoint_list='user.get_work_experience_list',
        endpoint_details='work_experience.get_work_experience_detail',
        attribute='work_experience',
        dump_only=True)
    projectresponses = RelatedFromList(
        endpoint_list='user.get_project_response_list',
        endpoint_details='project_response.get_project_response_detail',
        attribute='projectresponses',
        dump_only=True)

    group = fields.Nested(
        GroupSchema, only=['_descriptive', 'id'], dump_only=True)
    role = fields.Nested(
        RoleSchema, only=['_descriptive', 'id'], dump_only=True)

    tags = fields.List(fields.Nested(
        'TagSchema', only=['title', 'id'], dump_only=True
    ))


class EducationSchema(ExtendedSchema):
    class Meta:
        model = Education
    _type = fields.Method('get_type', dump_to='type', dump_only=True)

    @classmethod
    def get_type(cls, obj):
        return {
            'value': obj.type.value,
            'choices': [EducationType[item].value
                        for item in EducationType.__members__]}


class WorkExperienceSchema(ExtendedSchema):
    class Meta:
        model = WorkExperience


class ProjectSchema(BaseSchema):
    class Meta:
        model = Project

    customer = RelatedTo(attribute='customer')
    location = RelatedTo(attribute='location')
    projectresponses = RelatedFromList(
        endpoint_list='project.get_project_response_list',
        endpoint_details='project_response.get_project_response_detail',
        attribute='projectresponses',
        dump_only=True)


class ProjectResponseSchema(BaseSchema):
    class Meta:
        model = ProjectResponse

    user = RelatedTo(attribute='user')
    project = RelatedTo(attribute='project')
    _type = fields.Method('get_type', dump_to='type', dump_only=True)

    @classmethod
    def get_type(cls, obj):
        return {
            'value': obj.type.value,
            'choices': [ResponseType[item].value
                        for item in ResponseType.__members__]}


class LocationSchema(BaseSchema):
    class Meta:
        model = Location

    customer = RelatedTo(attribute='customer')
    project = RelatedTo(attribute='project')
    longitude = fields.Decimal(as_string=True)
    latitude = fields.Decimal(as_string=True)
    customers = RelatedFromList(
        endpoint_list='location.get_customer_list',
        endpoint_details='customer.get_customer_detail',
        attribute='customers',
        dump_only=True)
    projects = RelatedFromList(
        endpoint_list='location.get_project_list',
        endpoint_details='project.get_project_detail',
        attribute='projects',
        dump_only=True)


class ContactPersonSchema(BaseSchema):
    class Meta:
        model = ContactPerson

    customer = RelatedTo(attribute='customer')


class CustomerSchema(BaseSchema):
    class Meta:
        model = Customer

    location = RelatedTo(attribute='location')
    projects = RelatedFromList(
        endpoint_list='customer.get_project_list',
        endpoint_details='project.get_project_detail',
        attribute='projects',
        dump_only=True)


class TagSchema(ma.ModelSchema):
    class Meta:
        model = Tag
    id = fields.Integer(dump_to='_id')
