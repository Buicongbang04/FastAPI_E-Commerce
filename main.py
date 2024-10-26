from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import *
from authentication import getHashedPassword

from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient


app = FastAPI()

@post_save(User)
async def create_business(
    sender: Type[User],
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str]
) -> None:
    if created:
        business_obj = await Business.create(
            business_name = instance.username,
            owner = instance  
        )

    await business_pydantic.from_tortoise_orm(business_obj)

@app.get('/')
def index():
    return {"message": "Welcome to the E-commerce API"}

@app.post('/registration')
async def user_registration(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info['password'] = getHashedPassword(user_info['password'])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return {
        "Status": "Success",
        "Message": "User created successfully",
        "Data": f"Welcom {new_user.username}"
    }




register_tortoise(
    app,
    db_url='sqlite://data/db.sqlite3',
    modules = {"models": ["models"]},
    generate_schemas=True, 
    add_exception_handlers=True
)

