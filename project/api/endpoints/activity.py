from flask import Blueprint
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Activity, Customer, Project
from project.api.schemas import ActivitySchema, CustomerSchema, ProjectSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response


bp_activity = Blueprint('activity', __name__)

activity_schema = ActivitySchema()
activitys_schema = ActivitySchema(many=True)

args = {
    'id': fields.Integer(required=True, activity='view_args')
}

@bp_activity.route('/<id>', methods=['GET'])
@login_required
@use_args(args)
def get_activity_detail(args, id):
    activity = Activity.query.get(id)
    if not activity:
        return make_response(
            status_code=404,
            status='failure',
            message='No work experience found with that id')

    return make_response(
        status_code=200,
        status='success',
        data=activity_schema.dump(activity).data)


@bp_activity.route('/', methods=['GET'])
@login_required
def fetch_activity_list():
    activitys = Activity.query.all()
    return make_response(
        status_code=200,
        status='success',
        data=activitys_schema.dump(activitys).data)
