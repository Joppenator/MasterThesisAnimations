import numpy as np
from numba import njit, prange
import time
import cvxpy as cvx
import math

@njit(parallel=True)
def find_best_k_for_dim(d, l_bound, u_bound):
    """
    Returns an array where each row is [n, best_k, best_score].
    Parallelized over n.
    """
    num_n = u_bound - l_bound + 1
    results = np.zeros((num_n, 3), dtype=np.int32)
    
    # prange distributes the loop across all available CPU cores
    for idx in prange(num_n):
        n = l_bound + idx
        best_k = -1
        best_score = -1
        
        for k in range(2, n // 2 + 1):
            # Precompute k^i mod n
            k_pow = np.zeros(d, dtype=np.int64)
            k_pow[0] = 1
            for i in range(1, d):
                k_pow[i] = (k_pow[i-1] * k) % n
                
            score_k = n  # Initialize with a max possible bound
            
            # We only need to check j up to n/2 due to symmetry (j and n-j yield same distances)
            for j in range(1, (n // 2) + 1):
                max_dist_j = 0
                for i in range(d):
                    val = (j * k_pow[i]) % n
                    dist = val if val < n - val else n - val
                    if dist > max_dist_j:
                        max_dist_j = dist
                
                # We want to find the MINIMUM of max_dist_j over all j
                if max_dist_j < score_k:
                    score_k = max_dist_j
                    # PRUNING: If our score for this k is already worse/equal to our best, abort this k early
                    if score_k <= best_score:
                        break
                        
            if score_k > best_score:
                best_score = score_k
                best_k = k
                
        results[idx, 0] = n
        results[idx, 1] = best_k
        results[idx, 2] = best_score
        
    return results

def cycle_adjacency(n):
    G = np.zeros((n, n), dtype=int)
    for i in range(n):
        G[i, (i + 1) % n] = 1
        G[(i + 1) % n, i] = 1
    return G

def solve_theta(G):
    n = G.shape[0]
    X = cvx.Variable((n, n), symmetric=True)

    constraints = [X >> 0]  # X is positive semidefinite
    constraints.append(cvx.trace(X) == 1)  # Diagonal entries are 1
    for i in range(n):
        for j in range(n):
            if G[i, j] == 1 and i != j:
                constraints.append(X[i, j] == 0)  # Non-edges have zero entries

    objective = cvx.Maximize(cvx.sum(X))
    problem = cvx.Problem(objective, constraints)
    problem.solve()

    return problem.value

#Calculates upper bound at n,d using theta function of cycle graph
def upper_bound(n, d):
    G = cycle_adjacency(n)
    theta_value = solve_theta(G)
    return math.floor(theta_value ** d)

def main():
    # dimensions = [3, 4, 5, 6, 7, 8, 9, 10]
    # l_bound = [33, 108, 350, 1101, 3438, 10314, 30942, 92826]
    dimensions = [9, 10, 11, 12, 13]
    l_bound = [30942, 92826, 278478, 835434, 2506302]
    p=7
    
    start_time = time.time()
    
    for d in dimensions:
        print(f"\n--- Dimension {d} ---")
        #u_bound  = upper_bound(p,d)
        u_bound = l_bound[dimensions.index(d)]+1
        print(f"Upper bound: {u_bound}, Lower bound: {l_bound[dimensions.index(d)]}")
        res = find_best_k_for_dim(d, l_bound[dimensions.index(d)], u_bound)
        best = 10000
        best_n = 0
        best_k = 0
        best_q = 0
        best2 = 10000
        best_n2 = 0
        best_k2 = 0
        best_q2 = 0
        for row in res:
            #print(f"n={row[0]:<4} | best_k={row[1]:<4} | max_dist_to_0={row[2]}")
            if (best >= row[0]/row[2]):
                best2 = best
                best_k2 = best_k
                best_n2 = best_n
                best_q2 = best_q
                best = row[0]/row[2]
                best_n = row[0]
                best_k = row[1]
                best_q = row[2]
            elif (best2 >= row[0]/row[2]):
                best2 = row[0]/row[2]
                best_n2 = row[0]
                best_k2 = row[1]
                best_q2 = row[2]
        print(f"Best ratio n/k for dimension {d}: {best:.4f} (n={best_n}, q={best_q}, k={best_k})")
        print(f"Second best ratio n/k for dimension {d}: {best2:.4f} (n={best_n2}, q={best_q2}, k={best_k2})")
            
        
            
    print(f"\nCompleted in {time.time() - start_time:.4f} seconds")

if __name__ == "__main__":
    main()