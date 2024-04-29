from flask import abort
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase
from decimal import Decimal, DecimalException
from functools import wraps


# Initialise database
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


# Converts an SQLAlchemy object to dictionary
def object_as_dict(obj):
    """Converts an SQLAlchemy object to dictionary"""
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


# Converts all numeric values in a dictionary to a Decimal type
def make_decimal(dict):
    """Converts all numeric values in a dictionary to a Decimal type"""
    for key, value in dict.items():
        try:
            value = Decimal(value)
        except (ValueError, DecimalException):
            pass
    return dict


## Flask-login decorators
def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "superadmin":
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Note "in" role to allow superadmin can also access admin pages
        if not current_user.is_authenticated or "admin" not in current_user.role:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def is_admin():
    if not current_user.is_authenticated or "admin" not in current_user.role:
        return False
    else:
        return True
