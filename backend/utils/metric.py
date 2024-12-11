import torch
import torch.nn.functional as F
import numpy as np
from scipy.spatial.distance import directed_hausdorff

# Dice Similarity Coefficient (DSC)
# DSC = 2|X∩Y|/(|X|+|Y|)
# For prediction P and ground-truth G:
# \[
# DSC(P,G) = \frac{2\sum_i p_i g_i}{\sum_i p_i + \sum_i g_i}
# \]
def dice_coefficient(pred, target):
    pred = torch.argmax(pred, dim=1)
    pred = pred.float()
    target = target.float()
    intersection = (pred * target).sum()
    return (2.0 * intersection) / (pred.sum() + target.sum() + 1e-8)

def dice_loss(pred, target):
    return 1 - dice_coefficient(pred, target)

# Hausdorff Distance (HD)
# Given two sets of points A and B, HD(A,B) = max{ max_{a∈A} min_{b∈B} d(a,b), max_{b∈B} min_{a∈A} d(a,b) }
def hausdorff_distance(pred_mask, gt_mask):
    # Convert to binary
    pred_pts = np.argwhere(pred_mask)
    gt_pts = np.argwhere(gt_mask)
    if len(pred_pts) == 0 or len(gt_pts) == 0:
        return np.inf
    forward_hd = directed_hausdorff(pred_pts, gt_pts)[0]
    backward_hd = directed_hausdorff(gt_pts, pred_pts)[0]
    return max(forward_hd, backward_hd)