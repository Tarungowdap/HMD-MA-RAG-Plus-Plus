import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import ConnectionPatch

# Ensure figs directory exists
os.makedirs("figs", exist_ok=True)

# Set standard plotting style for academic publication
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 16,
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"]
})

# Muted, professional academic palette
COLOR_BASE = "#4f6d7a"       # Slate Blue-Grey for Base models
COLOR_MARAG = "#e25f38"      # Coral/Orange for our framework (MA-RAG)
COLOR_BASELINE1 = "#a3b18a"   # Muted Green
COLOR_BASELINE2 = "#b8c0ff"   # Muted Lilac
COLOR_BASELINE3 = "#f3c68f"   # Warm Gold
COLOR_TEXT = "#222222"        # Dark charcoal text
COLOR_BG_LIGHT = "#f4f6f9"    # Very light gray for panels/boxes
COLOR_BORDER = "#4a4a4a"      # Border color

def plot_baseline_comparison():
    """Generates the comparison bar chart of baseline paradigms (Table 1)."""
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=300)
    
    paradigms = [
        "Zero-Shot Backbone\n(Qwen3-8B)",
        "Naive RAG\n(SR-RAG)",
        "Prompt Scaling\n(Multi-Refine)",
        "Adaptive RAG\n(TC-RAG)",
        "Multi-Agent\n(MDAgents)",
        "MA-RAG-ext\n(Ours)"
    ]
    accuracies = [55.40, 56.23, 56.80, 57.40, 58.20, 62.20]
    colors = [COLOR_BASE, COLOR_BASELINE1, COLOR_BASELINE2, COLOR_BASELINE3, "#9b5de5", COLOR_MARAG]
    
    bars = ax.bar(paradigms, accuracies, color=colors, width=0.55, edgecolor="#333333", linewidth=1.2)
    
    # Grid lines
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.6, color="#cccccc")
    
    # Y-axis styling
    ax.set_ylabel("Average Accuracy (%)", fontweight="bold", labelpad=10)
    ax.set_ylim(50, 65)
    
    # Title
    ax.set_title("Performance Comparison across RAG Paradigms\n(7 Medical Benchmarks Average)", fontweight="bold", fontsize=13, pad=15)
    
    # Highlight our method with a boundary and label
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.annotate(f"{height:.2f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  # 5 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight="bold" if i == 5 else "normal")
        if i == 5:
            # Highlight our bar
            bar.set_linewidth(2.0)
            bar.set_edgecolor("#c0392b")
            
    plt.tight_layout()
    plt.savefig("figs/baseline_comparison.png", dpi=300, bbox_inches="tight")
    plt.savefig("figs/baseline_comparison.pdf", format="pdf", bbox_inches="tight")
    plt.close()
    print("Generated baseline comparison plots.")

def plot_benchmark_gains():
    """Generates the grouped bar chart for accuracy across individual benchmarks (Table 2)."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    
    benchmarks = [
        "MedQA\n(USMLE)",
        "MedMCQA",
        "Medbullets",
        "MMLU-Pro\n(Medical)",
        "NEJM\n(Clinical)",
        "MedExpQA",
        "MedXpertQA\n(Complex)",
        "Domain\nAverage"
    ]
    
    base_acc = [71.10, 61.30, 51.00, 64.90, 56.00, 67.20, 16.10, 55.40]
    marag_acc = [76.50, 66.80, 59.40, 70.50, 60.80, 72.40, 22.00, 62.20]
    gains = [m - b for b, m in zip(base_acc, marag_acc)]
    
    x = np.arange(len(benchmarks))
    width = 0.35
    
    rects_base = ax.bar(x - width/2, base_acc, width, label="Qwen3-8B Base", color=COLOR_BASE, edgecolor="#444444", linewidth=1)
    rects_marag = ax.bar(x + width/2, marag_acc, width, label="MA-RAG-ext (Ours)", color=COLOR_MARAG, edgecolor="#444444", linewidth=1.2)
    
    # Highlight Domain Average benchmark
    rects_marag[-1].set_edgecolor("#c0392b")
    rects_marag[-1].set_linewidth(1.8)
    
    # Visual grid lines
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.6, color="#cccccc")
    
    # Labeling
    ax.set_ylabel("Accuracy (%)", fontweight="bold", labelpad=10)
    ax.set_title("Medical Q&A Benchmark Performance: Qwen3-8B vs. MA-RAG-ext", fontweight="bold", fontsize=14, pad=18)
    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks, fontweight="normal")
    ax.set_ylim(0, 90)
    ax.legend(loc="upper right", framealpha=0.9, facecolor="#ffffff", edgecolor="#cccccc")
    
    # Add accuracy text and gain labels on top
    for i in range(len(benchmarks)):
        b_val = base_acc[i]
        m_val = marag_acc[i]
        gain = gains[i]
        
        # Base value text
        ax.annotate(f"{b_val:.1f}%",
                    xy=(x[i] - width/2, b_val),
                    xytext=(0, 2),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
        
        # MA-RAG value text
        ax.annotate(f"{m_val:.1f}%",
                    xy=(x[i] + width/2, m_val),
                    xytext=(0, 2),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight="bold")
        
        # Gain tag above both
        highest = max(b_val, m_val)
        ax.annotate(f"+{gain:.1f}%",
                    xy=(x[i], highest),
                    xytext=(0, 14),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, color="#b83b1d", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="#fff2f0", ec="#ffccc7", lw=0.8))
        
    plt.tight_layout()
    plt.savefig("figs/benchmark_gains.png", dpi=300, bbox_inches="tight")
    plt.savefig("figs/benchmark_gains.pdf", format="pdf", bbox_inches="tight")
    plt.close()
    print("Generated benchmark gains plots.")

def plot_local_validation():
    """Generates a side-by-side plot of local validation results: Accuracy & Safety vs Latency."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)
    
    # Left plot: Factual Accuracy (Domain Qs) and Hallucination Rejection (Nonsense Qs)
    categories = ["Factual Accuracy\n(Domain Qs)", "Hallucination Rejection\n(Nonsense Qs)"]
    base_vals = [96.7, 100.0]
    marag_vals = [100.0, 100.0]
    
    x = np.arange(len(categories))
    width = 0.3
    
    ax1.bar(x - width/2, base_vals, width, label="Base (Llama-3.1-8B-instant)", color=COLOR_BASE, edgecolor="#444444")
    bars_marag = ax1.bar(x + width/2, marag_vals, width, label="MA-RAG Framework", color=COLOR_MARAG, edgecolor="#444444", linewidth=1.2)
    
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(True, linestyle="--", alpha=0.6, color="#cccccc")
    ax1.set_ylabel("Success Rate (%)", fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontweight="bold")
    ax1.set_ylim(85, 103)
    ax1.set_title("Accuracy & Safety Comparison", fontweight="bold", fontsize=12, pad=12)
    ax1.legend(loc="lower right")
    
    # Labels on top
    for i in range(len(categories)):
        ax1.annotate(f"{base_vals[i]:.1f}%", xy=(x[i] - width/2, base_vals[i]), xytext=(0, 2), textcoords="offset points", ha='center', va='bottom', fontsize=9)
        ax1.annotate(f"{marag_vals[i]:.1f}%", xy=(x[i] + width/2, marag_vals[i]), xytext=(0, 2), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight="bold")

    # Right plot: Latency
    models = ["Base Model\n(Llama-3.1-8B-instant)", "MA-RAG\nFramework"]
    latencies = [1.04, 10.60]
    colors = [COLOR_BASE, COLOR_MARAG]
    
    bars_lat = ax2.bar(models, latencies, color=colors, width=0.4, edgecolor="#444444", linewidth=1.2)
    
    ax2.set_axisbelow(True)
    ax2.yaxis.grid(True, linestyle="--", alpha=0.6, color="#cccccc")
    ax2.set_ylabel("Average Latency per Query (seconds)", fontweight="bold")
    ax2.set_ylim(0, 13)
    ax2.set_title("Computation Latency Trade-off", fontweight="bold", fontsize=12, pad=12)
    
    for bar in bars_lat:
        height = bar.get_height()
        ax2.annotate(f"{height:.2f} s", xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight="bold")
        
    plt.suptitle("Local Validation Set Trade-offs: Quality vs. Latency", fontweight="bold", fontsize=14, y=0.98)
    plt.tight_layout()
    plt.savefig("figs/local_validation_metrics.png", dpi=300, bbox_inches="tight")
    plt.savefig("figs/local_validation_metrics.pdf", format="pdf", bbox_inches="tight")
    plt.close()
    print("Generated local validation plots.")

def draw_architecture_diagram():
    """Generates a publication-grade system architecture diagram using matplotlib."""
    fig, ax = plt.subplots(figsize=(13.5, 9.0), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9.5)
    ax.axis("off")
    
    # ------------------ DRAW BOX HELPER ------------------
    def draw_node(text, center, width, height, fill, border, text_color=COLOR_TEXT, font_w="normal", font_s=10.5, style="round"):
        cx, cy = center
        w_half, h_half = width/2, height/2
        
        if style == "round":
            patch = mpatches.FancyBboxPatch(
                (cx - w_half, cy - h_half), width, height,
                boxstyle="round,pad=0.04,rounding_size=0.1",
                facecolor=fill, edgecolor=border, linewidth=2, zorder=3
            )
        elif style == "diamond":
            coords = [[cx - w_half*1.2, cy], [cx, cy + h_half*1.2], [cx + w_half*1.2, cy], [cx, cy - h_half*1.2]]
            patch = mpatches.Polygon(coords, facecolor=fill, edgecolor=border, linewidth=2, zorder=3)
        else:
            patch = mpatches.Rectangle(
                (cx - w_half, cy - h_half), width, height,
                facecolor=fill, edgecolor=border, linewidth=2, zorder=3
            )
            
        ax.add_patch(patch)
        ax.text(cx, cy, text, ha="center", va="center", color=text_color, fontweight=font_w, fontsize=font_s, zorder=4, multialignment="center")
        return center
        
    def draw_arrow(start, end, text="", text_pos="side", arrow_color="#555555", style="->"):
        # Draw nice arrow using annotate
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle=style, color=arrow_color, lw=1.8, shrinkA=3, shrinkB=3, mutation_scale=12, zorder=2))
        if text:
            tx = (start[0] + end[0]) / 2
            ty = (start[1] + end[1]) / 2
            if text_pos == "side":
                ax.text(tx + 0.15, ty, text, ha="left", va="center", fontsize=9, color="#444444", fontweight="bold", zorder=5)
            elif text_pos == "above":
                ax.text(tx, ty + 0.12, text, ha="center", va="bottom", fontsize=9, color="#444444", fontweight="bold", zorder=5)
            elif text_pos == "below":
                ax.text(tx, ty - 0.12, text, ha="center", va="top", fontsize=9, color="#444444", fontweight="bold", zorder=5)

    # ------------------ BACKGROUND FRAMES ------------------
    # Frame for Medical Pipeline (Agentic Debate Loop)
    med_frame = mpatches.Rectangle(
        (6.1, 1.4), 6.5, 5.8,
        facecolor="#f9fafd", edgecolor="#adc5e3", linewidth=1.5, linestyle="--", zorder=1
    )
    ax.add_patch(med_frame)
    ax.text(6.3, 6.9, "Medical Pipeline (Multi-Round Agentic RAG Debate)", ha="left", va="bottom", fontsize=11, color="#2b5c8f", fontweight="bold", zorder=2)

    # Frame for Routing layer
    routing_frame = mpatches.Rectangle(
        (0.4, 7.3), 12.2, 1.8,
        facecolor="#fcfcfc", edgecolor="#dddddd", linewidth=1.2, zorder=1
    )
    ax.add_patch(routing_frame)
    ax.text(0.6, 8.8, "Classification & Routing Layer", ha="left", va="bottom", fontsize=11, color="#555555", fontweight="bold", zorder=2)

    # ------------------ DEFINE NODES ------------------
    # Step 1: Input Query
    n_input = draw_node("User Query\n(Text Case / Question)", (6.5, 8.2), 3.2, 0.75, "#ffffff", COLOR_BORDER, font_w="bold", font_s=11)
    
    # Step 2: Router Agent
    n_router = draw_node("Master Domain Classifier\n(Router Agent)", (6.5, 5.0), 3.2, 0.75, "#eaeaea", COLOR_BORDER, font_w="bold", font_s=11)
    
    # Connection from Input to Router
    draw_arrow(n_input, n_router)

    # Step 3: Domain Splits
    # Out of Domain / Nonsense
    n_block = draw_node("Safety Block\n(Immediate Reject)", (1.8, 5.0), 2.2, 0.75, "#ffe5e5", "#c0392b", text_color="#c0392b", font_w="bold", font_s=10.5)
    draw_arrow(n_router, n_block, text="Other", text_pos="above")

    # In Domain Branches: Legal & Financial
    n_legal = draw_node("Legal Agent\n(Statutes & Precedents RAG)", (1.8, 3.8), 2.4, 0.75, "#e3f2fd", "#1976d2", font_s=10.5)
    n_finance = draw_node("Financial Agent\n(Risk & Portfolio RAG)", (4.4, 3.8), 2.4, 0.75, "#e8f5e9", "#388e3c", font_s=10.5)
    
    # Routing arrows
    draw_arrow(n_router, (1.8, 4.2))
    draw_arrow(n_router, (4.4, 4.2))
    ax.text(1.9, 4.5, "Legal", ha="right", va="center", fontsize=9, color="#444444", fontweight="bold")
    ax.text(4.3, 4.5, "Financial", ha="left", va="center", fontsize=9, color="#444444", fontweight="bold")

    # In Domain Branch: Medical (enters the Medical Multi-Round Frame)
    n_med_start = (9.3, 6.7)
    draw_arrow(n_router, n_med_start, text="Medical", text_pos="above")
    
    # Internal Medical Flow:
    # 1. 3 Expert Candidates (Stage 1)
    n_med_gen = draw_node("Stage 1: Multi-Agent Parallel Generation\n(Expert A: Primary Care, Expert B: Specialist, Expert C: Emergency)", 
                          (9.35, 6.2), 5.8, 0.65, "#fff2e6", "#e67e22", font_s=9.5)
    
    # 2. Peer Review & Debate Critique (Stage 2)
    n_med_debate = draw_node("Stage 2: Peer-Review & Debate Critique\n(Cross-critique for inaccuracies & hallucinations)", 
                            (9.35, 5.0), 5.8, 0.65, "#fff2e6", "#e67e22", font_s=9.5)
    draw_arrow(n_med_gen, n_med_debate)

    # 3. Moderator Synthesis (Stage 3)
    n_med_mod = draw_node("Stage 3: Moderator Synthesis & Consensus Editing\n(Consolidates final stances into a clean draft)", 
                          (9.35, 3.8), 5.8, 0.65, "#fff2e6", "#e67e22", font_s=9.5)
    draw_arrow(n_med_debate, n_med_mod)

    # 4. Consensus & Safety Judge (Stage 4)
    n_med_judge = draw_node("Consensus Reached & \nHigh/Med Confidence?", 
                            (9.35, 2.5), 3.2, 0.65, "#fff9db", "#f59f00", font_w="bold", font_s=9.5, style="diamond")
    draw_arrow(n_med_mod, (9.35, 2.9)) # to top of diamond

    # 5. External RAG Loop (If NO)
    n_med_query = draw_node("Disagreement Query\nGenerator", (11.6, 3.8), 1.9, 0.60, "#eaeaea", COLOR_BORDER, font_s=8.5)
    n_med_kb = draw_node("External KB Retrieval\n(BM25 + Rerank)", (11.6, 5.0), 1.9, 0.60, "#eaeaea", COLOR_BORDER, font_s=8.5)
    
    # Diamond NO branch to Query Generator
    draw_arrow((11.0, 2.5), (11.6, 2.5), style="-") # horizontal line out of diamond
    draw_arrow((11.6, 2.5), (11.6, 3.5), text="No (Loop)", text_pos="side") # arrow up to generator
    
    draw_arrow(n_med_query, n_med_kb)
    # Loop back to Stage 1
    draw_arrow(n_med_kb, (11.6, 6.2), style="-")
    draw_arrow((11.6, 6.2), (11.45, 6.2)) # arrow back to side of Stage 1 box

    # 6. Medical Approved Output
    n_med_approve = draw_node("Approved Medical\nResponse", (9.35, 1.6), 2.2, 0.40, "#e8f5e9", "#2e7d32", font_w="bold", font_s=9.0)
    draw_arrow((9.35, 2.1), n_med_approve, text="Yes", text_pos="side")

    # Step 4: Final Synthesis & Output Consolidation
    n_synthesis = draw_node("Master Summarizer Agent\n(Multi-Domain Response Synthesis)", (5.0, 1.2), 3.5, 0.70, "#eaeaea", COLOR_BORDER, font_w="bold", font_s=11)
    
    # Draw connections from domain agents to synthesis
    draw_arrow(n_legal, (5.0, 3.8), style="-")
    draw_arrow(n_finance, (5.0, 3.8), style="-")
    draw_arrow((5.0, 3.8), n_synthesis)
    
    # Connection from Medical Approved Output to Synthesis
    draw_arrow(n_med_approve, (9.35, 1.2), style="-")
    draw_arrow((9.35, 1.2), n_synthesis)

    # Step 5: Final Response output
    n_output = draw_node("Consolidated Final Expert Response\n(Factually Verified & Hallucination Checked)", (5.0, 0.35), 4.2, 0.65, "#d4edda", "#28a745", font_w="bold", font_s=11.5)
    draw_arrow(n_synthesis, n_output)

    # ------------------ ADD LEGEND/LABELS ------------------
    # Title at the top center
    ax.text(6.5, 9.15, "MA-RAG: Multi-Domain Hallucination-Aware Agentic RAG Framework", ha="center", va="center", fontsize=15, fontweight="bold", color="#1a1a1a")

    # Metadata / Legend
    legend_rect = mpatches.Rectangle(
        (0.4, 0.1), 2.2, 2.0,
        facecolor="#ffffff", edgecolor="#dddddd", linewidth=1.0, zorder=1
    )
    ax.add_patch(legend_rect)
    ax.text(0.5, 1.9, "Legend:", ha="left", va="bottom", fontsize=10, fontweight="bold", color="#333333", zorder=2)
    
    # Colors representation
    ax.add_patch(mpatches.Rectangle((0.5, 1.55), 0.3, 0.2, facecolor="#fff2e6", edgecolor="#e67e22", zorder=2))
    ax.text(0.9, 1.6, "Medical debate steps", ha="left", va="center", fontsize=8.5, color="#333333", zorder=2)

    ax.add_patch(mpatches.Rectangle((0.5, 1.25), 0.3, 0.2, facecolor="#d4edda", edgecolor="#28a745", zorder=2))
    ax.text(0.9, 1.3, "Final response output", ha="left", va="center", fontsize=8.5, color="#333333", zorder=2)

    ax.add_patch(mpatches.Rectangle((0.5, 0.95), 0.3, 0.2, facecolor="#ffe5e5", edgecolor="#c0392b", zorder=2))
    ax.text(0.9, 1.0, "Safety block", ha="left", va="center", fontsize=8.5, color="#333333", zorder=2)

    ax.add_patch(mpatches.Rectangle((0.5, 0.65), 0.3, 0.2, facecolor="#eaeaea", edgecolor=COLOR_BORDER, zorder=2))
    ax.text(0.9, 0.7, "Routing & Core Agents", ha="left", va="center", fontsize=8.5, color="#333333", zorder=2)

    ax.add_patch(mpatches.Rectangle((0.5, 0.35), 0.3, 0.2, facecolor="#e3f2fd", edgecolor="#1976d2", zorder=2))
    ax.text(0.9, 0.4, "Other Domain agents", ha="left", va="center", fontsize=8.5, color="#333333", zorder=2)

    plt.tight_layout()
    plt.savefig("figs/architecture_diagram.png", dpi=300, bbox_inches="tight")
    plt.savefig("figs/architecture_diagram.pdf", format="pdf", bbox_inches="tight")
    plt.close()
    print("Generated architecture diagram plots.")

if __name__ == "__main__":
    plot_baseline_comparison()
    plot_benchmark_gains()
    plot_local_validation()
    draw_architecture_diagram()
    print("All plots generated successfully under 'figs/'!")
