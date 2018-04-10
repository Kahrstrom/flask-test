from flask import Blueprint
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Customer, Project, Location
from project.api.schemas import CustomerSchema, ProjectSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response


bp_customer = Blueprint('customer', __name__)

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

args = {
    'id': fields.Integer(required=True, customer='view_args')
}

save_args = {
    'name': fields.String(50, required=True),
    'customer_number': fields.String(50),
    'registration_number': fields.String(50),
    'location_id': fields.Integer()
}


@bp_customer.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_customer_detail(args, id):
    customer = Customer.query.get(id)
    if not customer:
        return make_response(
            status_code=404,
            status='failure',
            message='No work experience found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=customer_schema.dump(customer).data)


@bp_customer.route('/', methods=['GET'])
@login_required
def fetch_customer_list():
    customers = Customer.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=customers_schema.dump(customers).data)


@bp_customer.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_customer(args):
    location_id = args.get('location_id', None)
    location = None
    if location_id:
        location = Location.query.get(location_id)
        if not location:
            return make_response(
                status_code=400,
                status='failure',
                message='No location found with that id')

    customer = Customer(**args)
    if location:
        location.customers.append(customer)
    db.session.add(customer)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=customer_schema.dump(customer).data)


@bp_customer.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_customer(args, id):
    location_id = args.get('location_id', None)
    location = None
    if location_id:
        location = Location.query.get(location_id)
        if not location:
            return make_response(
                status_code=400,
                status='failure',
                message='No location found with that id')

    customer = Customer.query.get(id)
    customer.update(**args)
    if location:
        location.customers.append(customer)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated work experience',
        data=customer_schema.dump(customer).data)


@bp_customer.route('/<id>', methods=['DELETE'])
@login_required
def delete_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return make_response(
            status_code=404,
            status='failure',
            message='No customer found with that id')

    db.session.delete(customer)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully deleted eduation'
    )


@bp_customer.route('/<id>/project', methods=['GET'])
@login_required
def get_project_list(id):
    projects = Project.query.filter_by(customer_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=ProjectSchema(many=True).dump(projects).data)
