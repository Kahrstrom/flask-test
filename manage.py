import unittest
import coverage

from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/settings.py',
        'project/api/*/__init__.py'
    ]
)
COV.start()

from project import app, db, settings # noqa
from project.api.models import (
    User, Education, Group, Role, Tag, Project,
    Location, Customer, ProjectResponse, ContactPerson)  # noqa

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


def add_admin_account():
    admin = User(**{
        'email': settings.admin_email,
        'password': settings.admin_password,
        'name': 'Admin',
        'admin': True,
        'verified': True
    })
    db.session.add(admin)
    db.session.commit()


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()
    add_admin_account()
    # add_test_data()


@manager.command
def add_test_data():
    tag1 = Tag(**{
        'title': 'Programming'
    })
    tag2 = Tag(**{
        'title': 'Programming'
    })
    tag3 = Tag(**{
        'title': 'Social studies'
    })
    tag4 = Tag(**{
        'title': 'Creative'
    })
    tag5 = Tag(**{
        'title': 'Engineering',
        'user_id': 1
    })

    group = Group(**{
        'name': 'Copenhagen Office',
        'address': 'Købmagergade 67',
        'zipcode': '1150',
        'city': 'Copenhagen',
        'country': 'Denmark'
    })

    role = Role(**{
        'name': 'Application consultant'
    })

    user = User(**{
        'email': 'jonatan.tegen@gmail.com',
        'password': 'test',
        'name': 'Jonatan Tegen',
        'admin': False,
        'verified': False
    })
    education1 = Education(**{
        'title': 'Engineering Physics',
        'school': 'LTH',
        'extent': 'Master\'s degree',
        'description': 'Learned cool stuff!',
        'user_id': 1
    })
    education2 = Education(**{
        'title': 'Psychology',
        'school': 'Lund University',
        'type': 'COURSE',
        'extent': 'One semester',
        'description': ''
    })
    education3 = Education(**{
        'title': 'Math',
        'school': 'LTH',
        'type': 'COURSE',
        'extent': '30HP',
        'description': 'Math man..!'
    })
    project = Project(**{
        'title': 'Some cool project',
        'description': 'DO STUFF',
        'startdate': '2018-01-01T00:00+01:00',
        'enddate': '2018-08-01T00:00+01:00',
        'hours': 100
    })
    location1 = Location(**{
        'description': 'HQ',
        'latitude': 55.6831585,
        'longitude': 13.1756237,
        'street': 'Sankt Lars väg 46',
        'zipcode': '222 70',
        'city': 'Lund',
        'country': 'Sweden'
    })
    customer = Customer(**{
        'name': 'Lime Technologies AB',
        'customer_number': '123456',
        'registration_number': '',
        'location_id': 1
    })
    contact_person = ContactPerson(**{
        'firstname': 'Jonatan',
        'lastname': 'Tegen',
        'title': 'Consultant manager'
    })
    project_response = ProjectResponse(**{
        'type': 'INTERESTED'
    })
    location1.customers.append(customer)
    location1.projects.append(project)
    customer.projects.append(project)
    customer.contactpersons.append(contact_person)
    education1.tags.append(tag1)
    education2.tags.append(tag3)
    user.tags.append(tag2)
    user.tags.append(tag4)
    user.educations.append(education2)
    user.educations.append(education3)
    user.projectresponses.append(project_response)
    project.projectresponses.append(project_response)
    role.users.append(user)
    group.users.append(user)
    db.session.add(tag5)
    db.session.add(education1)
    db.session.add(user)
    db.session.add(location1)
    db.session.commit()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.engine.execute("drop schema if exists public cascade")
    db.engine.execute("create schema public")


@manager.command
def reset():
    drop_db()
    create_db()
    add_test_data()


server = Server(host=settings.host_ip, port=settings.port)
manager.add_command("runserver", server)

if __name__ == '__main__':
    manager.run()
