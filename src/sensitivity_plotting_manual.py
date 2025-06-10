import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import os

# --- Configuration Variables for Plotting ---
ANNOTATION_FONTSIZE = 14
TITLE_FONTSIZE = 14
AXIS_LABEL_FONTSIZE = 14
TICK_LABEL_FONTSIZE = 14
LEGEND_FONTSIZE = 12
FIGURE_WIDTH = 24
FIGURE_HEIGHT = 7

# --- File and Directory Configuration ---
results_dir = "fresco_sensitivity/"
apps = ["random"]
output_dir = "fresco_sensitivity/"
os.makedirs(output_dir, exist_ok=True)

for app in apps:
    file_path = os.path.join(results_dir, f"{app}.csv")
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        continue

    df = pd.read_csv(file_path)
    df.columns = [
        "suffix", "alpha", "beta", "gamma", "k",
        "latency", "energy", "cost", "dec_time",
        "qos_violation", "score"
    ]

    betas = sorted(df["beta"].unique())
    alphas = sorted(df["alpha"].unique())
    gammas = sorted(df["gamma"].unique())

    # ==================================================================
    #                  OBJECTIVE FEATURE PLOTS
    # ==================================================================
    fig_objectives, axes_objectives = plt.subplots(1, 3, figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
    ax0_obj, ax1_obj, ax2_obj = axes_objectives

    # === Plot 1 (Objectives): Latency vs Alpha (Your Finalized Version) ===
    cluster_alphas_p1 = [0.0, 0.2, 0.4, 0.6, 0.8]
    latency_threshold_p1 = 25
    label_positions_p1 = {0.0: (0, -25), 0.2: (5, 25), 0.4: (30, -25), 0.6: (15, 20), 0.8: (30, -25)}

    for beta_fixed in betas:
        subset = df[df["beta"] == beta_fixed].sort_values("alpha")
        ax0_obj.plot(subset["alpha"], subset["latency"], label=f"β={beta_fixed:.2f}", marker='o', markersize=4, zorder=2)
        for _, row in subset.iterrows():
            if (row['alpha'] in cluster_alphas_p1 and row['latency'] > latency_threshold_p1) or (row['alpha'] not in cluster_alphas_p1):
                ax0_obj.annotate(f"γ={row['gamma']:.2f}", (row["alpha"], row["latency"]), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=ANNOTATION_FONTSIZE)

    for alpha_val in cluster_alphas_p1:
        cluster_df = df[(df['alpha'] == alpha_val) & (df['latency'] < latency_threshold_p1)]
        if not cluster_df.empty:
            center_x, center_y = cluster_df['alpha'].mean(), cluster_df['latency'].mean()
            height, width = (cluster_df['latency'].max() - cluster_df['latency'].min()) + 2, 0.12
            ax0_obj.add_patch(Ellipse(xy=(center_x, center_y), width=width, height=height, edgecolor='gray', fc='None', lw=1.5, linestyle='--', zorder=3))
            sorted_cluster = cluster_df.sort_values('latency', ascending=False)
            gamma_values = sorted_cluster['gamma'].tolist()
            label_text = f"γ: [{min(gamma_values):.2f} - {max(gamma_values):.2f}]" if len(gamma_values) > 3 else f"γ: {{{', '.join([f'{g:.2f}' for g in gamma_values])}}}"
            ax0_obj.annotate(label_text, (center_x, center_y), xytext=label_positions_p1.get(alpha_val, (0,0)), textcoords='offset points', ha='center', va='center', fontsize=14, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec='None', alpha=0.7))

    ax0_obj.set_title("Latency vs Alpha (Lines: β, Label: γ)", fontsize=TITLE_FONTSIZE)
    ax0_obj.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
    ax0_obj.set_ylabel("Latency", fontsize=AXIS_LABEL_FONTSIZE)

    # === Plot 2 (Objectives): Energy vs Beta (Your Finalized Version) ===
    cluster_betas_p2 = [0.0, 0.2, 0.4, 0.6, 0.8]
    energy_threshold_p2 = 15
    label_positions_p2 = {0.0: (25, -35), 0.2: (0, 40), 0.4: (0, -30), 0.6: (0, 25), 0.8: (0, -25)}

    for alpha_fixed in alphas:
        subset = df[df["alpha"] == alpha_fixed].sort_values("beta")
        ax1_obj.plot(subset["beta"], subset["energy"], label=f"α={alpha_fixed:.2f}", marker='o', markersize=4, zorder=2)
        for _, row in subset.iterrows():
            if (row['beta'] in cluster_betas_p2 and row['energy'] > energy_threshold_p2) or (row['beta'] not in cluster_betas_p2):
                ax1_obj.annotate(f"γ={row['gamma']:.2f}", (row["beta"], row["energy"]), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=ANNOTATION_FONTSIZE)

    for beta_val in cluster_betas_p2:
        cluster_df = df[(df['beta'] == beta_val) & (df['energy'] < energy_threshold_p2)]
        if not cluster_df.empty:
            center_x, center_y = cluster_df['beta'].mean(), cluster_df['energy'].mean()
            height, width = (cluster_df['energy'].max() - cluster_df['energy'].min()) + 2, 0.12
            ax1_obj.add_patch(Ellipse(xy=(center_x, center_y), width=width, height=height, edgecolor='gray', fc='None', lw=1.5, linestyle='--', zorder=3))
            sorted_cluster = cluster_df.sort_values('energy', ascending=False)
            gamma_values = sorted_cluster['gamma'].tolist()
            label_text = f"γ: [{min(gamma_values):.2f} - {max(gamma_values):.2f}]" if len(gamma_values) > 3 else f"γ: {{{', '.join([f'{g:.2f}' for g in gamma_values])}}}"
            ax1_obj.annotate(label_text, (center_x, center_y), xytext=label_positions_p2.get(beta_val, (0,0)), textcoords='offset points', ha='center', va='center', fontsize=14, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec='None', alpha=0.7))

    ax1_obj.set_title("Energy vs Beta (Lines: α, Label: γ)", fontsize=TITLE_FONTSIZE)
    ax1_obj.set_xlabel("Beta", fontsize=AXIS_LABEL_FONTSIZE)
    ax1_obj.set_ylabel("Energy", fontsize=AXIS_LABEL_FONTSIZE)

    # === Plot 3 (Objectives): Cost vs Alpha (HYBRID LOGIC) ===
    # 1. Your manual definitions for dense, low-cost clusters
    dense_cluster_alphas_p3 = [0, 0.2, 0.4]
    cost_threshold_p3 = 80
    label_positions_p3 = {0: (5, -30), 0.2: (0, 45), 0.4: (0, -35)}
    
    # 2. New explicit definitions for the high-cost, two-point clusters
    explicit_clusters_p3 = [
        {'alpha': 0.6, 'gammas': [0.0, 0.2], 'label_pos': (0, -25)},
        {'alpha': 0.8, 'gammas': [0.0, 0.2], 'label_pos': (0, 25)}
    ]
    # Create a lookup set for all points that will be handled by the explicit logic
    explicit_points_to_skip = set()
    for c in explicit_clusters_p3:
        for g in c['gammas']:
            explicit_points_to_skip.add((c['alpha'], g))

    # --- Plotting loop for Plot 3 ---
    for gamma_fixed in gammas:
        subset = df[df["gamma"] == gamma_fixed].sort_values("alpha")
        ax2_obj.plot(subset["alpha"], subset["cost"], label=f"γ={gamma_fixed:.2f}", marker='o', markersize=4, zorder=2)
        for _, row in subset.iterrows():
            # Determine if the point belongs to any defined cluster
            is_in_dense_cluster = (row['alpha'] in dense_cluster_alphas_p3 and row['cost'] < cost_threshold_p3)
            is_in_explicit_cluster = (row['alpha'], row['gamma']) in explicit_points_to_skip
            
            # Annotate a point ONLY if it's NOT in ANY cluster
            if not is_in_dense_cluster and not is_in_explicit_cluster:
                 ax2_obj.annotate(f"β={row['beta']:.2f}", (row["alpha"], row["cost"]), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=ANNOTATION_FONTSIZE)

    # --- Process and draw YOUR DENSE CLUSTERS ---
    for alpha_val in dense_cluster_alphas_p3:
        cluster_df = df[(df['alpha'] == alpha_val) & (df['cost'] < cost_threshold_p3)]
        if not cluster_df.empty:
            center_x, center_y = cluster_df['alpha'].mean(), cluster_df['cost'].mean()
            height, width = (cluster_df['cost'].max() - cluster_df['cost'].min()) + 15, 0.12
            ax2_obj.add_patch(Ellipse(xy=(center_x, center_y), width=width, height=height, edgecolor='gray', fc='None', lw=1.5, linestyle='--', zorder=3))
            sorted_cluster = cluster_df.sort_values('cost', ascending=False)
            beta_values = sorted_cluster['beta'].tolist()
            label_text = f"β: [{min(beta_values):.2f} - {max(beta_values):.2f}]" if len(beta_values) > 3 else f"β: {{{', '.join([f'{b:.2f}' for b in beta_values])}}}"
            ax2_obj.annotate(label_text, (center_x, center_y), xytext=label_positions_p3.get(alpha_val, (0,0)), textcoords='offset points', ha='center', va='center', fontsize=14, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec='None', alpha=0.7))

    # --- Process and draw the NEW EXPLICIT CLUSTERS ---
    for cluster_info in explicit_clusters_p3:
        cluster_df = df[(df['alpha'] == cluster_info['alpha']) & (df['gamma'].isin(cluster_info['gammas']))]
        if not cluster_df.empty:
            center_x, center_y = cluster_df['alpha'].mean(), cluster_df['cost'].mean()
            height = max((cluster_df['cost'].max() - cluster_df['cost'].min()), 5) + 5
            width = 0.12
            ax2_obj.add_patch(Ellipse(xy=(center_x, center_y), width=width, height=height, edgecolor='gray', fc='None', lw=1.5, linestyle='--', zorder=3))
            sorted_cluster = cluster_df.sort_values('cost', ascending=False)
            beta_values = sorted_cluster['beta'].tolist()
            label_text = f"β: {{{', '.join([f'{b:.2f}' for b in beta_values])}}}" # Always a set for these
            ax2_obj.annotate(label_text, (center_x, center_y), xytext=cluster_info['label_pos'], textcoords='offset points', ha='center', va='center', fontsize=14, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec='None', alpha=0.7))

    ax2_obj.set_title("Cost vs Alpha (Lines: γ, Label: β)", fontsize=TITLE_FONTSIZE)
    ax2_obj.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
    ax2_obj.set_ylabel("Cost", fontsize=AXIS_LABEL_FONTSIZE)
    
    # --- Finalize Plots ---
    for ax in axes_objectives:
        ax.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONTSIZE)
        ax.legend(fontsize=LEGEND_FONTSIZE)

    plt.tight_layout()
    output_filename = f"fresco_objective_sensitivity_{app}.png"
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, dpi=300)
    plt.close(fig_objectives)
    print(f"Objective features plot saved to: {output_path}")
