# create_roles.py
from main import Role, User, db


def create_roles():
    admin = Role(id=1, name="Admin")
    user = Role(id=2, name="User")

    db.session.add(admin)
    db.session.add(user)

    db.session.commit()
    print("Roles created successfully!")


# Create the above-defined roles
create_roles()
