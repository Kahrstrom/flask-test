from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import ProjectResponse, User, Project
from project.api.schemas import ProjectResponseSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response
from project.api.models.enums import ResponseType

bp_project_response = Blueprint('project_response', __name__)

project_response_schema = ProjectResponseSchema()
project_responses_schema = ProjectResponseSchema(many=True)

args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'user_id': fields.Integer(required=True),
    'project_id': fields.Integer(required=True),
    'price': fields.Integer(missing=0),
    'type': fields.String(validate=lambda t: ResponseType.has_value(t))
}


@bp_project_response.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_project_response_detail(args, id):
    project_response = ProjectResponse.query.get(id)
    if not project_response:
        return make_response(
            status_code=404,
            status='failure',
            message='No project_response found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=project_response_schema.dump(project_response).data)


@bp_project_response.route('/', methods=['GET'])
@login_required
def get_project_response_list():
    project_responses = ProjectResponse.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=project_responses_schema.dump(project_responses).data)


@bp_project_response.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_project_response(args):
    user = User.query.get(args.get('user_id', g.user_id))
    if not user:
        return make_response(
            status_code=400,
            status='failure',
            message='No user found with that id')

    project = Project.query.get(args['project_id'])
    if not project:
        return make_response(
            status_code=400,
            status='failure',
            message='No project found with that id')

    project_response = ProjectResponse(**args)
    user.projectresponses.append(project_response)
    project.projectresponses.append(project_response)
    db.session.commit()
    return make_response(
        status_code=201,
        status='success',
        message=None,
        data=project_response_schema.dump(project_response).data)


@bp_project_response.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_project_response(args, id):
    user = User.query.get(args.get('user_id', g.user_id))
    if not user:
        return make_response(
            status_code=400,
            status='failure',
            message='No user found with that id')

    project_response = ProjectResponse.query.get(id)

    project_response.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated project_response',
        data=project_response_schema.dump(project_response).data)


@bp_project_response.route('/<id>', methods=['DELETE'])
@login_required
@use_args(args)
def delete_project_response(args, id):
    project_response = ProjectResponse.query.get(id)
    if not project_response:
        return make_response(
            status_code=404,
            status='failure',
            message='No project_response found with that id')

    db.session.delete(project_response)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully deleted eduation'
    )
