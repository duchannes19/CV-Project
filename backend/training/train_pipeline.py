import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from ..models.unet import UNet
from ..utils.metrics import dice_loss
from ..utils.logger import logger

def train(model, train_loader, val_loader, epochs=50, lr=1e-3, device='cuda'):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    model.to(device)
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for images, masks in train_loader:
            images, masks = images.to(device), masks.to(device)
            pred = model(images)
            loss = dice_loss(pred, masks)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for images, masks in val_loader:
                images, masks = images.to(device), masks.to(device)
                pred = model(images)
                loss = dice_loss(pred, masks)
                val_loss += loss.item()
        
        logger.info(f"Epoch {epoch}: Train Loss {train_loss/len(train_loader)}, Val Loss {val_loss/len(val_loader)}")

    return model