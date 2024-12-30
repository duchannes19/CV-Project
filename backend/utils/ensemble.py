from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K

def dice_coefficient(y_true, y_pred, smooth=1e-6):
    """
    Computes the Dice Coefficient.

    Args:
        y_true (tf.Tensor): Ground truth masks.
        y_pred (tf.Tensor): Predicted masks.
        smooth (float): Smoothing factor to avoid division by zero.

    Returns:
        tf.Tensor: Dice coefficient.
    """
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)

def dice_loss(y_true, y_pred):
    """
    Computes the Dice Loss.

    Args:
        y_true (tf.Tensor): Ground truth masks.
        y_pred (tf.Tensor): Predicted masks.

    Returns:
        tf.Tensor: Dice loss.
    """
    return 1 - dice_coefficient(y_true, y_pred)


def load_ensemble():
    # Paths to the best models
    model_paths = [
        "best_model_residual_spatial_dropout.keras",
        "best_model_residual_attention.keras",
        "best_model_residual_se.keras"
    ]

    # Load the models
    ensemble_models = []
    for idx, path in enumerate(model_paths, 1):
        try:
            model = load_model(
                path,
                custom_objects={
                    'dice_loss': dice_loss,
                    'dice_coefficient': dice_coefficient
                }
            )
            ensemble_models.append(model)
            print(f"[Ensemble] Loaded Model {idx} from '{path}'.")
        except Exception as e:
            print(f"[Ensemble] Error loading Model {idx} from '{path}': {e}")
    
    return ensemble_models