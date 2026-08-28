import math
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TYPE_RENAMES = {
    'T_coprime': 'T_pairwise',
    'T_gcd': 'T_cop',
    'U_1': 'U_+',
    'U_2': 'U_-',
    'U_3': 'U_two',
}

TYPE_LABELS = {
    'S': r'S',
    'T': r'T',
    'T_pairwise': r'T_{\mathrm{pairwise}}',
    'T_cop': r'T_{\mathrm{cop}}',
    'U_+': r'U_{+}',
    'U_-': r'U_{-}',
    'U_two': r'U_{2}',
}

P_MIN = 2.0
DEFAULT_P_MAX = 3.1


def rename_type(gen_type):
    return TYPE_RENAMES.get(gen_type, gen_type)


def latex_type_label(gen_type):
    return TYPE_LABELS.get(gen_type, gen_type.replace('_', r'\_'))


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
    final_data = {rename_type(gen_type): type_results for gen_type, type_results in final_data.items()}
    print("Time elapsed per generator type:")
    for i, (gen_type, elapsed) in enumerate(zip(['S', 'T', 'T_pairwise', 'T_cop', 'U_+', 'U_-', 'U_two'], time_elapsed)):
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
                'type': rename_type(gen_type),
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
    types = ['S', 'T', 'T_pairwise', 'T_cop', 'U_+', 'U_-', 'U_two']

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
    dimensions = sorted(df['d'].unique())

    for gen_type in types:
        for d in dimensions:
            mask = (df['type'] == gen_type) & (df['d'] == d)
            subset = df[mask]
            if subset.empty:
                continue
                
            filtered_sub = apply_fast_filter(subset, threshold_col='n_1_over_d', val_col='n_over_q')
            filtered_part1_list.append(filtered_sub)

    if filtered_part1_list:
        df_filtered_part1 = pd.concat(filtered_part1_list, ignore_index=True)
    else:
        df_filtered_part1 = pd.DataFrame(columns=df.columns)

    u2_subset = df_filtered_part1[df_filtered_part1['type'] == 'U_two']
    u2_x_upper_limit = float(u2_subset['n_over_q'].max()) if not u2_subset.empty else DEFAULT_P_MAX
    u2_y_upper_limit = float(u2_subset['n_1_over_d'].max()) if not u2_subset.empty else DEFAULT_P_MAX
    theta_upper_limit = max(DEFAULT_P_MAX, u2_x_upper_limit)
    t = np.round(np.arange(P_MIN, theta_upper_limit + 0.001, 0.01), 2)
    theta_n = np.array([theta(round(value * 100), 100) for value in t])

    def plot_axis_limits(gen_type, subset_type):
        if gen_type == 'U_two' and not subset_type.empty:
            return float(subset_type['n_over_q'].max())
        return DEFAULT_P_MAX

    def plot_generator_type(ax, gen_type, x_upper_limit=None, y_upper_limit=None):
        subset_type = df_filtered_part1[df_filtered_part1['type'] == gen_type]
        if subset_type.empty:
            ax.set_axis_off()
            return

        for d in dimensions:
            subset_d = subset_type[subset_type['d'] == d]
            if not subset_d.empty:
                ax.step(subset_d['n_over_q'], subset_d['n_1_over_d'],
                        where='post', label=rf'$d = {d}$', marker='o', markersize=4)

        xy_max = plot_axis_limits(gen_type, subset_type)
        x_limit = xy_max if x_upper_limit is None else x_upper_limit
        y_limit = xy_max if y_upper_limit is None else y_upper_limit
        ax.plot(t, theta_n, 'r--', linewidth=2, label=r'$\mathrm{Lovasz\ theta}$')
        ax.set_title(r'$\mathrm{Generator\ Type:}$ ' + rf'${latex_type_label(gen_type)}$')
        ax.set_xlabel(r'$p / q$')
        ax.set_ylabel(r'$p^{1/d}$')
        ax.set_xlim(P_MIN, x_limit)
        ax.set_ylim(P_MIN, y_limit)
        ax.legend()

    def plot_all_types(ax, x_upper_limit=DEFAULT_P_MAX, y_upper_limit=DEFAULT_P_MAX, title_range='[2,3]'):
        markers = ['s', 'D', 'o', '^', 'v', '>', '<', 'p', '*', 'h']
        for gen_type in types:
            subset_type = df_filtered_part2[df_filtered_part2['type'] == gen_type]
            if not subset_type.empty:
                ax.step(subset_type['n_over_q'], subset_type['n_1_over_d'],
                        where='post', label=rf'${latex_type_label(gen_type)}$',
                        marker=markers[types.index(gen_type)],
                        markersize=8 - 0.5 * types.index(gen_type))

        ax.plot(t, theta_n, 'r--', linewidth=2, label=r'$\mathrm{Lovasz\ theta}$')
        ax.set_title(r'$\mathrm{All\ Generator\ Types\ for\ ' + title_range + r'}$' + '\n' +
                     r'$\mathrm{Filtered\ across\ all\ dimensions}$')
        ax.set_xlabel(r'$p / q$')
        ax.set_ylabel(r'$p^{1/d}$')
        ax.set_xlim(P_MIN, x_upper_limit)
        ax.set_ylim(P_MIN, y_upper_limit)
        ax.legend()

    # Figure 1: S and U_2 side by side
    fig1, axes1 = plt.subplots(1, 2, figsize=(16, 6), sharex=False, sharey=False)
    plot_generator_type(axes1[0], 'S')
    plot_generator_type(axes1[1], 'U_two')
    fig1.tight_layout()
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

    # Figure 2: all types as-is and with extended axes
    fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6), sharex=False, sharey=False)
    plot_all_types(axes2[0], DEFAULT_P_MAX, DEFAULT_P_MAX, title_range='[2,3]')
    plot_all_types(axes2[1], 9.1, 9.1, title_range='[2,9]')
    fig2.tight_layout()
    plt.show()

    # ==========================================
    # 5. CALCULATE PERCENTAGE DOMINANCE IN [2, 6]
    # ==========================================
    interval_start = 2.0
    interval_end = 3.0
    interval_len = interval_end - interval_start

    percentage = {gen: 0.0 for gen in types}
    unique_percentage = {gen: 0.0 for gen in types}  # Tracks when a gen is strictly > all others

    # 1. Get all unique 'x' points (events) strictly inside the interval (2.0, 6.0]
    mask = (df_filtered_part2['n_over_q'] > interval_start) & (df_filtered_part2['n_over_q'] <= interval_end)
    event_xs = sorted(df_filtered_part2.loc[mask, 'n_over_q'].unique())

    # Ensure the interval calculation strictly closes exactly at 6.0
    if not event_xs or event_xs[-1] != interval_end:
        event_xs.append(interval_end)

    # 2. Initialize current_y for each generator at x = 2.0
    current_y = {}
    for gen in types:
        # Find points <= 2.0 to establish the starting y-value
        subset = df_filtered_part2[(df_filtered_part2['type'] == gen) & (df_filtered_part2['n_over_q'] <= interval_start)]
        if not subset.empty:
            current_y[gen] = subset['n_1_over_d'].max()
        else:
            current_y[gen] = 0.0  # Default floor based on your P_MIN

    # 3. Sweep through the intervals segment by segment
    current_x = interval_start

    for next_x in event_xs:
        # Find the highest y-value in the current segment [current_x, next_x)
        max_y = max(current_y.values())

        # Find which generator(s) achieve this max
        best_gens = [gen for gen, y_val in current_y.items() if y_val == max_y]
        segment_fraction = (next_x - current_x) / interval_len

        # Add to standard percentage (handles ties)
        for gen in best_gens:
            percentage[gen] += segment_fraction

        # Add to unique percentage ONLY if there are no ties
        if len(best_gens) == 1:
            unique_percentage[best_gens[0]] += segment_fraction

        # Process new data points exactly at next_x to update current_y for the *next* segment
        new_points = df_filtered_part2[df_filtered_part2['n_over_q'] == next_x]
        for _, row in new_points.iterrows():
            gen = row['type']
            y_val = row['n_1_over_d']
            # Step function only goes up based on your Pareto filter
            if y_val > current_y[gen]:
                current_y[gen] = y_val

        current_x = next_x

    # Print the final results
    print(f"\nDominance of interval p/q in [{interval_start}, {interval_end}]:")
    print(f"{'Generator':<15} | {'Best (inc. ties)':<20} | {'Uniquely Best':<20}")
    print("-" * 60)
    for gen in types:
        print(f"{gen:<15} | {percentage[gen]:>19.2%} | {unique_percentage[gen]:>19.2%}")