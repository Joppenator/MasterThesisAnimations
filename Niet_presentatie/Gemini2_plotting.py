import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import math

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
    with open("results.pkl", "rb") as f:
        results = pickle.load(f)

    final_data = results["final_data"]
    time_elapsed = results["time_elapsed"]
    print("Time elapsed per generator type:")
    for i, (gen_type, elapsed) in enumerate(zip(['S', 'T', 'T_pairwise', 'T_cop', 'U_+', 'U_-', 'U_2'], time_elapsed)):
        print(f"  {gen_type}: {elapsed:.2f} seconds")
    print(f"Total time elapsed: {sum(time_elapsed):.2f} seconds")
    # ==========================================
    # 1. CONVERT final_data TO PANDAS DATAFRAME
    # ==========================================
    # (Assuming 'final_data' is already in memory from the previous script)
    rows = []
    for gen_type, results in final_data.items():
        for row in results:
            n, d, q, best_g, best_number = row
            rows.append({
                'type': gen_type,
                'd': d,
                'n': n,
                'q': q,
                'best_n': best_number,
            })

    df = pd.DataFrame(rows)

    # Filter out q=0 to prevent division by zero errors
    df = df[df['q'] > 0].copy()

    # Add the required derived columns for plotting
    df['n_over_q'] = df['n'] / df['q']
    df['n_1_over_d'] = df['best_n'] ** (1 / df['d'])

    # ==========================================
    # 2. FAST PARETO FILTER FUNCTION
    # ==========================================
    def apply_fast_filter(group_df, threshold_col, val_col='n_over_q'):
        """
        1. Sorts by the threshold column descending.
        2. Keeps only rows where n/q is strictly less than the lowest n/q seen so far.
        """
        sorted_df = group_df.sort_values(by=[threshold_col, val_col], ascending=[False, True])
        cummin = sorted_df[val_col].cummin()
        mask = (sorted_df[val_col] == cummin) & (sorted_df[val_col] < cummin.shift(1).fillna(np.inf))
        return sorted_df[mask].sort_values(by=val_col, ascending=True)

    # ==========================================
    # 3. PART 1: FILTER & PLOT PER DIMENSION
    # ==========================================
    filtered_part1_list = []
    types = df['type'].unique()
    dimensions = sorted(df['d'].unique())

    for gen_type in types:
        for d in dimensions:
            mask = (df['type'] == gen_type) & (df['d'] == d)
            subset = df[mask]
            if subset.empty:
                continue
                
            filtered_sub = apply_fast_filter(subset, threshold_col='n', val_col='n_over_q')
            filtered_part1_list.append(filtered_sub)

    if filtered_part1_list:
        df_filtered_part1 = pd.concat(filtered_part1_list, ignore_index=True)
    else:
        df_filtered_part1 = pd.DataFrame(columns=df.columns)

    #Get lovasz theta function for plotting upper bound
    # First get the p_min and p_max values from the filtered dataframe, which are the min and max of n/q
    P_MIN = math.floor(df_filtered_part1['n_over_q'].min())
    P_MAX = math.ceil(df_filtered_part1['n_over_q'].max())
    t = np.linspace(P_MIN, P_MAX, 100*(P_MAX-P_MIN)+1)
    theta_n = np.zeros(100*(P_MAX-P_MIN)+1)
    for i in range(100*(P_MAX-P_MIN)+1):
        theta_n[i] = theta(int(t[i]*100),100)

    # Plotting Part 1
    for gen_type in types:
        subset_type = df_filtered_part1[df_filtered_part1['type'] == gen_type]
        if subset_type.empty:
            continue
            
        plt.figure(figsize=(10, 6))
        for d in dimensions:
            subset_d = subset_type[subset_type['d'] == d]
            if not subset_d.empty:
                plt.step(subset_d['n_over_q'], subset_d['n_1_over_d'], 
                        where='post', label=f'd = {d}', marker='o', markersize=4)
                if gen_type == 'U_3':
                    print(subset_d['n_over_q'], subset_d['n_1_over_d'])

        plt.plot(t, theta_n, 'r--', linewidth=2, label='Lovász theta')
        plt.title(f'Filtered Set for Generator Type: {gen_type}\n(Filtered by n per dimension)')
        plt.xlabel('n / q')
        plt.ylabel('n ** (1/d)')
        plt.xlim(P_MIN, P_MAX)
        plt.ylim(P_MIN, P_MAX)
        plt.legend(title='Dimension')
        #plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    # ==========================================
    # 4. PART 2: FILTER & PLOT ACROSS ALL DIMENSIONS
    # ==========================================
    filtered_part2_list = []

    for gen_type in types:
        subset = df[df['type'] == gen_type]
        if subset.empty:
            continue
        
        filtered_sub = apply_fast_filter(subset, threshold_col='n_1_over_d', val_col='n_over_q')
        filtered_part2_list.append(filtered_sub)

    if filtered_part2_list:
        df_filtered_part2 = pd.concat(filtered_part2_list, ignore_index=True)
    else:
        df_filtered_part2 = pd.DataFrame(columns=df.columns)

    # Plotting Part 2
    plt.figure(figsize=(10, 6))

    markers = ['s','D','o', '^', 'v', '>', '<', 'p', '*', 'h']  # Extend as needed
    for gen_type in types:
        subset_type = df_filtered_part2[df_filtered_part2['type'] == gen_type]
        if not subset_type.empty:
            plt.step(subset_type['n_over_q'], subset_type['n_1_over_d'], 
                    where='post', label=f'{gen_type}', marker=markers[types.tolist().index(gen_type)], markersize=8-0.5*types.tolist().index(gen_type))

    plt.plot(t, theta_n, 'r--', linewidth=2, label='Lovász theta')
    plt.title('Filtered Set for All Generator Types\n(Filtered by n**(1/d) across all dimensions)')
    plt.xlabel('n / q')
    plt.ylabel('n ** (1/d)')
    plt.xlim(P_MIN, P_MAX)
    plt.ylim(P_MIN, P_MAX)
    plt.legend(title='Generator Type')
    #plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()