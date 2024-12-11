from fastapi import FastAPI, UploadFile, File
from .routes import infer, train, data

app = FastAPI(title="Prostate Segmentation Backend")

app.include_router(infer.router, prefix="/infer", tags=["Inference"])
app.include_router(train.router, prefix="/train", tags=["Training"])
app.include_router(data.router, prefix="/data", tags=["Data"])