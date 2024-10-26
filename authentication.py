from passlib.context import CryptContext

pwd_context =  CryptContext(schemes=["bcrypt"], deprecated="auto")


def getHashedPassword(password):
    return pwd_context.hash(password)
























