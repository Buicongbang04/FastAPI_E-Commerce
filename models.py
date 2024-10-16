from tortoise import Model, fields
from pydantic import BaseModel
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, null=False, unique=True)
    email = fields.CharField(max_length=200, null=False, unique=True)
    password = fields.CharField(max_length=100, null=False)
    is_verified = fields.BooleanField(default=False)
    join_date = fields.DatetimeField(default=datetime.now(datetime.timezone.utc))


class Business(Model):
    id = fields.IntField(pk=True, index=True)
    business_name = fields.CharField(max_length=50, null=False, unique=True)
    city = fields.CharField(max_length=100, null=False, default="Unspecified")
    region =- fields.CharField(max_length=100, null=False, default="Unspecified")
    business_description = fields.TextField(null=False)
    logo = fields.CharField(max_length=200, null=True, default='default.jpg')
    owner = fields.ForeignKeyField('models.User', related_name='business')


class Product(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=100, null=False, index=True)
    category = fields.CharField(mac_length=30, index=True)
    original_price = fields.DecimalField(max_digits=12, decimal_places=2)
    new_price = fields.DecimalField(max_digits=12, decimal_places=2)
    percentage_discount = fields.DecimalField()
    offer_expiration_date = fields.DatetimeField(default=datetime.now(datetime.timezone.utc))
    product_image = fields.CharField(max_length=200, null=False, default='productDefault.jpg')
    business = fields.ForeignKeyField('models.Business', related_name='products')


user_pydantic = pydantic_model_creator(User, name='User', exclude=('is_verified'))
user_pydanticIn = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)
user_pydanticOut = pydantic_model_creator(User, name='UserOut', exclude=('password', ))

business_pydantic = pydantic_model_creator(Business, name='business', exclude=('is_verified'))
business_pydanticIn = pydantic_model_creator(Business, name='businessIn', exclude_readonly=True)

product_pydantic = pydantic_model_creator(Product, name='Product')
product_pydanticIn = pydantic_model_creator(Product, name='ProductIn', exclude=('percentage_discount', 'id'))