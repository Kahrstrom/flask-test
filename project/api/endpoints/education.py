from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Education, User, Tag
from project.api.schemas import EducationSchema, TagSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response, set_tags
from project.api.models.enums import EducationType

bp_education = Blueprint('education', __name__)

education_schema = EducationSchema()
educations_schema = EducationSchema(many=True)

args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'title': fields.String(50, required=True),
    'school': fields.String(50),
    'user_id': fields.Integer(50),
    'extent': fields.String(50),
    'description': fields.String(),
    'type': fields.String(validate=lambda t: EducationType.has_value(t)),
    'startdate': fields.DateTime(format='%Y-%m-%dT00:00%z'),
    'enddate': fields.DateTime(format='%Y-%m-%dT00:00%z')
}


@bp_education.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_education_detail(args, id):
    education = Education.query.get(id)
    if not education:
        return make_response(
            status_code=404,
            status='failure',
            message='No education found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=education_schema.dump(education).data)


@bp_education.route('/', methods=['GET'])
@login_required
def get_education_list():
    educations = Education.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=educations_schema.dump(educations).data)


@bp_education.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_education(args):
    user = User.query.get(args.get('user_id', g.user_id))
    if not user:
        return make_response(
            status_code=400,
            status='failure',
            message='No user found with that id')

    education = Education(**args)
    user.educations.append(education)
    db.session.commit()
    return make_response(
        status_code=201,
        status='success',
        message=None,
        data=education_schema.dump(education).data)


@bp_education.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_education(args, id):
    user = User.query.get(args.get('user_id', g.user_id))
    if not user:
        return make_response(
            status_code=400,
            status='failure',
            message='No user found with that id')

    education = Education.query.get(id)
    education.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated education',
        data=education_schema.dump(education).data)


@bp_education.route('/<id>', methods=['DELETE'])
@login_required
@use_args(args)
def delete_education(args, id):
    education = Education.query.get(id)
    if not education:
        return make_response(
            status_code=404,
            status='failure',
            message='No education found with that id')

    db.session.delete(education)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully deleted eduation'
    )


@bp_education.route('/<id>/tag', methods=['GET'])
@login_required
def get_tag_list(id):
    tags = Tag.query.filter_by(education_id=id).all()
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


@bp_education.route('/<id>/tag', methods=['POST'])
@login_required
@use_args(tags_arg)
def set_education_tags(args, id):
    education = Education.query.get(id)
    if not set_tags(
            session=db.session,
            parent=education,
            args=args,
            relation='education_id'):
        return make_response(
                status_code=404,
                status='failure',
                message='One or more tag could not be found'
            )

    tags = Tag.query.filter_by(education_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=TagSchema(many=True).dump(tags).data)
