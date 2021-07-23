from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager



class UserManager(BaseUserManager):
    """ This is model manager for customized user model which uses email as default username field. """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """ This method creates and saves new user through email and password. """

        if not email:
            raise ValueError("Email is required!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """ This method creates and saves regular users using email and password. """

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """ This method creates and saves superuser using email and password. """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)


        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(blank=True,
                              unique=True,
                              )
    name = models.CharField(max_length=150,
                                  null=True,
                                  blank=True,
                                  )

    date_of_birth = models.DateField(blank=True,
                                     null=True,
                                     )


    is_active = models.BooleanField(default=False,
                                    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
