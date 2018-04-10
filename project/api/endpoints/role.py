from flask import Blueprint
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Role
from project.api.schemas import RoleSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response


bp_role = Blueprint('role', __name__)

role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)

args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'name': fields.String(50, required=True),
    'main_role_id': fields.Integer(allow_none=True)
}


@bp_role.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_role_detail(args, id):
    role = Role.query.get(id)
    if not role:
        return make_response(
            status_code=404,
            status='failure',
            message='No work experience found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=role_schema.dump(role).data)


@bp_role.route('/', methods=['GET'])
@login_required
def fetch_role_list():
    roles = Role.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=roles_schema.dump(roles).data)


@bp_role.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_role(args):
    main_role_id = args.get('main_role_id', None)

    role = Role(**args)

    if main_role_id:
        main_role = Role.query.get(main_role_id)
        main_role.subroles.append(role)
    else:
        db.session.add(role)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=role_schema.dump(role).data)


@bp_role.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_role(args, id):
    role = Role.query.get(id)
    role.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated work experience',
        data=role_schema.dump(role).data)


@bp_role.route('/<id>', methods=['DELETE'])
@login_required
@use_args(args)
def delete_role(args, id):
    role = Role.query.get(id)
    if not role:
        return make_response(
            status_code=404,
            status='failure',
            message='No role found with that id')

    db.session.delete(role)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully deleted eduation'
    )
