from flask import Blueprint
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Location, Customer, Project
from project.api.schemas import LocationSchema, CustomerSchema, ProjectSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response


bp_location = Blueprint('location', __name__)

location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)

args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'description': fields.String(50),
    'latitude': fields.Float(),
    'longitude': fields.Float(),
    'street': fields.String(50, required=True),
    'zipcode': fields.String(10),
    'city': fields.String(50, required=True),
    'country': fields.String(50, required=True)
}


@bp_location.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_location_detail(args, id):
    location = Location.query.get(id)
    if not location:
        return make_response(
            status_code=404,
            status='failure',
            message='No work experience found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=location_schema.dump(location).data)


@bp_location.route('/', methods=['GET'])
@login_required
def fetch_location_list():
    locations = Location.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=locations_schema.dump(locations).data)


@bp_location.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_location(args):
    location = Location(**args)

    db.session.add(location)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=location_schema.dump(location).data)


@bp_location.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_location(args, id):
    location = Location.query.get(id)
    location.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated work experience',
        data=location_schema.dump(location).data)


@bp_location.route('/<id>', methods=['DELETE'])
@login_required
@use_args(args)
def delete_location(args, id):
    location = Location.query.get(id)
    if not location:
        return make_response(
            status_code=404,
            status='failure',
            message='No location found with that id')

    db.session.delete(location)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully deleted eduation'
    )


@bp_location.route('/<id>/customer', methods=['GET'])
@login_required
def get_customer_list(id):
    customers = Customer.query.filter_by(location_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=CustomerSchema(many=True).dump(customers).data)


@bp_location.route('/<id>/project', methods=['GET'])
@login_required
def get_project_list(id):
    projects = Project.query.filter_by(location_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=ProjectSchema(many=True).dump(projects).data)
