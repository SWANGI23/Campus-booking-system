# models.py
# Object-oriented design: User (superclass) with three subclasses.
# Data attributes are hidden with two underscores (encapsulation) and
# are accessed only through accessor (get_) methods.

class User:
    """General user. Subclasses are specialised versions (an 'is a' relationship)."""

    def __init__(self, username, password, role):
        self.__username = username
        self.__password = password        # hidden: outside code cannot read it directly
        self.__role = role

    def get_username(self):
        return self.__username

    def get_role(self):
        return self.__role

    def check_password(self, attempt):
        """The password is never returned - we only compare it."""
        return attempt == self.__password

    # The methods below are overridden by the subclasses (polymorphism).
    def get_welcome(self):
        return 'Welcome, ' + self.__username

    def can_choose_campus(self):
        return False

    def get_permissions(self):
        return []


class Lecturer(User):
    def __init__(self, username, password):
        User.__init__(self, username, password, 'Lecturer')

    def get_welcome(self):
        return 'Lecturer: ' + self.get_username()

    def can_choose_campus(self):
        return True

    def get_permissions(self):
        return ['Book resources', 'View own booking history', 'Cancel future bookings']


class CampusAdmin(User):
    def __init__(self, username, password, campus):
        User.__init__(self, username, password, 'CampusAdmin')
        self.__campus = campus            # an administrator belongs to ONE campus

    def get_campus(self):
        return self.__campus

    def get_welcome(self):
        return 'Campus Administrator: ' + self.get_username()

    def get_permissions(self):
        return ['Add/update/remove resources', 'View campus bookings', 'Monitor usage']


class SystemOperator(User):
    def __init__(self, username, password):
        User.__init__(self, username, password, 'SystemOperator')

    def get_welcome(self):
        return 'System Operator: ' + self.get_username()

    def can_choose_campus(self):
        return True

    def get_permissions(self):
        return ['View all campuses', 'Comparative reports']


class Resource:
    """A bookable campus resource."""

    def __init__(self, resource_id, name, rtype, campus):
        self.__resource_id = resource_id
        self.__name = name
        self.__rtype = rtype
        self.__campus = campus

    def get_resource_id(self):
        return self.__resource_id

    def get_name(self):
        return self.__name

    def get_type(self):
        return self.__rtype

    def get_campus(self):
        return self.__campus


def make_user(row):
    """Build the correct subclass from a database row (username, password, role, campus)."""
    (username, password, role, campus) = row     # tuple unpacking
    if role == 'Lecturer':
        return Lecturer(username, password)
    if role == 'CampusAdmin':
        return CampusAdmin(username, password, campus)
    return SystemOperator(username, password)
