from fastapi import APIRouter, File, UploadFile
import numpy as np
import pydicom
import io
from ..inference.inference_pipeline import run_inference
from ..models.unet import UNet

router = APIRouter()

# Load pre-trained model (path from config)
model = UNet(in_channels=1, out_channels=2)
# model.load_state_dict(torch.load("model_weights.pth"))

@router.post("/run")
async def run_segmentation(file: UploadFile = File(...)):
    # Parse DICOM file
    dicom_data = pydicom.dcmread(file.file)
    image = dicom_data.pixel_array.astype(np.float32)
    
    # Run inference
    pred_mask = run_inference(model, image, device='cuda')
    
    # Return mask and metrics
    # In practice, store the mask and return a resource ID.
    # Here, returning raw array might not be suitable. 
    return {"status": "success", "mask": pred_mask.tolist()}