from db.conn import connection
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from pydantic import BaseModel
from pymysql import Error as pymysql_error
from services.auth import *


class Documents(BaseModel):
    doc1: str
    doc2: str
    doc3: str


router = APIRouter(tags=["Invoice endpoints"])


@router.post("/documents")
def upload_documents(documents: Documents, token: str = Depends(oauth2_scheme)):
    if verify_token(token):
        try:
            with connection:
                # The connection would be closed because of timeout exceeded, therefore it is needed to reconnect.
                connection.ping()
                with connection.cursor() as cursor:
                    query = "INSERT INTO invoice (i_document1, i_document2, i_document3) VALUES (%s, %s, %s)"
                    cursor.execute(
                        query, (documents.doc1, documents.doc2, documents.doc3)
                    )

                connection.commit()
            return {"msg": "OK"}
        except pymysql_error:
            raise HTTPException(status_code=405, detail="Database connection error.")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/files")
def sube_documento(file : UploadFile):
    return { "filename" : file.filename}