from flask import Blueprint
from sqlalchemy import func
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Tag
from project.api.schemas import TagSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response


bp_tag = Blueprint('tag', __name__)

tag_schema = TagSchema()
tags_schema = TagSchema(many=True)

args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'title': fields.String(50, required=True)
}


@bp_tag.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_tag_detail(args, id):
    tag = Tag.query.get(id)
    if not tag:
        return make_response(
            status_code=404,
            status='failure',
            message='No work experience found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=tag_schema.dump(tag).data)


@bp_tag.route('/', methods=['GET'])
@login_required
def fetch_tag_list():
    tags = Tag.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=tags_schema.dump(tags).data)


@bp_tag.route('/list')
def fetch_tag_list_suggestions():
    tags = Tag.query.with_entities(
        Tag.title, func.count(Tag.title)).group_by(Tag.title).all()

    return make_response(
        status_code=200,
        status='success',
        data=tags_schema.dump(tags).data)


@bp_tag.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_tag(args, id):
    tag = Tag.query.get(id)
    tag.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated work experience',
        data=tag_schema.dump(tag).data)


@bp_tag.route('/<id>', methods=['DELETE'])
@login_required
@use_args(args)
def delete_tag(args, id):
    tag = Tag.query.get(id)
    if not tag:
        return make_response(
            status_code=404,
            status='failure',
            message='No tag found with that id')

    db.session.delete(tag)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully deleted eduation'
    )
