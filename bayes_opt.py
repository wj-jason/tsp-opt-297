import torch
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_mll
from botorch.optim import optimize_acqf
from botorch.acquisition import LogExpectedImprovement
from gpytorch.mlls import ExactMarginalLogLikelihood
from optimizer import *
from send_recieve import *
import numpy as np
import time
import re
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import glob

bounds = torch.tensor([[0.8, 5000], [0.999, 10000]])  # [param1_min, param2_min], [param1_max, param2_max]

def generate_initial_data(n=5):
    X = torch.rand(n, 2)
    X[:, 0] = X[:, 0] * (bounds[1, 0] - bounds[0, 0]) + bounds[0, 0]  # Scale param1
    X[:, 1] = X[:, 1] * (bounds[1, 1] - bounds[0, 1]) + bounds[0, 1]  # Scale param2
    Y = torch.tensor([[objective_function(x)] for x in X])  # Evaluate cost function
    return X, Y

def min_max_normalize(data, bounds):
    min_vals = bounds[0]
    max_vals = bounds[1]
    return (data - min_vals) / (max_vals - min_vals)

def min_max_denormalize(data, bounds):
    return data * (bounds[1] - bounds[0]) + bounds[0]

# Define the objective function for BoTorch
# params[0] = cooling rate
# params[1] = perturbations

def objective_function(params):
    print(f"Running test with cr={params[0]}, pert={params[1]}")

    run_optimizer(params[0], params[1])

    # print(f"Completed test with alpha={params}")

    with open(f"./current/qor_{params[0]}_{params[1]}.txt", 'r') as file:
        content = file.read()
    
    match = re.search(r"Average QoR:\s([\d\.]+)", content)
    
    return float(match.group(1))

def train_gp_model(train_X, train_Y):
    train_X = min_max_normalize(train_X, bounds)
    train_Y = (train_Y - train_Y.mean()) / train_Y.std() # standardize

    # train_X = train_X.to(torch.float64)
    # train_Y = train_Y.to(torch.float64)

    # train_X = min_max_normalize(train_X, bounds)

    gp = SingleTaskGP(train_X, train_Y)
    mll = ExactMarginalLogLikelihood(gp.likelihood, gp)
    fit_gpytorch_mll(mll)
    return gp

def optimize_acquisition_function(gp):
    LEI = LogExpectedImprovement(gp, best_f=train_Y.min(), maximize=False)
    candidate, _ = optimize_acqf(
        LEI,
        bounds=torch.tensor([[0.0, 0.0], [1.0, 1.0]], dtype=torch.float64),
        q=1,
        num_restarts=10,
        raw_samples=20,
    )
    return min_max_denormalize(candidate.detach(), bounds)

def extract_parameters(file_path):
    """Extracts cooling rate, perturbations, and average QoR from a file."""
    with open(file_path, "r") as file:
        content = file.read()

    # Extract cooling rate and perturbations from filename
    match = re.search(r"qor_([\d\.]+)_([\d\.]+)\.txt", file_path)
    if not match:
        return None  # Skip files that don’t match the pattern

    cooling_rate, perturbations = map(float, match.groups())

    # Extract average QoR
    avg_qor_match = re.search(r"Average QoR:\s([\d\.]+)", content)
    if not avg_qor_match:
        return None  # Skip files without QoR data

    avg_qor = float(avg_qor_match.group(1))

    return cooling_rate, perturbations, avg_qor


def main():
    global train_X, train_Y

    qor_files = glob.glob("./current/qor_*.txt")
    data_points = [extract_parameters(file) for file in qor_files]
    data_points = [d for d in data_points if d is not None]  # Remove None values
    train_X = torch.tensor([[cr, pert] for cr, pert, _ in data_points], dtype=torch.float64)
    train_Y = torch.tensor([[qor] for _, _, qor in data_points], dtype=torch.float64)

    print(train_X)
    print(train_Y)

    # num_iterations = 10
    # for _ in range(num_iterations):
    #     gp = train_gp_model(train_X, train_Y)
    #     next_x = optimize_acquisition_function(gp)
    #     next_y = torch.tensor([[objective_function(next_x[0])]])
        
    #     # Append new data point
    #     train_X = torch.cat([train_X, next_x])
    #     train_Y = torch.cat([train_Y, next_y])

    # Best found solution
    best_idx = train_Y.argmin()
    best_x = train_X[best_idx]
    best_y = train_Y[best_idx]

    # Convert tensors to numpy arrays
    X = train_X.numpy()
    Y = train_Y.numpy().flatten()
    
    # Create a grid to interpolate the cost function surface
    cr_vals = np.linspace(bounds[0, 0].item(), bounds[1, 0].item(), 100)
    pert_vals = np.linspace(bounds[0, 1].item(), bounds[1, 1].item(), 100)
    CR, PERT = np.meshgrid(cr_vals, pert_vals)
    
    # Interpolate cost values over the grid
    Z = griddata(X, Y, (CR, PERT), method='cubic')
    Z = np.clip(Z, np.min(Y), np.max(Y))
    
    # Plot the surface
    plt.figure(figsize=(8, 6))
    cp = plt.contourf(CR, PERT, Z, levels=20, cmap='viridis_r')
    plt.colorbar(cp, label='QoR')
    
    # Scatter points of evaluated parameters
    plt.scatter(X[:, 0], X[:, 1], c='red', marker='o', label='Evaluations')
    
    # Highlight the best point
    plt.scatter(best_x[0], best_x[1], color='white', edgecolors='black', s=100, label=f'Best: {best_x}, QoR: {best_y.item()}')

    plt.xlabel('Cooling Rate')
    plt.ylabel('Perturbations')
    plt.title('QoR Surface')
    plt.legend()

    plot_path = "./plots/qor_surface.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Plot saved to {plot_path}")


def test():
    run_optimizer(0.965, 6500)
    run_optimizer(0.97, 7000)
    run_optimizer(0.89, 7200)

if __name__ == '__main__':
    # run_botorch_optimization()
    # print(objective_function([10, 0]))
    main()