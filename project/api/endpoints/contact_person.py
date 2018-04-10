from flask import Blueprint
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import ContactPerson, Customer
from project.api.schemas import ContactPersonSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response


bp_contact_person = Blueprint('contact_person', __name__)

contact_person_schema = ContactPersonSchema()
contact_persons_schema = ContactPersonSchema(many=True)

args = {
    'id': fields.Integer(required=True, contact_person='view_args')
}

save_args = {
    'firstname': fields.String(50, required=True),
    'lastname': fields.String(50, required=True),
    'title': fields.String(50),
    'customer_id': fields.Integer(required=True)
}


@bp_contact_person.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_contact_person_detail(args, id):
    contact_person = ContactPerson.query.get(id)
    if not contact_person:
        return make_response(
            status_code=404,
            status='failure',
            message='No contact person found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=contact_person_schema.dump(contact_person).data)


@bp_contact_person.route('/', methods=['GET'])
@login_required
def fetch_contact_person_list():
    contact_persons = ContactPerson.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=contact_persons_schema.dump(contact_persons).data)


@bp_contact_person.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_contact_person(args):
    customer = Customer.query.get(args['customer_id'])
    if not customer:
        return make_response(
            status_code=400,
            status='failure',
            message='No customer found with that id')

    contact_person = ContactPerson(**args)
    db.session.add(contact_person)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=contact_person_schema.dump(contact_person).data)


@bp_contact_person.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_contact_person(args, id):
    customer = Customer.query.get(args['customer_id'])
    if not customer:
        return make_response(
            status_code=400,
            status='failure',
            message='No customer found with that id')
    contact_person = ContactPerson.query.get(id)
    contact_person.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated work experience',
        data=contact_person_schema.dump(contact_person).data)


@bp_contact_person.route('/<id>', methods=['DELETE'])
@login_required
def delete_contact_person(id):
    contact_person = ContactPerson.query.get(id)
    if not contact_person:
        return make_response(
            status_code=404,
            status='failure',
            message='No contact_person found with that id')

    db.session.delete(contact_person)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully deleted contact person'
    )
