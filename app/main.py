from fastapi import FastAPI
from starlette.responses import JSONResponse
from routes import analyze

app = FastAPI(title="ResumeAnalyzer", version="0.1.0")


@app.get("/ping")
def ping():
    return JSONResponse({"message": "pong"})


app.include_router(analyze.router)
