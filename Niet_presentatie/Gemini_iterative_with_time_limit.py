import numpy as np
from itertools import combinations
import math
from math import gcd
import pandas as pd
import matplotlib.pyplot as plt
import time
import pickle

def get_best_q_vectorized(generators, n, chunk_size=50000):
    """
    Evaluates the 'q' metric (minimum maximum distance to the 0 vector mod n) 
    for a list of generators. Uses chunking to prevent out-of-memory errors on large sets.
    """
    if len(generators) == 0:
        return 0, None
        
    generators = np.array(generators, dtype=np.int32)
    best_q = -1
    best_g = None
    
    # c_vals shape: (n-1, 1, 1) to broadcast against (chunk_size, d)
    c_vals = np.arange(1, n, dtype=np.int32).reshape(-1, 1, 1)
    
    for i in range(0, len(generators), chunk_size):
        chunk = generators[i:i + chunk_size]
        
        # Reshape chunk to (1, chunk_size, d)
        g_reshaped = chunk.reshape(1, chunk.shape[0], chunk.shape[1])
        
        # Calculate multiples modulo n
        # Shape: (n-1, chunk_size, d)
        multiples = (c_vals * g_reshaped) % n
        
        # Calculate distance to 0 mod n
        dists = np.minimum(multiples, n - multiples)
        
        # Infinity norm: max across coordinates (axis=2)
        # Shape: (n-1, chunk_size)
        max_dists = np.max(dists, axis=2)
        
        # Minimum non-zero distance across all elements in the subgroup (axis=0)
        # Shape: (chunk_size,)
        qs = np.min(max_dists, axis=0)
        
        # Find the max q in this chunk
        chunk_best_idx = np.argmax(qs)
        chunk_best_q = qs[chunk_best_idx]
        
        if chunk_best_q > best_q:
            best_q = chunk_best_q
            best_g = chunk[chunk_best_idx]
            
    return best_q, best_g

def get_best_q_vectorized_2d_unique(generators, n, p=None, chunk_size=None):
    """
    Evaluates the 'q' metric for pairs of generators.
    Calculates s*gen_1 + t*gen_2 mod p, where s and t range from 0 to n-1.
    """
    if len(generators) == 0:
        return 0, None, 0
        
    p = p if p is not None else n
    generators = np.array(generators, dtype=np.int32)
    
    if generators.ndim != 3 or generators.shape[1] != 2:
        raise ValueError("Generators must have shape (N, 2, d) representing N pairs of d-dimensional vectors.")
        
    d = generators.shape[2]
    
    # Calculate a safe chunk size to keep RAM usage around ~100-200MB per chunk
    if chunk_size is None:
        chunk_size = max(1, 10_000_000 // ((n**2) * d))
        
    best_q = -1
    best_g = None
    
    # Pre-compute all (s, t) combinations from 0 to n-1
    s = np.arange(n, dtype=np.int32)
    t = np.arange(n, dtype=np.int32)
    S, T = np.meshgrid(s, t, indexing='ij')
    
    # Flatten and remove the (0, 0) case (which is at index 0)
    s_flat = S.ravel()[1:]
    t_flat = T.ravel()[1:]
    
    # Reshape for broadcasting: (V, 1, 1) where V = n**2 - 1
    s_vals = s_flat.reshape(-1, 1, 1)
    t_vals = t_flat.reshape(-1, 1, 1)
    
    for i in range(0, len(generators), chunk_size):
        chunk = generators[i:i + chunk_size]
        
        # Split chunk into g1 and g2 and reshape to (1, chunk_size, d)
        g1 = chunk[:, 0, :].reshape(1, chunk.shape[0], d)
        g2 = chunk[:, 1, :].reshape(1, chunk.shape[0], d)
        
        # Calculate multiples modulo p
        # s_vals * g1 triggers broadcast: (V, 1, 1) * (1, C, d) -> (V, C, d)
        multiples = (s_vals * g1 + t_vals * g2) % p

        # Calculate distance to 0 mod p
        dists = np.minimum(multiples, p - multiples)
        
        # Infinity norm: max across coordinates (axis=2)
        # Shape: (V, chunk_size)
        max_dists = np.max(dists, axis=2)

        # Dispose of 0 vectors
        max_dists[max_dists == 0] = p

        # Minimum non-zero distance across all elements in the subgroup (axis=0)
        qs = np.min(max_dists, axis=0)
        
        # Reset those that generated only 0 vectors back to 0
        qs[qs == p] = 0
        
        # Find the max q in this chunk
        chunk_best_idx = np.argmax(qs)
        chunk_best_q = qs[chunk_best_idx]
        
        if chunk_best_q > best_q:
            best_q = chunk_best_q
            best_g = chunk[chunk_best_idx]
            
    # Calculate unique elements for the absolute best generator pair
    best_unique_count = 0
    if best_g is not None:
        s_all = S.ravel().reshape(-1, 1)
        t_all = T.ravel().reshape(-1, 1)
        
        g1_best = best_g[0].reshape(1, d)
        g2_best = best_g[1].reshape(1, d)
        
        all_multiples = (s_all * g1_best + t_all * g2_best) % p
        unique_elements = np.unique(all_multiples, axis=0)
        non_zero_unique = unique_elements[np.any(unique_elements != 0, axis=1)]
        best_unique_count = len(non_zero_unique) + 1
            
    return best_q, best_g, best_unique_count

def is_pairwise_coprime(tup):
    for i in range(len(tup)):
        for j in range(i + 1, len(tup)):
            if gcd(tup[i], tup[j]) > 1:
                return False
    return True

def generate_optimal_lattices_time_bounded(p_min, p_max, time_per_gen=3600):
    """
    Evaluates lattice generators grouping by generator type, then dimension, then n.
    Limits execution strictly by wall-clock time per generator.
    
    Args:
        p_min: Lower bound scalar for n bounds
        p_max: Upper bound scalar for n bounds
        time_per_gen: Time limit per generator type in seconds (default 3600s = 1 hour)
        max_iter_time: Maximum time allowed for a single 'n' iteration before skipping (default 300s = 5 mins)
    """
    gen_types = ['S', 'T', 'T_coprime', 'T_gcd', 'U_1', 'U_2', 'U_3']
    results = {g: [] for g in gen_types}
    time_elapsed = {g: 0.0 for g in gen_types}
    
    for gen_type in gen_types:
        print(f"\n=======================================================")
        print(f"Starting evaluations for Generator Type: {gen_type}")
        print(f"=======================================================")
        
        gen_start_time = time.time()
        d = 2
        
        # d starts at 2 and continues until 1 hour has elapsed for this generator
        while (time.time() - gen_start_time) < time_per_gen:
            n_min = math.floor(p_min ** d)
            n_max = math.floor(p_max ** d)
            
            print(f"\n--- Dimension {d} | n_range: [{n_min}, {n_max}] ---")
            
            # n runs from p_min**d to p_max**d
            for n in range(n_min, n_max + 1):
                # Check absolute time limit before starting iteration
                if (time.time() - gen_start_time) >= time_per_gen:
                    print(f"[{gen_type}] Time limit reached before processing n={n}. Breaking.")
                    break
                
                max_k = n // 2
                generators = []
                
                # ----------------------------------------------------
                # Generate vectors dynamically based on current gen_type
                # ----------------------------------------------------
                if gen_type == 'S':
                    for k in range(2, max_k + 1):
                        generators.append([(k ** i) % n for i in range(d)])
                        
                elif gen_type in ['T', 'T_coprime', 'T_gcd']:
                    for k_comb in combinations(range(2, max_k + 1), d - 1):
                        vec = [1] + list(k_comb)
                        if gen_type == 'T':
                            generators.append(vec)
                        elif gen_type == 'T_coprime' and is_pairwise_coprime(vec):
                            generators.append(vec)
                        elif gen_type == 'T_gcd' and all(gcd(k, n) == 1 for k in k_comb):
                            generators.append(vec)
                            
                elif gen_type in ['U_1', 'U_2', 'U_3']:
                    for k1, k2 in combinations(range(2, max_k + 1), 2):
                        g1 = np.array([(k1 ** i) % n for i in range(d)])
                        g2 = np.array([(k2 ** i) % n for i in range(d)])
                        
                        if gen_type == 'U_1':
                            generators.append((g1 + g2) % n)
                        elif gen_type == 'U_2':
                            generators.append((g1 - g2) % n)
                        elif gen_type == 'U_3':
                            generators.append([g1, g2])
                
                # ----------------------------------------------------
                # Compute Best Q
                # ----------------------------------------------------
                if gen_type == 'U_3':
                    q, best_g, best_number = get_best_q_vectorized_2d_unique(generators, n)
                    results[gen_type].append((n, d, q, best_g, best_number))
                    print(f"Processed n={n} | Best q: {q} | Unique elements: {best_number}")
                else:
                    q, best_g = get_best_q_vectorized(generators, n)
                    results[gen_type].append((n, d, q, best_g, n))
                    print(f"Processed n={n} | Best q: {q}")
            
            # Increment d when the n-loop is fully processed or broken early
            d += 1
            
        # Log completion metrics for the generator
        total_gen_time = time.time() - gen_start_time
        time_elapsed[gen_type] = total_gen_time
        print(f"Finished {gen_type}. Total time: {total_gen_time:.2f}s")

    return results, time_elapsed

def theta(p,q):
    summ = 0
    for i in range(q):
        multi = 1
        for j in range(1,q):
            c_i = math.cos(2*math.pi*i/q)
            a_j = math.cos(2*math.pi/p*math.floor(j*p/q))
            multi = multi*(c_i-a_j)/(1-a_j)
        summ = summ + multi
    return summ*p/q

if __name__ == "__main__":
    P_MIN = 2
    P_MAX = 6
    
    # Target execution time settings (in seconds)
    # 3600 seconds = 1 hour per generator. 7 generators total = ~7-8 hours.
    TIME_PER_GENERATOR = 3600
    
    print("Starting optimized generator search...")
    
    final_data, time_elapsed = generate_optimal_lattices_time_bounded(
        p_min=P_MIN, 
        p_max=P_MAX, 
        time_per_gen=TIME_PER_GENERATOR,
    )

    results = {
        "final_data": final_data,
        "time_elapsed": time_elapsed
    }
    
    # Optional: Save results to disk incrementally in real runs
    with open('lattice_results.pkl', 'wb') as f:
        pickle.dump(results, f)