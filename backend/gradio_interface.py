# backend/gradio_interface.py

import gradio as gr
import torch
from app.models.unet import UNet
#from app.models.fcn import FCN  # Assuming you have an FCN implementation
#from app.models.segdgan import SegDGAN  # Assuming you have a SegDGAN implementation
from app.training.train_pipeline import train
from app.training.evaluate_pipeline import evaluate
#from app.utils.config import CONFIG  # Assuming you have a config file
#from app.utils.logger import logger

# Define a mapping from model names to classes
MODEL_CLASSES = {
    "U-Net": UNet,
    #"FCN": FCN,
    #"SegDGAN": SegDGAN
}

def train_model(model_name, epochs, learning_rate):
    """
    Train the selected model with the provided hyperparameters.
    """
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #logger.info(f"Training {model_name} on {device}")
        
        # Initialize the model
        ModelClass = MODEL_CLASSES.get(model_name)
        if not ModelClass:
            return f"Model {model_name} is not supported."
        
        model = ModelClass(in_channels=1, out_channels=2)  # Adjust channels as needed
        model.to(device)
        
        # Define training parameters
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        criterion = torch.nn.CrossEntropyLoss()  # Or use dice_loss as defined earlier
        
        # Call the training function
        train(model=model, 
              train_loader=None,  # Replace with actual DataLoader
              val_loader=None,    # Replace with actual DataLoader
              epochs=epochs, 
              optimizer=optimizer, 
              criterion=criterion, 
              device=device)
        
        return f"Training of {model_name} completed successfully."
    
    except Exception as e:
        #logger.error(f"Error during training: {str(e)}")
        return f"An error occurred during training: {str(e)}"

def evaluate_model(model_name):
    """
    Evaluate the selected model and return metrics.
    """
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #logger.info(f"Evaluating {model_name} on {device}")
        
        # Initialize the model
        ModelClass = MODEL_CLASSES.get(model_name)
        if not ModelClass:
            return f"Model {model_name} is not supported."
        
        model = ModelClass(in_channels=1, out_channels=2)  # Adjust channels as needed
        model.to(device)
        
        # Load the trained model weights
        model.load_state_dict(torch.load(f"models/{model_name.lower()}_weights.pth", map_location=device))
        model.eval()
        
        # Call the evaluation function
        metrics = evaluate(model=model, 
                           test_loader=None,  # Replace with actual DataLoader
                           device=device)
        
        # Assuming metrics is a dictionary containing 'Dice' and 'Hausdorff'
        dice = metrics.get("Dice", "N/A")
        hausdorff = metrics.get("Hausdorff", "N/A")
        
        return f"Evaluation Results for {model_name}:\nDice Similarity Coefficient (DSC): {dice}\nHausdorff Distance (HD): {hausdorff}"
    
    except Exception as e:
        #logger.error(f"Error during evaluation: {str(e)}")
        return f"An error occurred during evaluation: {str(e)}"

def main():
    """
    Define and launch the Gradio interface.
    """
    with gr.Blocks() as demo:
        gr.Markdown("# Prostate Cancer Segmentation Model Training and Evaluation")
        
        with gr.Tab("Train Model"):
            with gr.Row():
                model_dropdown = gr.Dropdown(choices=list(MODEL_CLASSES.keys()), value="U-Net", label="Select Model")
                epochs_input = gr.Number(value=50, label="Number of Epochs", precision=0)
                lr_input = gr.Number(value=1e-3, label="Learning Rate", precision=5)
            train_button = gr.Button("Start Training")
            train_output = gr.Textbox(label="Training Status")
            
            train_button.click(fn=train_model, 
                               inputs=[model_dropdown, epochs_input, lr_input], 
                               outputs=train_output)
        
        with gr.Tab("Evaluate Model"):
            with gr.Row():
                eval_model_dropdown = gr.Dropdown(choices=list(MODEL_CLASSES.keys()), value="U-Net", label="Select Model for Evaluation")
            evaluate_button = gr.Button("Evaluate Model")
            evaluate_output = gr.Textbox(label="Evaluation Metrics", lines=4)
            
            evaluate_button.click(fn=evaluate_model, 
                                  inputs=[eval_model_dropdown], 
                                  outputs=evaluate_output)
    
    demo.launch(server_name="0.0.0.0", server_port=7861)  # You can change the port as needed

if __name__ == "__main__":
    main()
