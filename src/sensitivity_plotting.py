import pandas as pd
import matplotlib.pyplot as plt
import os
from io import StringIO
from util import Settings

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
FIGURE_HEIGHT = 5  # landscape orientation
REFERENCE_LINE_WIDTH = 4
REFERENCE_LINE_COLOR = "grey"

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
    # Compute battery lifetime (percentage of remaining capacity)
    df["battery_lifetime"] = (1 - df["energy"] / Settings.BATTERY_LF) * 100

    betas = sorted(df["beta"].unique())
    alphas = sorted(df["alpha"].unique())
    gammas = sorted(df["gamma"].unique())
    gammas_to_plot = [0.2, 0.4, 0.6]

    best_latency = df["latency"].min()
    best_cost = df["cost"].min()
    best_battery = df["battery_lifetime"].max()

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
    ax0_score.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)


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
    ax1_score.set_xlabel("Beta", fontsize=AXIS_LABEL_FONTSIZE)


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
    ax2_score.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)


    # --- Finalize Score Plots ---
    for ax in axes_score:
        ax.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONTSIZE)
        ax.legend(fontsize=LEGEND_FONTSIZE)
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
    ax0_obj.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
    ax0_obj.set_ylabel("Latency (ms)", fontsize=AXIS_LABEL_FONTSIZE)
    ax0_obj.axhline(
        best_latency,
        color=REFERENCE_LINE_COLOR,
        linestyle="--",
        linewidth=REFERENCE_LINE_WIDTH,
    )
    ax0_obj.annotate(
        f"{best_latency:.2f} ms",
        xy=(ax0_obj.get_xlim()[1], best_latency),
        xytext=(5, 0),
        textcoords="offset points",
        va="center",
        fontsize=ANNOTATION_FONTSIZE,
        color=REFERENCE_LINE_COLOR,
    )

    # === Plot 2 (Objectives): Cost vs Alpha ===
    ax1_obj = axes_objectives[1]
    for alpha_fixed in alphas:
        subset = df[df["alpha"] == alpha_fixed].sort_values("alpha")
        ax1_obj.plot(subset["alpha"], subset["cost"], label=f"α={alpha_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax1_obj.annotate(
                f"γ={row['gamma']:.2f}",
                (row["alpha"], row["cost"]),
                textcoords="offset points",
                xytext=(0, ANNOTATION_XYTEXT_OFFSET_Y),
                ha='center',
                fontsize=ANNOTATION_FONTSIZE,
            )
    ax1_obj.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
    ax1_obj.set_ylabel("Cost ($)", fontsize=AXIS_LABEL_FONTSIZE)
    ax1_obj.axhline(
        best_cost,
        color=REFERENCE_LINE_COLOR,
        linestyle="--",
        linewidth=REFERENCE_LINE_WIDTH,
    )
    ax1_obj.annotate(
        f"${best_cost:.2f}",
        xy=(ax1_obj.get_xlim()[1], best_cost),
        xytext=(5, 0),
        textcoords="offset points",
        va="center",
        fontsize=ANNOTATION_FONTSIZE,
        color=REFERENCE_LINE_COLOR,
    )

    # === Plot 3 (Objectives): Battery Lifetime vs Beta ===
    ax2_obj = axes_objectives[2]
    for gamma_fixed in gammas:
        subset = df[df["gamma"] == gamma_fixed].sort_values("beta")
        ax2_obj.plot(subset["beta"], subset["battery_lifetime"], label=f"γ={gamma_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax2_obj.annotate(f"β={row['beta']:.2f}",
                             (row["beta"], row["battery_lifetime"]),
                             textcoords="offset points",
                             xytext=(0, ANNOTATION_XYTEXT_OFFSET_Y),
                             ha='center',
                             fontsize=ANNOTATION_FONTSIZE)
    ax2_obj.set_xlabel("Beta", fontsize=AXIS_LABEL_FONTSIZE)
    ax2_obj.set_ylabel("Battery lifetime (%)", fontsize=AXIS_LABEL_FONTSIZE)
    ax2_obj.axhline(
        best_battery,
        color=REFERENCE_LINE_COLOR,
        linestyle="--",
        linewidth=REFERENCE_LINE_WIDTH,
    )
    ax2_obj.annotate(
        f"{best_battery:.2f}%",
        xy=(ax2_obj.get_xlim()[1], best_battery),
        xytext=(5, 0),
        textcoords="offset points",
        va="center",
        fontsize=ANNOTATION_FONTSIZE,
        color=REFERENCE_LINE_COLOR,
    )

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
        ax_lat.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
        ax_lat.set_ylabel("Latency (ms)", fontsize=AXIS_LABEL_FONTSIZE)
        if idx == 0:
          ax_lat.set_ylim(bottom=7.5)
        else:
          ax_lat.set_ylim(bottom=0)
        ax_lat.axhline(
            best_latency,
            color=REFERENCE_LINE_COLOR,
            linestyle="--",
            linewidth=REFERENCE_LINE_WIDTH,
        )
        ax_lat.annotate(
            f"{best_latency:.2f} ms",
            xy=(ax_lat.get_xlim()[1], best_latency),
            xytext=(-60, 10),
            textcoords="offset points",
            va="center",
            fontsize=ANNOTATION_FONTSIZE,
            color="black",
        )

        # --------------------------------------------------
        # Cost vs Alpha — connect all data visually
        # --------------------------------------------------
        ax_cost = axes_gamma[idx, 1]
        df_sorted = df_gamma.sort_values("alpha")
        ax_cost.plot(df_sorted["alpha"], df_sorted["cost"],
                     label=f"γ={gamma_fixed:.1f}", marker='o')
        for _, row in df_sorted.iterrows():
            ax_cost.annotate(f"β={row['beta']:.1f}",
                             (row["alpha"], row["cost"]),
                             textcoords="offset points", xytext=(0, 5),
                             ha='center', fontsize=ANNOTATION_FONTSIZE)
        ax_cost.set_xlabel("Alpha", fontsize=AXIS_LABEL_FONTSIZE)
        ax_cost.set_ylabel("Cost ($)", fontsize=AXIS_LABEL_FONTSIZE)
        if idx == 0:
            ax_cost.set_ylim(bottom=-10)
        elif idx == 1:
            ax_cost.set_ylim(bottom=-2)
        elif idx == 2:
            ax_cost.set_ylim(bottom=-0.2)

        ax_cost.axhline(
            best_cost,
            color=REFERENCE_LINE_COLOR,
            linestyle="--",
            linewidth=REFERENCE_LINE_WIDTH,
        )
        ax_cost.annotate(
            f"${best_cost:.2f}",
            xy=(ax_cost.get_xlim()[1], best_cost),
            xytext=(-50, 10),
            textcoords="offset points",
            va="center",
            fontsize=ANNOTATION_FONTSIZE,
            color="black",
        )
        # --------------------------------------------------
        # Battery Lifetime vs Beta — connect all data visually
        # --------------------------------------------------
        ax_energy = axes_gamma[idx, 2]
        df_sorted = df_gamma.sort_values("beta")
        ax_energy.plot(
            df_sorted["beta"],
            df_sorted["battery_lifetime"],
            label=f"γ={gamma_fixed:.1f}",
            marker="o",
        )
        for _, row in df_sorted.iterrows():
            ax_energy.annotate(
                f"α={row['alpha']:.1f}",
                (row["beta"], row["battery_lifetime"]),
                textcoords="offset points",
                xytext=(0, 5),
                ha="center",
                fontsize=ANNOTATION_FONTSIZE,
            )
        ax_energy.set_xlabel("Beta", fontsize=AXIS_LABEL_FONTSIZE)
        ax_energy.set_ylabel("Battery lifetime (%)", fontsize=AXIS_LABEL_FONTSIZE)
        ax_energy.axhline(
            best_battery,
            color=REFERENCE_LINE_COLOR,
            linestyle="--",
            linewidth=REFERENCE_LINE_WIDTH,
        )
        ax_energy.annotate(
            f"{best_battery:.2f}%",
            xy=(ax_energy.get_xlim()[1], best_battery),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            fontsize=ANNOTATION_FONTSIZE,
            color="black",
        )

        # Common styling
        for ax in axes_gamma[idx]:
            ax.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONTSIZE)
            ax.legend(fontsize=LEGEND_FONTSIZE)

    plt.tight_layout()
    output_gamma_file = os.path.join(output_dir, f"fresco_gamma_fixed_{app}.png")
    plt.savefig(output_gamma_file, dpi=300)
    plt.close(fig_gamma)
    print(f"Gamma fixed plots saved: {output_gamma_file}")

