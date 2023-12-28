from fastapi import FastAPI
from routes.user import router as UserRouter
from routes.invoice import router as InvoiceRouter

app = FastAPI(debug=True)


app.include_router(UserRouter)
app.include_router(InvoiceRouter)
