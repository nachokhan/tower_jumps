from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import aiohttp
import logging
import sys

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROCESSOR_URL = os.getenv("PROCESSOR_URL")

@app.post("/process")
async def process_file(file: UploadFile = File(...)):

    logging.info(f"Recieving file: {file.filename}")
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")

    async with aiohttp.ClientSession() as session:
        form = aiohttp.FormData()
        form.add_field('file', await file.read(), filename=file.filename, content_type=file.content_type)

        async with session.post(
            f"{PROCESSOR_URL}/process",
            data=form,
            timeout=aiohttp.ClientTimeout(total=60*10)
        ) as sync_response:
            if sync_response.status != 200:
                raise HTTPException(status_code=sync_response.status, detail="Error from sync processor")
            sync_data = await sync_response.json()

    return {"sync_result": sync_data}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
