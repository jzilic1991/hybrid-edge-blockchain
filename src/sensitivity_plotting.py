import pandas as pd
import matplotlib.pyplot as plt
import os
from io import StringIO

# --- Configuration Variables for Plotting ---
# A readable font size for the simple annotations.
ANNOTATION_FONTSIZE = 14
# The vertical distance (in points) to place the label above the data marker.
ANNOTATION_XYTEXT_OFFSET_Y = 8
TITLE_FONTSIZE = 14
AXIS_LABEL_FONTSIZE = 14
TICK_LABEL_FONTSIZE = 14
LEGEND_FONTSIZE = 14
FIGURE_WIDTH = 24
FIGURE_HEIGHT = 7

# Folder and app configurations
results_dir = "fresco_sensitivity/"
apps = ["random"]
output_dir = "fresco_sensitivity/"
os.makedirs(output_dir, exist_ok=True)

for app in apps:
    file_path = os.path.join(results_dir, f"{app}.csv")
    if not os.path.exists(file_path):
        print(f"⚠️ File not found for app: {app}")
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
    gammas_to_plot = [0.2, 0.4, 0.6]

    # ==================================================================
    #                       SCORE PLOTS
    # ==================================================================
    fig_score, axes_score = plt.subplots(1, 3, figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))

    # === Plot 1 (Score): Score vs Alpha ===
    ax0_score = axes_score[0]
    for beta_fixed in betas:
        subset = df[df["beta"] == beta_fixed].sort_values("alpha")
        ax0_score.plot(subset["alpha"], subset["score"], label=f"β={beta_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax0_score.annotate(f"γ={row['gamma']:.2f}",
                               (row["alpha"], row["score"]),
                               textcoords="offset points",
                               xytext=(0, ANNOTATION_XYTEXT_OFFSET_Y),
                               ha='center',
                               fontsize=ANNOTATION_FONTSIZE)
    ax0_score.set_title("Score vs Alpha (Lines: β, Label: γ)", fontsize=TITLE_FONTSIZE)

    # === Plot 2 (Score): Score vs Beta ===
    ax1_score = axes_score[1]
    for alpha_fixed in alphas:
        subset = df[df["alpha"] == alpha_fixed].sort_values("beta")
        ax1_score.plot(subset["beta"], subset["score"], label=f"α={alpha_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax1_score.annotate(f"γ={row['gamma']:.2f}",
                               (row["beta"], row["score"]),
                               textcoords="offset points",
                               xytext=(0, ANNOTATION_XYTEXT_OFFSET_Y),
                               ha='center',
                               fontsize=ANNOTATION_FONTSIZE)
    ax1_score.set_title("Score vs Beta (Lines: α, Label: γ)", fontsize=TITLE_FONTSIZE)

    # === Plot 3 (Score): Score vs Alpha ===
    ax2_score = axes_score[2]
    for gamma_fixed in gammas:
        subset = df[df["gamma"] == gamma_fixed].sort_values("alpha")
        ax2_score.plot(subset["alpha"], subset["score"], label=f"γ={gamma_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax2_score.annotate(f"β={row['beta']:.2f}",
                               (row["alpha"], row["score"]),
                               textcoords="offset points",
                               xytext=(0, ANNOTATION_XYTEXT_OFFSET_Y),
                               ha='center',
                               fontsize=ANNOTATION_FONTSIZE)
    ax2_score.set_title("Score vs Alpha (Lines: γ, Label: β)", fontsize=TITLE_FONTSIZE)

    # --- Finalize Score Plots ---
    for ax in axes_score:
        ax.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONTSIZE)
        ax.legend(fontsize=LEGEND_FONTSIZE)
        if "Alpha" in ax.get_title():
            ax.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
        else:
            ax.set_xlabel("Beta", fontsize=AXIS_LABEL_FONTSIZE)
        ax.set_ylabel("Score", fontsize=AXIS_LABEL_FONTSIZE)
        
    plt.tight_layout()
    output_score_file = os.path.join(output_dir, f"fresco_score_sensitivity_{app}.png")
    plt.savefig(output_score_file, dpi=300)
    plt.close(fig_score)
    print(f"Score plot saved: {output_score_file}")


    # ==================================================================
    #                  OBJECTIVE FEATURE PLOTS
    # ==================================================================
    fig_objectives, axes_objectives = plt.subplots(1, 3, figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))

    # === Plot 1 (Objectives): Latency vs Alpha ===
    ax0_obj = axes_objectives[0]
    for beta_fixed in betas:
        subset = df[df["beta"] == beta_fixed].sort_values("alpha")
        ax0_obj.plot(subset["alpha"], subset["latency"], label=f"β={beta_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax0_obj.annotate(f"γ={row['gamma']:.2f}",
                             (row["alpha"], row["latency"]),
                             textcoords="offset points",
                             xytext=(0, ANNOTATION_XYTEXT_OFFSET_Y),
                             ha='center',
                             fontsize=ANNOTATION_FONTSIZE)
    ax0_obj.set_title("Latency vs Alpha (Lines: β, Label: γ)", fontsize=TITLE_FONTSIZE)
    ax0_obj.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
    ax0_obj.set_ylabel("Latency", fontsize=AXIS_LABEL_FONTSIZE)

    # === Plot 2 (Objectives): Energy vs Beta ===
    ax1_obj = axes_objectives[1]
    for alpha_fixed in alphas:
        subset = df[df["alpha"] == alpha_fixed].sort_values("beta")
        ax1_obj.plot(subset["beta"], subset["energy"], label=f"α={alpha_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax1_obj.annotate(f"γ={row['gamma']:.2f}",
                             (row["beta"], row["energy"]),
                             textcoords="offset points",
                             xytext=(0, ANNOTATION_XYTEXT_OFFSET_Y),
                             ha='center',
                             fontsize=ANNOTATION_FONTSIZE)
    ax1_obj.set_title("Energy vs Beta (Lines: α, Label: γ)", fontsize=TITLE_FONTSIZE)
    ax1_obj.set_xlabel("Beta", fontsize=AXIS_LABEL_FONTSIZE)
    ax1_obj.set_ylabel("Energy", fontsize=AXIS_LABEL_FONTSIZE)

    # === Plot 3 (Objectives): Cost vs Alpha ===
    ax2_obj = axes_objectives[2]
    for gamma_fixed in gammas:
        subset = df[df["gamma"] == gamma_fixed].sort_values("alpha")
        ax2_obj.plot(subset["alpha"], subset["cost"], label=f"γ={gamma_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax2_obj.annotate(f"β={row['beta']:.2f}",
                             (row["alpha"], row["cost"]),
                             textcoords="offset points",
                             xytext=(0, ANNOTATION_XYTEXT_OFFSET_Y),
                             ha='center',
                             fontsize=ANNOTATION_FONTSIZE)
    ax2_obj.set_title("Cost vs Alpha (Lines: γ, Label: β)", fontsize=TITLE_FONTSIZE)
    ax2_obj.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
    ax2_obj.set_ylabel("Cost", fontsize=AXIS_LABEL_FONTSIZE)

    # --- Finalize Objective Plots ---
    for ax in axes_objectives:
        ax.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONTSIZE)
        ax.legend(fontsize=LEGEND_FONTSIZE)
        
    plt.tight_layout()
    output_objectives_file = os.path.join(output_dir, f"fresco_objective_sensitivity_{app}.png")
    plt.savefig(output_objectives_file, dpi=300)
    plt.close(fig_objectives)
    print(f"Objective features plot saved: {output_objectives_file}")

    # ==================================================================
    #          GAMMA FIXED SUBPLOTS (γ = 0.2, 0.4, 0.6)
    # ==================================================================
    fig_gamma, axes_gamma = plt.subplots(len(gammas_to_plot), 3,
                                         figsize=(FIGURE_WIDTH, FIGURE_HEIGHT * len(gammas_to_plot)))

    for idx, gamma_fixed in enumerate(gammas_to_plot):
        df_gamma = df[df["gamma"] == gamma_fixed]
        if df_gamma.empty:
            continue

        # --------------------------------------------------
        # Latency vs Alpha — connect all data visually
        # --------------------------------------------------
        ax_lat = axes_gamma[idx, 0]
        df_sorted = df_gamma.sort_values("alpha")
        ax_lat.plot(df_sorted["alpha"], df_sorted["latency"],
                    label=f"γ={gamma_fixed:.1f}", marker='o')
        for _, row in df_sorted.iterrows():
            ax_lat.annotate(f"β={row['beta']:.1f}",
                            (row["alpha"], row["latency"]),
                            textcoords="offset points", xytext=(0, 5),
                            ha='center', fontsize=ANNOTATION_FONTSIZE)
        ax_lat.set_title(f"Latency vs Alpha (γ={gamma_fixed:.1f})", fontsize=TITLE_FONTSIZE)
        ax_lat.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
        ax_lat.set_ylabel("Latency", fontsize=AXIS_LABEL_FONTSIZE)

        # --------------------------------------------------
        # Energy vs Beta — connect all data visually
        # --------------------------------------------------
        ax_energy = axes_gamma[idx, 1]
        df_sorted = df_gamma.sort_values("beta")
        ax_energy.plot(df_sorted["beta"], df_sorted["energy"],
                       label=f"γ={gamma_fixed:.1f}", marker='o')
        for _, row in df_sorted.iterrows():
            ax_energy.annotate(f"β={row['beta']:.1f}",
                               (row["beta"], row["energy"]),
                               textcoords="offset points", xytext=(0, 5),
                               ha='center', fontsize=ANNOTATION_FONTSIZE)
        ax_energy.set_title(f"Energy vs Beta (γ={gamma_fixed:.1f})", fontsize=TITLE_FONTSIZE)
        ax_energy.set_xlabel("Beta", fontsize=AXIS_LABEL_FONTSIZE)
        ax_energy.set_ylabel("Energy", fontsize=AXIS_LABEL_FONTSIZE)

        # --------------------------------------------------
        # Cost vs Alpha — connect all data visually
        # --------------------------------------------------
        ax_cost = axes_gamma[idx, 2]
        df_sorted = df_gamma.sort_values("alpha")
        ax_cost.plot(df_sorted["alpha"], df_sorted["cost"],
                     label=f"γ={gamma_fixed:.1f}", marker='o')
        for _, row in df_sorted.iterrows():
            ax_cost.annotate(f"β={row['beta']:.1f}",
                             (row["alpha"], row["cost"]),
                             textcoords="offset points", xytext=(0, 5),
                             ha='center', fontsize=ANNOTATION_FONTSIZE)
        ax_cost.set_title(f"Cost vs Alpha (γ={gamma_fixed:.1f})", fontsize=TITLE_FONTSIZE)
        ax_cost.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
        ax_cost.set_ylabel("Cost", fontsize=AXIS_LABEL_FONTSIZE)

        # Common styling
        for ax in axes_gamma[idx]:
            ax.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONTSIZE)
            ax.legend(fontsize=LEGEND_FONTSIZE)

    plt.tight_layout()
    output_gamma_file = os.path.join(output_dir, f"fresco_gamma_fixed_{app}.png")
    plt.savefig(output_gamma_file, dpi=300)
    plt.close(fig_gamma)
    print(f"Gamma fixed plots saved: {output_gamma_file}")

