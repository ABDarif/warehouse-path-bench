"""
Gantt chart: Multi-Robot Warehouse Pathfinding Optimization Project.
Sources: T2510622_Updated Report (3).pdf (Project Management Plan §3.5, Methodology Ch 4) and codebase.
Project duration: May 2025 – December 2025 (8 months).
Components: Project list, duration, milestones, dependencies.
All labels are placed to the right of each bar (nothing inside bars).
"""

import matplotlib.pyplot as plt
from datetime import datetime
import os

# Project: May 2025 – December 2025 (8 months) — thesis report
START = datetime(2025, 5, 1)
MONTHS_TOTAL = 8

# Tasks: short labels for Y-axis (fit in graph area); bar_text = description to the RIGHT of bar only
TASKS = [
    {"label": "1. Literature & problem def.", "start_mo": 0, "end_mo": 1.2,
     "bar_text": "Literature review and problem formulation", "color": "#2166ac"},
    {"label": "2. Sim. environment development", "start_mo": 0.5, "end_mo": 2.5,
     "bar_text": "Layouts, SimPy, grid, collision tracker; synthetic data", "color": "#4393c3"},
    {"label": "3. Baseline algorithm determining", "start_mo": 1.8, "end_mo": 3.2,
     "bar_text": "Directional and congestion handling", "color": "#92c5de"},
    {"label": "4. Routing algos. & Hybrid NN2opt", "start_mo": 2.8, "end_mo": 4.5,
     "bar_text": "Held-Karp, NN2opt, Hybrid NN2opt, GA, ACO, ALO; baseline-driven improvement", "color": "#f4a582"},
    {"label": "5. Congestion & single-robot testing", "start_mo": 4, "end_mo": 5.5,
     "bar_text": "SimPy testing; single-depot, run_matrix; travel time, congestion, efficiency", "color": "#d6604d"},
    {"label": "6. Multi-robot & multi-depot", "start_mo": 5.2, "end_mo": 6.5,
     "bar_text": "3–15 robots; run_multi_depot; collision and scalability", "color": "#b2182b"},
    {"label": "7. Performance evaluation", "start_mo": 6.2, "end_mo": 7.5,
     "bar_text": "Six metrics; viz and result generation", "color": "#762a83"},
    {"label": "8. Assessment & thesis writing", "start_mo": 7, "end_mo": 8,
     "bar_text": "Results summary and comparisons", "color": "#404040"},
]

# Milestones (report and codebase)
MILESTONES = [
    (2.5, "Simulation ready"),
    (4.5, "Algorithms integrated"),
    (6.5, "Experiments complete"),
    (8, "Project completion"),
]

# Dependencies: sequential flow as in report (step-by-step methodology)
DEPENDENCIES = [
    (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7),
]

def month_to_date(month_float):
    y = START.year
    m = START.month + int(month_float)
    while m > 12:
        m -= 12
        y += 1
    return datetime(y, min(m, 12), 1)


def main():
    n = len(TASKS)
    fig, ax = plt.subplots(figsize=(18, 9))
    # Y-lim: tight to bars only (no extra gap below last task)
    ax.set_xlim(0, MONTHS_TOTAL)
    ax.set_ylim(-0.5, n - 0.35)
    ax.invert_yaxis()

    ax.grid(axis="x", alpha=0.35, linestyle="--")
    ax.set_axisbelow(True)

    # X-axis: months (May–Dec 2025)
    ax.set_xticks(range(MONTHS_TOTAL + 1))
    ax.set_xticklabels([str(m) for m in range(MONTHS_TOTAL + 1)], fontsize=11)
    ax.set_xlabel("Timeline (months from May 2025)", fontsize=13, fontweight="bold", labelpad=8)
    ax.set_xlim(0, MONTHS_TOTAL)

    bar_height = 0.6
    # Draw bars (no text inside)
    for i, t in enumerate(TASKS):
        width = t["end_mo"] - t["start_mo"]
        ax.barh(i, width, left=t["start_mo"], height=bar_height,
                color=t["color"], edgecolor="black", linewidth=0.6)

    # Right-side labels: minimal extra space so no large blank to the right
    x_max = MONTHS_TOTAL + 2.0
    ax.set_xlim(0, x_max)
    for i, t in enumerate(TASKS):
        ax.text(t["end_mo"] + 0.06, i, t["bar_text"], ha="left", va="center",
                fontsize=9, color="black", wrap=False)

    # Milestones: vertical dashed lines only; labels in a single line above the plot (no overlap)
    for mo, _ in MILESTONES:
        ax.axvline(x=mo, color="gray", linestyle="--", linewidth=1, alpha=0.8)

    # Dependencies: arrows from end of task A to start of task B
    for (i_from, i_to) in DEPENDENCIES:
        if i_from >= n or i_to >= n or i_from == i_to:
            continue
        t_from, t_to = TASKS[i_from], TASKS[i_to]
        x1, y1 = t_from["end_mo"], i_from
        x2, y2 = t_to["start_mo"], i_to
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="gray", lw=0.9, alpha=0.6))

    # Y-axis: task names
    ax.set_yticks(range(n))
    ax.set_yticklabels([t["label"] for t in TASKS], fontsize=11)
    ax.set_ylabel("")

    # Top axis: calendar
    ax2 = ax.twiny()
    ax2.set_xlim(0, MONTHS_TOTAL)
    cal_ticks = [0, 2, 4, 6, 8]
    cal_dates = [month_to_date(m) for m in cal_ticks]
    ax2.set_xticks(cal_ticks)
    ax2.set_xticklabels([d.strftime("%b '%y") for d in cal_dates], fontsize=11)
    ax2.set_xlabel("")

    fig.suptitle("Warehouse Order Picking and Congestion-Aware Routing: Project Timeline (May–Dec 2025)",
                 fontsize=15, fontweight="bold", y=1.02)
    # Milestones: centered, directly under the title
    milestone_line = "  ·  ".join(f"{mlabel} ({mo} mo)" for mo, mlabel in MILESTONES)
    fig.text(0.5, 0.97, "Milestones: " + milestone_line, ha="center", va="top", fontsize=9, style="italic")
    plt.subplots_adjust(left=0.2, right=0.78, bottom=0.12, top=0.88)
    plt.tight_layout()

    out_path = os.path.join("figs", "gantt_timeline.png")
    os.makedirs("figs", exist_ok=True)
    plt.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.2)
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
