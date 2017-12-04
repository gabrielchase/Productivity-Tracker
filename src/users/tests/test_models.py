import pytest

from django.contrib.auth import get_user_model
from mixer.backend.django import mixer
from users.tests.fixtures import new_user_info

# IMPORTANT: Allows tests to write into the database 
pytestmark = pytest.mark.django_db
User = get_user_model()


class TestUser:

    def test_model_create_user(self, new_user_info):
        new_user = User.objects.create_user(
            first_name=new_user_info['first_name'],
            last_name=new_user_info['last_name'],
            email=new_user_info['email'],
            country=new_user_info['country'],
            mobile_number=new_user_info['mobile_number'],
            goal=new_user_info['goal'],
            password=new_user_info['password']
        )

        expected_username = '{}{}'.format(new_user_info['first_name'], new_user_info['last_name'])
        
        assert new_user.id == 1, 'User instance should be created'
        assert new_user.first_name == new_user_info['first_name'], 'first_name should be the same'
        assert new_user.last_name == new_user_info['last_name'], 'last_name should be the same'
        assert new_user.email == new_user_info['email'], 'email should be the same'
        assert new_user.username == expected_username, 'username should be the same first_name + last_name'
        assert new_user.password != new_user_info['password'], 'password is hashed'

        assert new_user.get_full_name() == '{}, {}'.format(new_user.last_name, new_user.first_name)
        assert new_user.get_short_name() == new_user.username
        assert str(new_user) == '({}, {}, {}, {}, {})'.format(new_user.id, new_user.first_name, new_user.last_name, new_user.email, new_user.username)

        assert new_user.details.user.id == new_user.id
        assert str(new_user.details) == str(new_user)
        assert new_user.details.country == new_user_info['country']
        assert new_user.details.mobile_number == new_user_info['mobile_number']
        assert new_user.details.goal == new_user_info['goal']

    def test_model_exceptions(self, new_user_info):
        
        # User with first_name and last_name is created
        u1 = User.objects.create_user(
            new_user_info['first_name'],
            new_user_info['last_name'],
            new_user_info['email'],
            new_user_info['password']
        )

        assert u1.id == 2, 'User is created'

        # Fail because the email address is already used
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_user(
                new_user_info['first_name'],
                new_user_info['last_name'],
                new_user_info['email'],
                new_user_info['password']
            )
        assert str(excinfo.value) == 'Email address is already taken'

        # Fail because the email address is ''
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_user(
                first_name=new_user_info['first_name'],
                last_name=new_user_info['last_name'],
                email='',
                password=new_user_info['password']
            )
        assert str(excinfo.value) == 'Users must register an email address'

        # Fail because the email address is type None
        with pytest.raises(ValueError) as excinfo:
            User.objects.create_user(
                first_name=new_user_info['first_name'],
                last_name=new_user_info['last_name'],
                email=None,
                password=new_user_info['password']
            )
        assert str(excinfo.value) == 'Users must register an email address', 'Exception that handles email provided in registration is None'

        # User with the same first_name last_name is created 
        # because it has a different email.
        # This user's username appends the number of instance it is in the database to the end
        other_email = mixer.faker.email()
        instances = User.objects.filter(first_name=new_user_info['first_name'], last_name=new_user_info['last_name']).count()
        u2 = User.objects.create_user(
            new_user_info['first_name'],
            new_user_info['last_name'],
            other_email,
            new_user_info['password']
        )

        assert u2.first_name == new_user_info['first_name']
        assert u2.last_name == new_user_info['last_name']
        assert u2.email == other_email
        assert u2.password != new_user_info['password']
        assert u2.username == '{}{}-{}'.format(new_user_info['first_name'], new_user_info['last_name'], instances+1)
        
        # Same case as above but with a different instance appended to the end
        other_email_2 = mixer.faker.email()
        instances_2 = User.objects.filter(first_name=new_user_info['first_name'], last_name=new_user_info['last_name']).count()
        u3 = User.objects.create_user(
            new_user_info['first_name'],
            new_user_info['last_name'],
            other_email_2,
            new_user_info['password']
        )

        assert u3.first_name == new_user_info['first_name']
        assert u3.last_name == new_user_info['last_name']
        assert u3.email == other_email_2
        assert u3.password != new_user_info['password']
        assert u3.username == '{}{}-{}'.format(new_user_info['first_name'], new_user_info['last_name'], instances_2+1)
        