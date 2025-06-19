from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"} 