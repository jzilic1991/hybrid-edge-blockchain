import pandas as pd
import matplotlib.pyplot as plt
import os

# Folder and app configurations
results_dir = "fresco_sensitivity/"
apps = ["mobiar"]  # Extend to: "intrasafe", "naviar", "random"

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

    fig, axes = plt.subplots(1, 3, figsize=(22, 6))

    # === Plot 1: Score vs Alpha (lines per β, label γ) ===
    betas = sorted(df["beta"].unique())
    ax0 = axes[0]
    for beta_fixed in betas:
        subset = df[df["beta"] == beta_fixed].sort_values("alpha")
        ax0.plot(subset["alpha"], subset["score"], label=f"β={beta_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax0.annotate(f"γ={row['gamma']:.2f}",
                         (row["alpha"], row["score"]),
                         textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)

    ax0.set_title("Score vs Alpha (Lines: β, Label: γ)")
    ax0.set_xlabel("Alpha")
    ax0.set_ylabel("Score")
    ax0.legend()

    # === Plot 2: Score vs Beta (lines per α, label γ) ===
    alphas = sorted(df["alpha"].unique())
    ax1 = axes[1]
    for alpha_fixed in alphas:
        subset = df[df["alpha"] == alpha_fixed].sort_values("beta")
        ax1.plot(subset["beta"], subset["score"], label=f"α={alpha_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax1.annotate(f"γ={row['gamma']:.2f}",
                         (row["beta"], row["score"]),
                         textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)

    ax1.set_title("Score vs Beta (Lines: α, Label: γ)")
    ax1.set_xlabel("Beta")
    ax1.set_ylabel("Score")
    ax1.legend()

    # === Plot 3: Score vs Alpha (lines per γ, label β) ===
    gammas = sorted(df["gamma"].unique())
    ax2 = axes[2]
    for gamma_fixed in gammas:
        subset = df[df["gamma"] == gamma_fixed].sort_values("alpha")
        ax2.plot(subset["alpha"], subset["score"], label=f"γ={gamma_fixed:.2f}", marker='o')
        for _, row in subset.iterrows():
            ax2.annotate(f"β={row['beta']:.2f}",
                         (row["alpha"], row["score"]),
                         textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)

    ax2.set_title("Score vs Alpha (Lines: γ, Label: β)")
    ax2.set_xlabel("Alpha")
    ax2.set_ylabel("Score")
    ax2.legend()

    plt.tight_layout()
    output_file = os.path.join(results_dir, f"fresco_sensitivity_{app}.png")
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"✅ Plot saved: {output_file}")

