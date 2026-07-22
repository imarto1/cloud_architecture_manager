from fastapi import FastAPI

app = FastAPI(title="Cloud Architecture Manager API")


@app.get("/")
async def root():
    return {"message": "Welcome to Cloud Architecture Manager API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

