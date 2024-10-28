from fastapi import FastAPI, Request, HTTPException, status
from tortoise.contrib.fastapi import register_tortoise
from models import *
from authentication import getHashedPassword, verify_token

# signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from emails import send_email

# response classes
from fastapi.responses import HTMLResponse

# templates
from fastapi.templating import Jinja2Templates

app = FastAPI()

@post_save(User)
async def create_business(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str]
) -> None:
    if created:
        business_obj = await Business.create(business_name = instance.username, owner = instance)

        await business_pydantic.from_tortoise_orm(business_obj)

        # Send the email to the user
        await send_email([instance.email], instance)

@app.get('/')
def index():
    return {"message": "Welcome to the E-commerce API"}

@app.post('/registration')
async def user_registration(user: user_pydanticIn): # type: ignore
    user_info = user.dict(exclude_unset=True)
    user_info['password'] = getHashedPassword(user_info['password'])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return {
        "Status": "Success",
        "Message": "User created successfully",
        "Data": f"Welcom {new_user.username}"
    }


templates = Jinja2Templates(directory="templates")

@app.get('/verification', response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await verify_token(token)

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse("verification.html", 
                                          {"request": request, "username": user.username})
    raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or Expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

register_tortoise(
    app,
    db_url='sqlite://data/db.sqlite3',
    modules = {"models": ["models"]},
    generate_schemas=True, 
    add_exception_handlers=True
)

