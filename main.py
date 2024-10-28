from fastapi import FastAPI, Request, HTTPException, status, Depends
from tortoise.contrib.fastapi import register_tortoise
from models import *

# authentication
from authentication import *
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_curr_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, config['SECRET'], algorithms=["HS256"])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return await user

@app.post('/user/me')
async def user_login(user: user_pydanticIn = Depends(get_curr_user)):
    business = await Business.get(owner=user)

    return {
        "status": "Success",
        "message": "User logged in successfully",
        "data": {
            "username": user.username,
            "email": user.email,
            "verified": user.is_verified,
            "joined_date": user.join_date.strftime("%b-%d-%Y"),
            
        }
    }

@app.post('/token')
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {"access_token": token, "token_type": "bearer"}



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


