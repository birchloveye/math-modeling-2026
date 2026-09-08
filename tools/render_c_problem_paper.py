#!/usr/bin/env python3
"""生成C题科研插图与符合国赛电子版基本规范的中文PDF。"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "workspace/figures/.mplconfig"))
(ROOT / "workspace/figures/.mplconfig").mkdir(parents=True, exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

sys.path.insert(0, str(ROOT / "tools"))
from c_problem_experiment import design_concentration, num, predict_fixed, read_sheet, week_num  # noqa: E402

COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
HEADING_COLOR = "#1f4e79"
ACCENT_COLOR = "#b8860b"
SONG = Path(r"C:\Windows\Fonts\simsun.ttc")
HEI = Path(r"C:\Windows\Fonts\simhei.ttf")


def configure_plotting() -> FontProperties:
    font = FontProperties(fname=str(SONG), size=10.5)
    plt.rcParams.update({
        "font.family": font.get_name(), "font.size": 10.5, "axes.titlesize": 11,
        "axes.labelsize": 10.5, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
        "legend.fontsize": 9, "axes.linewidth": 0.9, "lines.linewidth": 1.3,
        "xtick.major.width": 0.9, "ytick.major.width": 0.9, "figure.dpi": 160,
        "savefig.dpi": 600, "axes.unicode_minus": False,
    })
    return font


def plot_figures(data_path: Path, results_a: Path, results_b: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_plotting()
    a = json.loads(results_a.read_text(encoding="utf-8"))
    b = json.loads(results_b.read_text(encoding="utf-8"))
    male = read_sheet(data_path, "男胎检测数据")
    x, y, _, _ = design_concentration(male, "B")
    fixed = np.array(b["q1"]["fixed_coefficients_standardized"])
    fitted = predict_fixed(x, fixed, b["q1"]["scaler"])
    weeks = np.array([week_num(r["检测孕周"]) for r in male])
    bmis = np.array([num(r["孕妇BMI"]) for r in male])

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.35), constrained_layout=True)
    ax = axes[0]
    sc = ax.scatter(weeks, y * 100, c=bmis, cmap="viridis", s=10, alpha=0.35, linewidths=0)
    order = np.argsort(weeks)
    bins = np.linspace(weeks.min(), weeks.max(), 24)
    idx = np.digitize(weeks, bins)
    centers, medians = [], []
    for k in range(1, len(bins)):
        mask = idx == k
        if np.sum(mask) >= 8:
            centers.append(float(np.mean(weeks[mask])))
            medians.append(float(np.median(y[mask]) * 100))
    ax.plot(centers, medians, color=COLORS[3], marker="o", markersize=3.2, label="分箱中位数")
    ax.axhline(4, color="#555555", linestyle="--", linewidth=1.1, label="4%阈值")
    ax.set_xlabel("检测孕周(周)")
    ax.set_ylabel("Y染色体浓度(%)")
    ax.set_title("(a) 观测浓度与孕周")
    ax.grid(alpha=0.18, linewidth=0.6)
    ax.legend(frameon=False, loc="upper left")
    cb = fig.colorbar(sc, ax=ax, fraction=0.047, pad=0.03)
    cb.set_label("BMI")

    ax = axes[1]
    residual = (y - fitted) * 100
    bands = [(20, 29.14), (29.14, 34.50), (34.50, 48)]
    values = [residual[(bmis >= lo) & (bmis < hi)] for lo, hi in bands]
    box = ax.boxplot(values, patch_artist=True, widths=0.58, showfliers=False,
                     medianprops={"color": "#333333", "linewidth": 1.2},
                     whiskerprops={"linewidth": 0.9}, capprops={"linewidth": 0.9},
                     boxprops={"linewidth": 0.9})
    for patch, color in zip(box["boxes"], COLORS[:3], strict=True):
        patch.set_facecolor(color)
        patch.set_alpha(0.72)
    ax.axhline(0, color="#555555", linewidth=1.0, linestyle="--")
    ax.set_xticks([1, 2, 3], ["<29.14", "29.14-34.50", ">=34.50"])
    ax.set_xlabel("BMI区间")
    ax.set_title("(b) 路线B拟合残差分布")
    ax.grid(axis="y", alpha=0.18, linewidth=0.6)
    figure1 = output_dir / "figure1_concentration_fit.png"
    fig.savefig(figure1, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    grouping = b["q2_q3"]["selected_grouping"]["groups"]
    labels = ["<29.14", "29.14-34.50", ">=34.50"]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.0), constrained_layout=True)
    ax = axes[0, 0]
    bars = ax.bar(labels, [g["week"] for g in grouping], color=COLORS[:3], width=0.62)
    ax.set_ylim(10, 19)
    ax.set_ylabel("推荐检测时点(周)")
    ax.set_title("(a) 主情景推荐时点")
    ax.tick_params(axis="x", labelbottom=False)
    ax.grid(axis="y", alpha=0.18, linewidth=0.6)
    for bar, value in zip(bars, [g["week"] for g in grouping], strict=True):
        ax.text(bar.get_x() + bar.get_width()/2, value + 0.15, f"{value:.1f}", ha="center", va="bottom", fontsize=9)

    ax = axes[0, 1]
    probs = [g["attainment_probability"] for g in grouping]
    bars = ax.bar(labels, probs, color=COLORS[:3], width=0.62)
    ax.set_ylim(0.75, 1.0)
    ax.set_title("(b) 推荐时点达标概率")
    ax.tick_params(axis="x", labelbottom=False)
    ax.grid(axis="y", alpha=0.18, linewidth=0.6)
    for bar, value in zip(bars, probs, strict=True):
        ax.text(bar.get_x() + bar.get_width()/2, value + 0.006, f"{value:.1%}", ha="center", va="bottom", fontsize=9)

    ax = axes[1, 0]
    costs = [2, 3, 5]
    for group_index, color in enumerate(COLORS[:3]):
        values = [b["q2_q3"]["risk_sensitivity"][f"risk_fail_{cost}"]["groups"][group_index]["week"] for cost in costs]
        ax.plot(costs, values, color=color, marker=["o", "s", "^"][group_index], label=labels[group_index])
    ax.set_xlabel("未达标代价系数")
    ax.set_ylabel("推荐检测时点(周)")
    ax.set_title("(c) 风险权重敏感性")
    ax.set_xticks(costs)
    ax.grid(alpha=0.18, linewidth=0.6)
    ax.legend(frameon=False, ncol=1)

    ax = axes[1, 1]
    tasks = ["ANY", "T13", "T18", "T21"]
    metric_names = ["balanced_accuracy", "sensitivity", "specificity", "pr_auc"]
    metric_labels = ["平衡准确率", "灵敏度", "特异度", "PR-AUC"]
    width = 0.18
    positions = np.arange(len(tasks))
    for j, (metric, label, color) in enumerate(zip(metric_names, metric_labels, COLORS[:4], strict=True)):
        vals = [a["q4"]["labels"][task][metric] for task in tasks]
        ax.bar(positions + (j - 1.5) * width, vals, width=width, label=label, color=color,
               hatch=["", "//", "..", "xx"][j], edgecolor="white", linewidth=0.4)
    ax.set_xticks(positions, tasks)
    ax.set_xlabel("异常判定任务")
    ax.set_ylim(0, 1.04)
    ax.set_title("(d) 路线A折外分类性能")
    ax.grid(axis="y", alpha=0.18, linewidth=0.6)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper center")
    figure2 = output_dir / "figure2_results_overview.png"
    fig.savefig(figure2, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return [figure1, figure2]


def clean_inline(text: str) -> str:
    text = re.sub(r"\[claim:[^\]]+\]", "", text)
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"\\\((.*?)\\\)", lambda match: equation_text(match.group(1)), text)
    return html.escape(text)


def equation_text(text: str) -> str:
    text = text.replace(r"\boldsymbol", "").replace(r"\mathbf", "")
    text = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", text)
    text = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", text)
    text = re.sub(r"_\{([^{}]+)\}", r"_(\1)", text)
    text = re.sub(r"\\operatorname\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\(?:mathbf|boldsymbol)\s*\{?([^{}\s]+)\}?", r"\1", text)
    replacements = {
        r"\beta": "β", r"\gamma": "γ", r"\theta": "θ", r"\alpha": "α", r"\varepsilon": "ε",
        r"\ge": "≥", r"\le": "≤", r"\inf": "inf", r"\prod": "Π", r"\sum": "Σ",
        r"\mid": " | ", r"\qquad": "    ", r"\operatorname": "", r"\mathbf": "",
        r"\frac": "/", r"\max": "max", r"\in": "∈", r"\top": "T",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[{}]", "", text)
    text = text.replace("\\", " ")
    return text.strip()


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("SimSun", str(SONG), subfontIndex=0))
    pdfmetrics.registerFont(TTFont("SimHei", str(HEI)))


def build_pdf(markdown_path: Path, output_pdf: Path, figures_dir: Path) -> None:
    register_fonts()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    body = ParagraphStyle("BodyCN", fontName="SimSun", fontSize=12, leading=20, firstLineIndent=24,
                          alignment=TA_LEFT, textColor=colors.HexColor("#222222"), spaceAfter=4)
    abstract_body = ParagraphStyle("AbstractCN", parent=body, firstLineIndent=24, leading=20)
    h1 = ParagraphStyle("H1CN", fontName="SimHei", fontSize=15, leading=22, spaceBefore=10, spaceAfter=7,
                        textColor=colors.HexColor(HEADING_COLOR))
    h2 = ParagraphStyle("H2CN", fontName="SimHei", fontSize=13, leading=20, spaceBefore=8, spaceAfter=5)
    title_style = ParagraphStyle("TitleCN", fontName="SimHei", fontSize=18, leading=27, alignment=TA_CENTER, spaceAfter=20)
    eq_style = ParagraphStyle("EquationCN", fontName="SimSun", fontSize=11, leading=18, alignment=TA_CENTER, spaceBefore=4, spaceAfter=6)
    caption_style = ParagraphStyle("CaptionCN", fontName="SimSun", fontSize=10.5, leading=15, alignment=TA_CENTER, spaceAfter=8)
    ref_style = ParagraphStyle("RefCN", fontName="SimSun", fontSize=10.5, leading=16, leftIndent=14, firstLineIndent=-14, spaceAfter=3)
    list_style = ParagraphStyle("ListCN", parent=body, leftIndent=24, firstLineIndent=-12)

    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    story = []
    title = lines[0].lstrip("# ")
    abstract_title = ParagraphStyle("AbstractTitle", parent=h1, alignment=TA_CENTER, textColor=colors.HexColor("#222222"))
    story.extend([Spacer(1, 0.7 * cm), Paragraph(clean_inline(title), title_style),
                  HRFlowable(width="42%", thickness=0.8, color=colors.HexColor(ACCENT_COLOR), spaceAfter=12),
                  Paragraph("摘要", abstract_title)])
    i = lines.index("## 摘要") + 1
    while i < len(lines) and not lines[i].startswith("## 1 "):
        line = lines[i].strip()
        if line.startswith("**关键词：**"):
            story.append(Spacer(1, 4))
            story.append(Paragraph(clean_inline(line), abstract_body))
        elif line and not line.startswith("##"):
            story.append(Paragraph(clean_inline(line), abstract_body))
        i += 1
    story.append(PageBreak())

    table_rows: list[list[str]] = []
    equation: list[str] = []
    equation_number = 0
    in_refs = False
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if line == r"\[":
            equation = []
            i += 1
            while i < len(lines) and lines[i].strip() != r"\]":
                equation.append(lines[i].strip())
                i += 1
            equation_number += 1
            eq = Table([[Paragraph(html.escape(equation_text(" ".join(equation))), eq_style),
                         Paragraph(f"({equation_number})", eq_style)]],
                       colWidths=[14.8 * cm, 1.0 * cm])
            eq.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                    ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
            story.append(eq)
        elif line.startswith("!["):
            match = re.match(r"!\[[^]]*\]\(([^)]+)\)", line)
            if match:
                image_path = (markdown_path.parent / match.group(1)).resolve()
                image = Image(str(image_path), width=15.8 * cm, height=15.8 * cm * (3.35 / 7.2 if "figure1" in image_path.name else 6.0 / 7.2))
                story.append(KeepTogether([Spacer(1, 5), image]))
        elif line.startswith("# ") or line == "## 摘要":
            pass
        elif line.startswith("## "):
            in_refs = line == "## 参考文献"
            story.append(Paragraph(clean_inline(line[3:]), h1))
        elif line.startswith("### "):
            story.append(Paragraph(clean_inline(line[4:]), h2))
        elif line.startswith("|"):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [clean_inline(c.strip()) for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    table_rows.append(cells)
                i += 1
            i -= 1
            widths = [15.8 * cm / len(table_rows[0])] * len(table_rows[0])
            data = [[Paragraph(cell, caption_style) for cell in row] for row in table_rows]
            table = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
            table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "SimSun"), ("FONTSIZE", (0, 0), (-1, -1), 10.5),
                ("LINEBELOW", (0, 0), (-1, 0), 0.9, colors.HexColor("#444444")),
                ("LINEBELOW", (0, -1), (-1, -1), 0.9, colors.HexColor("#444444")),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend([Spacer(1, 4), table, Spacer(1, 7)])
        elif re.match(r"^\d+\. ", line):
            story.append(Paragraph(clean_inline(line), list_style))
        elif line.startswith("**图"):
            story.append(Paragraph(clean_inline(line), caption_style))
        elif line:
            style = ref_style if in_refs and line.startswith("[") else body
            story.append(Paragraph(clean_inline(line), style))
        i += 1

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("SimSun", 9)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawCentredString(A4[0] / 2, 1.25 * cm, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(str(output_pdf), pagesize=A4, leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm, title=title, author="")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "workspace/data/附件.xlsx")
    parser.add_argument("--paper", type=Path, default=ROOT / "workspace/paper/draft.md")
    parser.add_argument("--output", type=Path, default=ROOT / "output/pdf/C题_NIPT建模论文.pdf")
    args = parser.parse_args()
    figures = ROOT / "workspace/figures"
    plot_figures(args.data, ROOT / "workspace/experiments/runs/c-problem-routes-ab-v7-0001/results.json",
                 ROOT / "workspace/experiments/runs/c-problem-routes-ab-v7-0002/results.json", figures)
    build_pdf(args.paper, args.output, figures)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
