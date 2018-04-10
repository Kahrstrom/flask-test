import jwt
import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event, inspect
from flask import g
from sqlalchemy_utils.types.choice import ChoiceType

from project import app, db, bcrypt
from .enums import UserType, EducationType, ResponseType


class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    timestamp = db.Column(db.DateTime)

    @declared_attr
    def created_by_user_id(self):
        return db.Column(db.Integer, db.ForeignKey('user.id'))

    @declared_attr
    def updated_by_user_id(self):
        return db.Column(db.Integer, db.ForeignKey('user.id'))

    @declared_attr
    def created_by(self):
        return db.relationship('User', foreign_keys=[self.created_by_user_id])

    @declared_attr
    def updated_by(self):
        return db.relationship('User', foreign_keys=[self.updated_by_user_id])

    @property
    def _descriptive(self):
        return self.id

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def after_insert(mapper, connection, target):
        pass

    @staticmethod
    def after_update(mapper, connection, target):
        pass

    @staticmethod
    def before_update(mapper, connection, target):
        target.timestamp = datetime.datetime.utcnow()
        target.updated_by_user_id = getattr(g, 'user_id', None)

    @staticmethod
    def before_insert(mapper, connection, target):
        target.created_by_user_id = getattr(g, 'user_id', None)

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls.before_update)
        event.listen(cls, 'before_insert', cls.before_insert)
        event.listen(cls, 'after_update', cls.after_update)
        event.listen(cls, 'after_insert', cls.after_insert)


class ExperienceMixin(object):
    highlight = db.Column(db.Boolean, default=False)


class User(BaseMixin, db.Model):
    """ User Model for storing user related details """
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    verified = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow())
    admin = db.Column(db.Boolean, nullable=False, default=False)
    user_type = db.Column(ChoiceType(UserType, impl=db.Integer()))

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group', foreign_keys=[group_id], backref='users')

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', foreign_keys=[role_id], backref='users')

    @property
    def _descriptive(self):
        return self.name

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.password = bcrypt.generate_password_hash(
            kwargs['password'], app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def encode_auth_token(self, days=1):
        """
        Generates the Auth Token
        :return: string
        """
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=days),
            'iat': datetime.datetime.utcnow(),
            'sub': self.id,
            'admin': self.admin
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        ).decode('utf-8')

    def check_password_hash(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False


class Role(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    main_role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    main_role = db.relationship('Role', remote_side=[id],  backref='subroles')

    @property
    def all_users_id(self):
        all_roles = [item.id for item in self.get_children_list(self.id)]
        all_users = db.session.query(User).filter(
            User.role_id.in_(all_roles)).all()
        return all_users

    @staticmethod
    def get_children_list(role_id):
        beginning_getter = db.session.query(Role).\
            filter(Role.id == role_id).cte(name='children_for', recursive=True)
        with_recursive = beginning_getter.union_all(
            db.session.query(Role).filter(
                Role.main_role_id == beginning_getter.c.id, Role.id != role_id)
        )
        return db.session.query(with_recursive).all()

    @property
    def _descriptive(self):
        return self.name


class Group(BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    address = db.Column(db.String(50))
    zipcode = db.Column(db.String(10))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))

    main_group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    main_group = db.relationship(
        'Group', remote_side=[id], backref='subgroups')

    @property
    def _descriptive(self):
        return self.name

    @property
    def all_users_id(self):
        all_groups = [item.id for item in self.get_children_list(self.id)]
        all_users = db.session.query(User).filter(
            User.group_id.in_(all_groups)).all()
        return all_users

    @staticmethod
    def get_children_list(group_id):
        beginning_getter = db.session.query(Group).\
            filter(Group.id == group_id).cte(
                name='children_for', recursive=True)
        with_recursive = beginning_getter.union_all(
            db.session.query(Group).filter(
                Group.main_group_id == beginning_getter.c.id)
        )
        return db.session.query(with_recursive).all()


class Location(BaseMixin, db.Model):
    description = db.Column(db.String(50), default='')
    latitude = db.Column(db.Float(10, 8))
    longitude = db.Column(db.Float(10, 8))

    street = db.Column(db.String(50), nullable=False)
    zipcode = db.Column(db.String(10), default='')
    city = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)

    @property
    def _descriptive(self):
        return '{}, {} - {}'.format(
            self.street, self.city, self.country)


class ContactPerson(BaseMixin, db.Model):
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50))

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', backref='contactpersons')


class Customer(BaseMixin, db.Model):
    name = db.Column(db.String(50), nullable=False)
    customer_number = db.Column(db.String(50), default='')
    registration_number = db.Column(db.String(50), default='')

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', backref='customers')

    @property
    def _descriptive(self):
        return '{}, {}'.format(
            self.name, self.customer_number)


class Project(BaseMixin, db.Model):
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(), default='')

    startdate = db.Column(db.DateTime())
    enddate = db.Column(db.DateTime())
    hours = db.Column(db.Integer, default=0)

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', backref='projects')

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', backref='projects')

    @property
    def _descriptive(self):
        return self.title + (
            ', {}'.format(self.customer.name) if self.customer != '' else '')


class ProjectResponse(BaseMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', foreign_keys=[user_id], backref='projectresponses')

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='projectresponses')

    price = db.Column(db.Integer, default=0)
    type = db.Column(ChoiceType(
        ResponseType,
        impl=db.String()), default=ResponseType.empty.value)

    @property
    def _descriptive(self):
        return '{} - {} - {}'.format(
            self.user.name, self.type, self.project.title)

    def add_activity(self, new, session):
        new_value = next(iter(inspect(self).attrs.type.history.added), None)
        old_value = next(iter(inspect(self).attrs.type.history.deleted), None)
        if old_value:
            old_value = old_value.value
        if not new and new_value == old_value:
            print('uppdatera inte')
            return

        origin = self.user.name
        target = self.project._descriptive
        if self.type == ResponseType.interested.value:
            action = '{} is interested in the project {}'
        elif self.type == ResponseType.accepted.value:
            action = '{} was accepted for the project {}'
        elif self.type == ResponseType.proposed.value:
            action = '{} was proposed for the project {}'
        else:
            return

        activity = Activity(**{
            'action': action.format(origin, target),
            'user_id': self.user.id,
            'project_response_id': self.id
        })
        session.add(activity)


class Education(BaseMixin, ExperienceMixin, db.Model):
    title = db.Column(db.String(50), nullable=False)
    school = db.Column(db.String(50), default='')
    extent = db.Column(db.String(50), default='')
    description = db.Column(db.String(), default='')
    type = db.Column(ChoiceType(
        EducationType,
        impl=db.String()), default=EducationType.education.value)

    startdate = db.Column(db.DateTime())
    enddate = db.Column(db.DateTime())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', foreign_keys=[user_id], backref='educations')

    @property
    def _descriptive(self):
        return self.title + (
            ', {}'.format(self.school) if self.school != '' else '')


class WorkExperience(BaseMixin, ExperienceMixin, db.Model):
    title = db.Column(db.String(50), nullable=False)
    employer = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(), default='')

    startdate = db.Column(db.DateTime())
    enddate = db.Column(db.DateTime())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', foreign_keys=[user_id], backref='work_experience')

    @property
    def _descriptive(self):
        return '{}, {}'.format(self.title, self.employer)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='tags')

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='tags')

    education_id = db.Column(db.Integer, db.ForeignKey('education.id'))
    education = db.relationship('Education', backref='tags')

    work_experience_id = db.Column(
        db.Integer, db.ForeignKey('work_experience.id'))
    work_experience = db.relationship('WorkExperience', backref='tags')


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='activities')

    project_response_id = db.Column(
        db.Integer, db.ForeignKey('project_response.id'))
    project_response = db.relationship(
        'ProjectResponse', backref='activities')

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='activities')

    education_id = db.Column(db.Integer, db.ForeignKey('education.id'))
    education = db.relationship('Education', backref='activities')

    work_experience_id = db.Column(
        db.Integer, db.ForeignKey('work_experience.id'))
    work_experience = db.relationship('WorkExperience', backref='activities')

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', backref='activities')

    action = db.Column(db.String(150), default='')

    @property
    def _descriptive(self):
        return '{} {} {}'.format(self.origin, self.action, self.target)


# LOG ACTIVITIES
# I.e. 'John Doe is interested in Cool project, BMW'
# or   'Jane Doe was accepted for Cool project2, Volvo'
@event.listens_for(db.Session, 'after_flush')
def test(session, ctx):
    for instance in session.dirty:
        if not getattr(instance, 'add_activity', None):
            print('nope')
            continue
        instance.add_activity(new=False, session=session)

    for instance in session.new:
        if not getattr(instance, 'add_activity', None):
            print('nope')
            continue
        instance.add_activity(new=False, session=session)
