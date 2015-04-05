from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from datetime import datetime
from .models import *
from PIL import Image as img
import math
from sorl.thumbnail import ImageField
from django.template.defaultfilters import slugify
from django.core.validators import MaxLengthValidator
from sorl.thumbnail import get_thumbnail
from django.core.files.base import ContentFile

from django.db import models

from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)

class PersonManager(BaseUserManager):
    def create_user(self, email,date_of_birth, username,password=None,):
        if not email:
            msg = 'Users must have an email address'
            raise ValueError(msg)
           
        if not username:
            msg = 'This username is not valid'
            raise ValueError(msg)

        if not date_of_birth:
            msg = 'Please Verify Your DOB'
            raise ValueError(msg)

        user = self.model(
            email=PersonManager.normalize_email(email),username=username,date_of_birth=date_of_birth)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,username,password,date_of_birth):
        user = self.create_user(email,password=password,username=username,date_of_birth=date_of_birth)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user



class Person(AbstractBaseUser, PermissionsMixin):

    inbox = (
        ('A', 'Activate'),
        ('D', 'Deactivate'),
        ('F', 'Permit To Friends Only'),
    )



    email = models.EmailField(verbose_name='email address',max_length=255,unique=True,blank=True,null=True)
    username = models.CharField(max_length=255, unique=True,db_index=True,)
    date_of_birth = models.DateField(blank=True,null=True)
    name = models.CharField(max_length=3200, blank=True)
    image = models.ImageField(upload_to='photos', blank=True)
    description = models.CharField(max_length=250,blank=True)
    slug = models.SlugField()
    inbox = models.CharField(max_length=3200, choices=inbox ,default='A')
    profile = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','date_of_birth',]
       
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
       
    objects = PersonManager()
       
    def get_full_name(self):
        return self.email
       
    def get_short_name(self):
        return self.email

    def __unicode__(self):
        return self.email


    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.username)
        super(Person, self).save(*args, **kwargs) 

    def __unicode__(self):
        return self.username


class Board(models.Model):

    SHIRT_SIZES = (

    ('1', 'Adventure Recreation'),
    ('1','Animal'),
    ('2','Architecture'),
    ('3','Art'),
    ('4','Convention'),
    ('5','Fashion'),
    ('6','Festival'),
    ('7','Food'),
    ('8','Holiday'),
    ('9','Literature'),
    ('10','Music'),
    ('11','Outdoor Recereation'),

)
    shirt_size = models.CharField(max_length=3200, choices=SHIRT_SIZES)
    user = models.ForeignKey(Person)
    name = models.CharField(max_length=55)
    profile = models.BooleanField(default=True)
    slug = models.SlugField()
    created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=300,blank=True)
    comments = models.BooleanField(default=True)
    friends = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.name)
        super(Board, self).save(*args, **kwargs)   

    def __unicode__(self):
        return self.name


    def pic(self):
        p = Picture.objects.get(is_primary=True,board=self)
        p.image.url
        return p.image.url

    def pic_image(self):
        p = Picture.objects.get(is_primary=True,board=self)
        return p.image


class Picture(models.Model):
    user = models.ForeignKey(Person)
    board = models.ForeignKey(Board,blank=False,null=False,related_name='board')
    description = models.CharField(blank=False,max_length=3200)
    created = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False)
    image = models.ImageField(upload_to='whatever', blank=True)



    def delete(self, *args, **kwargs):
        self.image.delete(False)
        super(Picture, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.description





class BoardComment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Person)
    body = models.CharField(max_length=300,blank=True)
    board = models.ForeignKey(Board)
 
    def __unicode__(self):
        return self.user.username

class LikeBoard(models.Model):
    user = models.ForeignKey(Person)
    board = models.ForeignKey(Board)
    created = models.DateTimeField(auto_now_add=True)  


class Contact(models.Model):
    BUSINESS = 'BUSINESS'
    General = 'GENERAL'
    Account = 'My Account'
    Technical = 'Technical Problem'
    Feedback =  'Feedback'
    Others = 'Others'
    CATEGORY = (
        (General, 'General'),
        (Account, 'My Account'),
        (Technical, 'Technical Problem'),
        (Feedback, 'Feedback'),
        (Others, 'Others'),
    )
    Category =models.CharField(max_length=3200,choices=CATEGORY)
    text = models.CharField(blank = False,max_length=200)
    email = models.EmailField(blank= False)
    user = models.ForeignKey(Person)

    def __unicode__(self):
        return self.user.username




