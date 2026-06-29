import os
import json
import numpy as np
import matplotlib.pyplot as plt

# Paths
MA_RAG_DIR = r"c:\Users\Suhas Sreenath\Desktop\Medical_Hallucination_Aware_RAG\MA-RAG"
results_path = os.path.join(MA_RAG_DIR, "runs", "finance_law_proper_results.json")
figs_dir = os.path.join(MA_RAG_DIR, "figs")
os.makedirs(figs_dir, exist_ok=True)

# Set professional plotting style
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 15,
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"]
})

# Academic color palette
COLOR_BASE = "#4f6d7a"       # Slate Blue-Grey
COLOR_MARAG_LEG = "#1976d2"  # Muted Blue for Law
COLOR_MARAG_FIN = "#388e3c"  # Muted Green for Finance

def load_data():
    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)
        
    data = {
        "Financial": {
            "base_latencies": [], "base_correct": 0,
            "marag_latencies": [], "marag_correct": 0,
            "total": 0
        },
        "Legal": {
            "base_latencies": [], "base_correct": 0,
            "marag_latencies": [], "marag_correct": 0,
            "total": 0
        }
    }
    
    for qid, res in results.items():
        domain = res["expected_domain"]
        if domain not in data:
            continue
        
        stats = data[domain]
        stats["total"] += 1
        
        # Base Model
        stats["base_latencies"].append(res["base_time"])
        if res["base_evaluation"] == "Correct":
            stats["base_correct"] += 1
            
        # MA-RAG
        stats["marag_latencies"].append(res["marag_time"])
        if res["marag_evaluation"] == "Correct":
            stats["marag_correct"] += 1
            
    return data

def plot_accuracy(data):
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    
    domains = ["Legal", "Financial"]
    x = np.arange(len(domains))
    width = 0.35
    
    base_accs = [data[d]["base_correct"]/data[d]["total"] * 100 for d in domains]
    marag_accs = [data[d]["marag_correct"]/data[d]["total"] * 100 for d in domains]
    
    rects1 = ax.bar(x - width/2, base_accs, width, label="Base Model (Llama-3.1-8B-instant)", color=COLOR_BASE, edgecolor="#333333", linewidth=1)
    
    marag_colors = [COLOR_MARAG_LEG, COLOR_MARAG_FIN]
    rects2 = ax.bar(x + width/2, marag_accs, width, label="MA-RAG Framework (Ours)", color=marag_colors, edgecolor="#333333", linewidth=1.2)
    
    ax.set_ylabel("Factual Accuracy / Safety Success (%)", fontweight="bold", labelpad=10)
    ax.set_ylim(75, 105)
    ax.set_yticks(range(75, 101, 5))
    
    ax.set_xticks(x)
    ax.set_xticklabels(["Legal Domain\n(30 Questions)", "Financial Domain\n(30 Questions)"], fontweight="bold")
    
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, color="#cccccc")
    
    ax.set_title("Performance Accuracy: Base Model vs. MA-RAG Framework", fontweight="bold", fontsize=13, pad=15)
    
    for bar in rects1:
        height = bar.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9.5)
                    
    for bar in rects2:
        height = bar.get_height()
        ax.annotate(f"{height:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9.5, fontweight="bold")
    
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLOR_BASE, edgecolor="#333333", label="Base Model (Llama-3.1-8B-instant)"),
        Patch(facecolor="#1976d2", edgecolor="#333333", label="MA-RAG Framework (Ours)")
    ]
    ax.legend(handles=legend_elements, loc="lower right")
    
    plt.tight_layout()
    plt.savefig(os.path.join(figs_dir, "domain_accuracy_comparison.png"), dpi=300, bbox_inches="tight")
    plt.savefig(os.path.join(figs_dir, "domain_accuracy_comparison.pdf"), format="pdf", bbox_inches="tight")
    plt.close()
    print("Generated expanded accuracy plot.")

def plot_latency_cdf(data):
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)
    
    # Collect all base latencies (both Law & Finance)
    base_lats = data["Legal"]["base_latencies"] + data["Financial"]["base_latencies"]
    base_sorted = np.sort(base_lats)
    base_y = np.arange(1, len(base_sorted) + 1) / len(base_sorted)
    ax.plot(base_sorted, base_y, label="Base Model (Zero-Shot)", color=COLOR_BASE, linewidth=2.5, linestyle="--")
    
    # MA-RAG Legal CDF
    leg_sorted = np.sort(data["Legal"]["marag_latencies"])
    leg_y = np.arange(1, len(leg_sorted) + 1) / len(leg_sorted)
    ax.plot(leg_sorted, leg_y, label="MA-RAG Legal Pipeline", color=COLOR_MARAG_LEG, linewidth=2.2, linestyle="-")
    
    # MA-RAG Financial CDF
    fin_sorted = np.sort(data["Financial"]["marag_latencies"])
    fin_y = np.arange(1, len(fin_sorted) + 1) / len(fin_sorted)
    ax.plot(fin_sorted, fin_y, label="MA-RAG Financial Pipeline", color=COLOR_MARAG_FIN, linewidth=2.2, linestyle="-")
    
    ax.set_xlabel("Query Execution Latency (seconds)", fontweight="bold", labelpad=10)
    ax.set_ylabel("Cumulative Probability (CDF)", fontweight="bold", labelpad=10)
    ax.set_title("Latency Distribution: Base Model vs. MA-RAG Pipelines", fontweight="bold", fontsize=13, pad=15)
    
    ax.grid(True, linestyle="--", alpha=0.5, color="#cccccc")
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 1.05)
    
    ax.legend(loc="lower right", framealpha=0.9, facecolor="#ffffff", edgecolor="#cccccc")
    
    plt.tight_layout()
    plt.savefig(os.path.join(figs_dir, "finance_law_latency_cdf.png"), dpi=300, bbox_inches="tight")
    plt.savefig(os.path.join(figs_dir, "finance_law_latency_cdf.pdf"), format="pdf", bbox_inches="tight")
    plt.close()
    print("Generated expanded CDF plot.")

def plot_tradeoff(data):
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)
    
    domains = ["Legal", "Financial"]
    colors = [COLOR_MARAG_LEG, COLOR_MARAG_FIN]
    markers = ["s", "^"]
    labels = ["Legal (Law)", "Financial (Finance)"]
    
    for d, color, marker, label in zip(domains, colors, markers, labels):
        # Base stats
        base_acc = data[d]["base_correct"]/data[d]["total"] * 100
        base_lat = np.mean(data[d]["base_latencies"])
        
        # MA-RAG stats
        marag_acc = data[d]["marag_correct"]/data[d]["total"] * 100
        marag_lat = np.mean(data[d]["marag_latencies"])
        
        # Plot points
        ax.scatter(base_lat, base_acc, color=COLOR_BASE, marker=marker, s=110, edgecolors="#333333", zorder=3)
        ax.scatter(marag_lat, marag_acc, color=color, marker=marker, s=130, edgecolors="#333333", zorder=3)
        
        # Draw arrow from Base to MA-RAG
        ax.annotate("", xy=(marag_lat - 0.3, marag_acc), xytext=(base_lat + 0.3, base_acc),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.8, shrinkA=5, shrinkB=5, linestyle=":"))
        
        # Labels
        ax.text(marag_lat, marag_acc - 1.2, f"MA-RAG {d}", ha="center", va="top", fontweight="bold", color=color, fontsize=9.5)
        ax.text(base_lat, base_acc + 0.8, f"Base {d}", ha="center", va="bottom", color="#555555", fontsize=9)
        
    ax.set_xlabel("Average Query Latency (seconds)", fontweight="bold", labelpad=10)
    ax.set_ylabel("Factual Accuracy / Safety Success (%)", fontweight="bold", labelpad=10)
    ax.set_title("Quality-Latency Trade-off: Base Model vs. MA-RAG", fontweight="bold", fontsize=13, pad=15)
    
    ax.set_xlim(0, 16)
    ax.set_ylim(75, 105)
    ax.grid(True, linestyle="--", alpha=0.5, color="#cccccc")
    
    import matplotlib.lines as mlines
    leg_handles = [
        mlines.Line2D([], [], color='#555555', marker='s', linestyle='None', markersize=8, label='Legal Domain (30 Qs)'),
        mlines.Line2D([], [], color='#555555', marker='^', linestyle='None', markersize=8, label='Financial Domain (30 Qs)')
    ]
    ax.legend(handles=leg_handles, loc="lower right")
    
    plt.tight_layout()
    plt.savefig(os.path.join(figs_dir, "finance_law_tradeoff.png"), dpi=300, bbox_inches="tight")
    plt.savefig(os.path.join(figs_dir, "finance_law_tradeoff.pdf"), format="pdf", bbox_inches="tight")
    plt.close()
    print("Generated expanded trade-off plot.")

if __name__ == "__main__":
    data = load_data()
    plot_accuracy(data)
    plot_latency_cdf(data)
    plot_tradeoff(data)
    print("All expanded validation figures generated successfully!")
