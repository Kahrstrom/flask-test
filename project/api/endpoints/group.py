from flask import Blueprint
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Group
from project.api.schemas import GroupSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response


bp_group = Blueprint('group', __name__)

group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)

args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'name': fields.String(50, required=True),
    'main_group_id': fields.Integer(allow_none=True)
}


@bp_group.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_group_detail(args, id):
    group = Group.query.get(id)
    if not group:
        return make_response(
            status_code=404,
            status='failure',
            message='No work experience found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=group_schema.dump(group).data)


@bp_group.route('/', methods=['GET'])
@login_required
def fetch_group_list():
    groups = Group.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=groups_schema.dump(groups).data)


@bp_group.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_group(args):
    main_group_id = args.get('main_group_id', None)

    group = Group(**args)

    if main_group_id:
        main_group = Group.query.get(main_group_id)
        main_group.subgroups.append(group)
    else:
        db.session.add(group)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=group_schema.dump(group).data)


@bp_group.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_group(args, id):
    group = Group.query.get(id)
    group.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated work experience',
        data=group_schema.dump(group).data)


@bp_group.route('/<id>', methods=['DELETE'])
@login_required
@use_args(args)
def delete_group(args, id):
    group = Group.query.get(id)
    if not group:
        return make_response(
            status_code=404,
            status='failure',
            message='No group found with that id')

    db.session.delete(group)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully deleted eduation'
    )
