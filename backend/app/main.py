from fastapi import FastAPI  

app = FastAPI(
    title = "Nexus Clip API",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message":"Nexus Clip API"}