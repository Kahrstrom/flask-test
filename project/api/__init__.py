from .endpoints.user import bp_user
from .endpoints.auth import bp_auth
from .endpoints.education import bp_education
from .endpoints.work_experience import bp_work_experience
from .endpoints.project import bp_project
from .endpoints.group import bp_group
from .endpoints.role import bp_role
from .endpoints.tag import bp_tag
from .endpoints.location import bp_location
from .endpoints.customer import bp_customer
from .endpoints.project_response import bp_project_response
from .endpoints.contact_person import bp_contact_person
from .endpoints.activity import bp_activity
from .. import app


def register_blueprints():
    print('{}/{}'.format(app.config['APPLICATION_ROOT'], 'customer'))
    app.register_blueprint(
        bp_user,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'user'))
    app.register_blueprint(
        bp_auth,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'auth'))
    app.register_blueprint(
        bp_education,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'education'))
    app.register_blueprint(
        bp_work_experience,
        url_prefix='{}/{}'.format(
            app.config['APPLICATION_ROOT'], 'workexperience'))
    app.register_blueprint(
        bp_project,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'project'))
    app.register_blueprint(
        bp_group,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'group'))
    app.register_blueprint(
        bp_role,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'role'))
    app.register_blueprint(
        bp_tag,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'tag'))
    app.register_blueprint(
        bp_location,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'location'))
    app.register_blueprint(
        bp_customer,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'customer'))
    app.register_blueprint(
        bp_project_response,
        url_prefix='{}/{}'.format(
            app.config['APPLICATION_ROOT'], 'project_response'))
    app.register_blueprint(
        bp_contact_person,
        url_prefix='{}/{}'.format(
            app.config['APPLICATION_ROOT'], 'contact_person'))
    app.register_blueprint(
        bp_activity,
        url_prefix='{}/{}'.format(
            app.config['APPLICATION_ROOT'], 'activity'))
