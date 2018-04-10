from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models.enums import ResponseType
from project.api.models import Project, User, Tag, ProjectResponse
from project.api.schemas import (
    ProjectSchema,
    TagSchema,
    ProjectResponseSchema
)
from project.api.common.decorators import login_required
from project.api.common.utils import make_response, set_tags


bp_project = Blueprint('project', __name__)

project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)

args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'title': fields.String(50, required=True),
    'customer': fields.String(50, required=True),
    'user_id': fields.Integer(50),
    'description': fields.String(),
    'startdate': fields.DateTime(format='%Y-%m-%dT00:00%z'),
    'enddate': fields.DateTime(format='%Y-%m-%dT00:00%z'),
    'highlight': fields.Boolean()
}


@bp_project.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_project_detail(args, id):
    project = Project.query.get(id)
    if not project:
        return make_response(
            status_code=404,
            status='failure',
            message='No work experience found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=project_schema.dump(project).data)


@bp_project.route('/', methods=['GET'])
@login_required
def fetch_project_list():
    projects = Project.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=projects_schema.dump(projects).data)


@bp_project.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_project(args):
    user = User.query.get(args.get('user_id', g.user_id))
    if not user:
        return make_response(
            status_code=400,
            status='failure',
            message='No user found with that id')

    project = Project(**args)
    user.project.append(project)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=project_schema.dump(project).data)


@bp_project.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_project(args, id):
    user = User.query.get(args.get('user_id', g.user_id))
    if not user:
        return make_response(
            status_code=400,
            status='failure',
            message='No user found with that id')

    project = Project.query.get(id)
    project.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated work experience',
        data=project_schema.dump(project).data)


@bp_project.route('/<id>', methods=['DELETE'])
@login_required
@use_args(args)
def delete_project(args, id):
    project = Project.query.get(id)
    if not project:
        return make_response(
            status_code=404,
            status='failure',
            message='No project found with that id')

    db.session.delete(project)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully deleted eduation'
    )


project_response_filter_args = {
    'type': fields.String(validate=lambda t: ResponseType.has_value(t)),
}


@bp_project.route('/<id>/project_response', methods=['GET'])
@login_required
@use_args(project_response_filter_args)
def get_project_response_list(id, args):
    project_responses = ProjectResponse.query.filter_by(project_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=ProjectResponseSchema(many=True).dump(project_responses).data)


@bp_project.route('/<id>/tag', methods=['GET'])
@login_required
def get_tag_list(id):
    tags = Tag.query.filter_by(project_id=id).all()
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


@bp_project.route('/<id>/tag', methods=['POST'])
@login_required
@use_args(tags_arg)
def set_project_tags(args, id):
    project = Project.query.get(id)
    if not set_tags(
            session=db.session,
            parent=project,
            args=args,
            relation='project_id'):
        return make_response(
                status_code=404,
                status='failure',
                message='One or more tags could not be found'
            )

    tags = Tag.query.filter_by(project_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=TagSchema(many=True).dump(tags).data)
