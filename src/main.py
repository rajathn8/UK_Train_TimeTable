import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

if __name__ == "__main__":
    import uvicorn

    logging.info("Starting FastAPI app with Uvicorn...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
