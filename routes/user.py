from db.conn import connection
from pymysql import Error as pymysql_error
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from services.auth import *

router = APIRouter(tags=["User endpoints"])


class User(BaseModel):
    id: int = None
    email: str


class UserDB(User):
    password: str


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=os.getenv("ALGORITHM")
        )
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credential_exception


@router.post("/userSignUp")
async def user_signup(user: UserDB):
    hashed = hash_password(user.password)
    try:
        with connection:
            # The connection would be closed because of timeout exceeded, therefore it is needed to reconnect.
            connection.ping()
            with connection.cursor() as cursor:
                query = "INSERT INTO users (u_email, u_password) VALUES (%s, %s)"
                cursor.execute(query, (user.email, hashed))
            connection.commit()
        return {"msg": "OK"}
    except pymysql_error:
        raise HTTPException(status_code=405, detail="Database connection error.")


@router.post("/userLogin")
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        with connection:
            connection.ping()
            with connection.cursor() as cursor:
                query = "SELECT * FROM users WHERE u_email = %s"
                cursor.execute(query, (form_data.username))
                userDB = cursor.fetchone()
                if not userDB:
                    raise HTTPException(
                        status_code=404, detail="Wrong email or password."
                    )
        if verify_password(form_data.password, userDB["u_password"]):
            authenticatedUser = User(id=userDB["u_id"], email=userDB["u_email"])
            access_token_expires = timedelta(
                seconds=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
            )
            access_token = create_access_token(
                data=jsonable_encoder(authenticatedUser),
                expires_delta=access_token_expires,
            )
            return {"access_token": access_token, "token_type": "bearer"}
        raise HTTPException(status_code=404, detail="Wrong email or password.")
    except pymysql_error:
        raise HTTPException(status_code=405, detail="Database connection error.")
