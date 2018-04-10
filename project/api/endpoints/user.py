from flask import Blueprint
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import (
    User,
    Education,
    ProjectResponse,
    WorkExperience,
    Tag
)
from project.api.schemas import (
    UserSchema,
    EducationSchema,
    ProjectResponseSchema,
    WorkExperienceSchema,
    TagSchema
)
from project.api.common.decorators import login_required, admin_required
from project.api.common.utils import make_response, set_tags


bp_user = Blueprint('user', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)


user_args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'name': fields.String(),
    'group_id': fields.Integer(allow_none=True),
    'role_id': fields.Integer(allow_none=True)
}


@bp_user.route('/<id>', methods=['GET'])
@login_required
@use_args(user_args)
def get_user_detail(args, id):
    user = User.query.get(id)
    if not user:
        return make_response(
            status_code=404,
            status='failure',
            message='No user found with that id')
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=user_schema.dump(user).data)


@bp_user.route('/', methods=['GET'])
@login_required
def get_user_list():
    users = User.query.all()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=users_schema.dump(users).data)


@bp_user.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_user(args, id):
    user = User.query.get(id)
    user.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated user',
        data=user_schema.dump(user).data)


@bp_user.route('/<id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_user(id):
    user = User.query.get(id)
    user.verified = True
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully verified user',
        data=user_schema.dump(user).data)


@bp_user.route('/<id>/education', methods=['GET'])
@login_required
def get_education_list(id):
    educations = Education.query.filter_by(user_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=EducationSchema(many=True).dump(educations).data)


@bp_user.route('/<id>/project_response', methods=['GET'])
@login_required
def get_project_response_list(id):
    project_responses = ProjectResponse.query.filter_by(user_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=ProjectResponseSchema(many=True).dump(project_responses).data)


@bp_user.route('/<id>/workexperience', methods=['GET'])
@login_required
def get_work_experience_list(id):
    work_experience = WorkExperience.query.filter_by(user_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=WorkExperienceSchema(many=True).dump(work_experience).data)


@bp_user.route('/<id>/tag', methods=['GET'])
@login_required
def get_tag_list(id):
    tags = Tag.query.filter_by(user_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=TagSchema(many=True).dump(tags).data)


tags_arg = {
    'tags': fields.List(
        fields.Nested(
            {
                'id': fields.Integer(),
                'title': fields.String(required=True)
            }
        )
    )
}


@bp_user.route('/<id>/tag', methods=['POST'])
@login_required
@use_args(tags_arg)
def set_user_tags(args, id):
    user = User.query.get(id)
    if not set_tags(
            session=db.session,
            parent=user,
            args=args,
            relation='user_id'):
        return make_response(
                status_code=404,
                status='failure',
                message='One or more tags could not be found'
            )

    tags = Tag.query.filter_by(user_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=TagSchema(many=True).dump(tags).data)
