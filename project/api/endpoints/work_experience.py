from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import WorkExperience, User, Tag, Activity
from project.api.schemas import (
    WorkExperienceSchema,
    TagSchema,
    ActivitySchema
)
from project.api.common.decorators import login_required
from project.api.common.utils import make_response, set_tags


bp_work_experience = Blueprint('work_experience', __name__)

work_experience_schema = WorkExperienceSchema()
work_experiences_schema = WorkExperienceSchema(many=True)

args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'title': fields.String(50, required=True),
    'employer': fields.String(50, required=True),
    'user_id': fields.Integer(50),
    'description': fields.String(),
    'startdate': fields.DateTime(format='%Y-%m-%dT00:00%z'),
    'enddate': fields.DateTime(format='%Y-%m-%dT00:00%z'),
    'highlight': fields.Boolean()
}


@bp_work_experience.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_work_experience_detail(args, id):
    work_experience = WorkExperience.query.get(id)
    if not work_experience:
        return make_response(
            status_code=404,
            status='failure',
            message='No work experience found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=work_experience_schema.dump(work_experience).data)


@bp_work_experience.route('/', methods=['GET'])
@login_required
def fetch_work_experience_list():
    work_experiences = WorkExperience.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=work_experiences_schema.dump(work_experiences).data)


@bp_work_experience.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_work_experience(args):
    user = User.query.get(args.get('user_id', g.user_id))
    if not user:
        return make_response(
            status_code=400,
            status='failure',
            message='No user found with that id')

    work_experience = WorkExperience(**args)
    user.work_experience.append(work_experience)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=work_experience_schema.dump(work_experience).data)


@bp_work_experience.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_work_experience(args, id):
    user = User.query.get(args.get('user_id', g.user_id))
    if not user:
        return make_response(
            status_code=400,
            status='failure',
            message='No user found with that id')

    work_experience = WorkExperience.query.get(id)
    work_experience.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated work experience',
        data=work_experience_schema.dump(work_experience).data)


@bp_work_experience.route('/<id>', methods=['DELETE'])
@login_required
@use_args(args)
def delete_work_experience(args, id):
    work_experience = WorkExperience.query.get(id)
    if not work_experience:
        return make_response(
            status_code=404,
            status='failure',
            message='No work_experience found with that id')

    db.session.delete(work_experience)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully deleted eduation'
    )


@bp_work_experience.route('/<id>/tag', methods=['GET'])
@login_required
def get_tag_list(id):
    tags = Tag.query.filter_by(work_experience_id=id).all()
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


@bp_work_experience.route('/<id>/tag', methods=['POST'])
@login_required
@use_args(tags_arg)
def set_work_experience_tags(args, id):
    work_experience = WorkExperience.query.get(id)
    if not set_tags(
            session=db.session,
            parent=work_experience,
            args=args,
            relation='work_experience_id'):
        return make_response(
                status_code=404,
                status='failure',
                message='One or more tags could not be found'
            )

    tags = Tag.query.filter_by(work_experience_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=TagSchema(many=True).dump(tags).data)


@bp_work_experience.route('/<id>/activity', methods=['GET'])
@login_required
def get_user_activity_list(id):
    activities = Activity.query.filter_by(work_experience_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=ActivitySchema(many=True).dump(activities).data)
