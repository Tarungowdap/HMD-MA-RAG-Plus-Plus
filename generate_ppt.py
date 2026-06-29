import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color Palette Definitions
DARK_BG = RGBColor(15, 23, 42)        # Slate 900
LIGHT_BG = RGBColor(248, 250, 252)    # Slate 50
TEXT_PRIMARY = RGBColor(30, 41, 59)   # Slate 800
TEXT_MUTED = RGBColor(100, 116, 139)  # Slate 500
ACCENT_BLUE = RGBColor(14, 165, 233)   # Sky 500
ACCENT_TEAL = RGBColor(13, 148, 136)  # Teal 600
CARD_BG = RGBColor(255, 255, 255)     # White
CARD_BORDER = RGBColor(226, 232, 240) # Slate 200

# Helper function to set slide background color
def set_slide_bg(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

# Helper function to add a card shape
def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    return shape

# Helper function to add slide title
def add_slide_header(slide, title_text, category_text="MA-RAG FRAMEWORK"):
    # Category Tracker
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.name = "Arial"
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = ACCENT_BLUE
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = "Arial"
    p_title.font.size = Pt(28)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_PRIMARY

# Helper to format a paragraph with standard settings
def format_p(p, text, size=14, bold=False, color=TEXT_PRIMARY, space_after=6, align=PP_ALIGN.LEFT):
    p.text = text
    p.font.name = "Arial"
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.space_after = Pt(space_after)
    p.alignment = align

# ----------------- SLIDE 1: TITLE SLIDE (DARK THEME) -----------------
slide_layout = prs.slide_layouts[6] # Blank layout
slide1 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide1, DARK_BG)

# Title Decorative Line
line = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(2.2), Inches(2.0), Inches(0.08))
line.fill.solid()
line.fill.fore_color.rgb = ACCENT_BLUE
line.line.fill.background()

# Title and Subtitle Textbox
title_box = slide1.shapes.add_textbox(Inches(1.5), Inches(2.4), Inches(10.3), Inches(3.2))
tf = title_box.text_frame
tf.word_wrap = True

p1 = tf.paragraphs[0]
format_p(p1, "From Conflict to Consensus", size=46, bold=True, color=RGBColor(255, 255, 255), space_after=12)

p2 = tf.add_paragraph()
format_p(p2, "Boosting Multi-Domain Reasoning via Multi-Round Agentic RAG", size=22, bold=False, color=ACCENT_BLUE, space_after=24)

p3 = tf.add_paragraph()
format_p(p3, "A collaborative multi-agent debate framework with self-directed retrieval and consensus-guided safety barriers for high-stakes decision domains.", size=14, color=RGBColor(203, 213, 225))


# ----------------- SLIDE 2: THE CHALLENGE OF CRITICAL DOMAINS -----------------
slide2 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide2, LIGHT_BG)
add_slide_header(slide2, "The Challenge of Critical Domains", "Context & Motivation")

# Left Card: LLMs in High-Stakes Fields
add_card(slide2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
lc_box = slide2.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(4.4))
tf_lc = lc_box.text_frame
tf_lc.word_wrap = True

p_lc_h = tf_lc.paragraphs[0]
format_p(p_lc_h, "Critical Knowledge Domains", size=20, bold=True, color=ACCENT_TEAL, space_after=14)

points_lc = [
    ("Medical, Legal, & Financial sectors ", "demand absolute accuracy; false information can lead to severe harm, litigation, or financial ruin."),
    ("Hallucination Vulnerability: ", "LLMs frequently synthesize logical-sounding but factually incorrect details (e.g. wrong medication dosages, fake case laws, inaccurate tax rules)."),
    ("No Room for Guesswork: ", "Systems must acknowledge uncertainty and enforce rigorous evidence verification before providing advice.")
]
for title, text in points_lc:
    p = tf_lc.add_paragraph()
    format_p(p, "", size=14, space_after=10)
    run_title = p.add_run()
    run_title.text = title
    run_title.font.bold = True
    run_title.font.color.rgb = TEXT_PRIMARY
    run_text = p.add_run()
    run_text.text = text
    run_text.font.color.rgb = TEXT_PRIMARY

# Right Card: Traditional RAG Limitations
add_card(slide2, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.0))
rc_box = slide2.shapes.add_textbox(Inches(7.2), Inches(1.9), Inches(5.0), Inches(4.4))
tf_rc = rc_box.text_frame
tf_rc.word_wrap = True

p_rc_h = tf_rc.paragraphs[0]
format_p(p_rc_h, "Limitations of Standard RAG", size=20, bold=True, color=RGBColor(225, 29, 72), space_after=14) # Rose 600

points_rc = [
    ("Static Single-Turn Retrieval: ", "Fetches documents once based on the initial query. If the query is ambiguous, retrieval fails to capture relevant context."),
    ("Lack of Internal Consensus: ", "LLMs produce a single answer without exploring alternative perspectives, leading to confirmation bias."),
    ("No Safety Validation: ", "Vanilla RAG does not evaluate if the retrieved documents are conflicting or if the LLM's summary is highly confident.")
]
for title, text in points_rc:
    p = tf_rc.add_paragraph()
    format_p(p, "", size=14, space_after=10)
    run_title = p.add_run()
    run_title.text = title
    run_title.font.bold = True
    run_title.font.color.rgb = TEXT_PRIMARY
    run_text = p.add_run()
    run_text.text = text
    run_text.font.color.rgb = TEXT_PRIMARY


# ----------------- SLIDE 3: KEY ARCHITECTURAL INNOVATIONS -----------------
slide3 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide3, LIGHT_BG)
add_slide_header(slide3, "MA-RAG: Key Architectural Innovations", "System Capabilities")

# Three Column Cards
card_w = Inches(3.6)
card_h = Inches(4.8)
tops = Inches(1.8)

# Col 1: Multi-Agent Debate
add_card(slide3, Inches(0.8), tops, card_w, card_h)
col1_box = slide3.shapes.add_textbox(Inches(1.0), tops + Inches(0.3), card_w - Inches(0.4), card_h - Inches(0.6))
tf_col1 = col1_box.text_frame
tf_col1.word_wrap = True
format_p(tf_col1.paragraphs[0], "01 / Peer Debate Arena", size=18, bold=True, color=ACCENT_BLUE, space_after=12)
p_c1_sub = tf_col1.add_paragraph()
format_p(p_c1_sub, "Leverages specialized expert agent personas operating in parallel. By debating conflicting ideas, they discover omissions, refine logic, and self-correct factual errors during peer review.", size=13, color=TEXT_PRIMARY, space_after=10)

# Col 2: Self-Directed Search
add_card(slide3, Inches(4.8), tops, card_w, card_h)
col2_box = slide3.shapes.add_textbox(Inches(5.0), tops + Inches(0.3), card_w - Inches(0.4), card_h - Inches(0.6))
tf_col2 = col2_box.text_frame
tf_col2.word_wrap = True
format_p(tf_col2.paragraphs[0], "02 / Active Disagreement RAG", size=18, bold=True, color=ACCENT_TEAL, space_after=12)
p_c2_sub = tf_col2.add_paragraph()
format_p(p_c2_sub, "Analyzes agent disputes dynamically. Instead of static retrieval, the framework identifies core disagreements and generates precise queries to fetch targeted evidence from a local database.", size=13, color=TEXT_PRIMARY, space_after=10)

# Col 3: Safety Guardian
add_card(slide3, Inches(8.8), tops, card_w, card_h)
col3_box = slide3.shapes.add_textbox(Inches(9.0), tops + Inches(0.3), card_w - Inches(0.4), card_h - Inches(0.6))
tf_col3 = col3_box.text_frame
tf_col3.word_wrap = True
format_p(tf_col3.paragraphs[0], "03 / Safety Guardian Layer", size=18, bold=True, color=RGBColor(219, 39, 119), space_after=12) # Pink 600
p_c3_sub = tf_col3.add_paragraph()
format_p(p_c3_sub, "Acts as a strict gatekeeper. It evaluates the consensus and measures clinical/regulatory confidence. If confidence is low, it triggers a safety block rather than risking harmful hallucinations.", size=13, color=TEXT_PRIMARY, space_after=10)


# ----------------- SLIDE 4: SYSTEM ARCHITECTURE & FLOW -----------------
slide4 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide4, LIGHT_BG)
add_slide_header(slide4, "End-to-End Pipeline Architecture", "System Flow")

# Left Column: The Pipeline Description
add_card(slide4, Inches(0.8), Inches(1.6), Inches(4.2), Inches(5.0))
pipe_box = slide4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(3.8), Inches(4.6))
tf_pipe = pipe_box.text_frame
tf_pipe.word_wrap = True
format_p(tf_pipe.paragraphs[0], "Process Overview", size=20, bold=True, color=TEXT_PRIMARY, space_after=12)
steps = [
    ("1. Master Domain Router: ", "Classifies user query into Medical, Legal, Financial, or Other using LLM-based zero-shot routing."),
    ("2. Domain Arena Isolation: ", "Launches domain-specific models, keeping contexts and retrievers secure and separate."),
    ("3. Collaborative Resolution: ", "Engages the debate, critique, search, and validation loops until a high-confidence consensus is achieved.")
]
for title, text in steps:
    p = tf_pipe.add_paragraph()
    format_p(p, "", size=13, space_after=8)
    run_t = p.add_run()
    run_t.text = title
    run_t.font.bold = True
    run_t.font.color.rgb = ACCENT_BLUE
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY

# Right Area: Flow Diagram representation using Cards
add_card(slide4, Inches(5.4), Inches(1.6), Inches(7.1), Inches(5.0))
flow_box = slide4.shapes.add_textbox(Inches(5.7), Inches(1.8), Inches(6.5), Inches(4.6))
tf_flow = flow_box.text_frame
tf_flow.word_wrap = True

format_p(tf_flow.paragraphs[0], "Pipeline Flow Visualized", size=20, bold=True, color=ACCENT_TEAL, space_after=14)

p_f1 = tf_flow.add_paragraph()
format_p(p_f1, "[User Query]  -->  [Master Domain Router]", size=14, bold=True, color=TEXT_PRIMARY, space_after=8)
p_f1.alignment = PP_ALIGN.CENTER

p_f2 = tf_flow.add_paragraph()
format_p(p_f2, "      | (Routes to Classified Domain)", size=12, color=TEXT_MUTED, space_after=8)
p_f2.alignment = PP_ALIGN.CENTER

p_f3 = tf_flow.add_paragraph()
format_p(p_f3, "[3-Expert Personas] <--> [Peer Review/Critique] <--> [RAG Search on Disputes]", size=14, bold=True, color=TEXT_PRIMARY, space_after=8)
p_f3.alignment = PP_ALIGN.CENTER

p_f4 = tf_flow.add_paragraph()
format_p(p_f4, "      | (Debates & Refines Answers)", size=12, color=TEXT_MUTED, space_after=8)
p_f4.alignment = PP_ALIGN.CENTER

p_f5 = tf_flow.add_paragraph()
format_p(p_f5, "[Moderator Synthesis]  -->  [Consensus Judge & Safety Guardian]", size=14, bold=True, color=TEXT_PRIMARY, space_after=8)
p_f5.alignment = PP_ALIGN.CENTER

p_f6 = tf_flow.add_paragraph()
format_p(p_f6, "      | (Check Consensus & Confidence)", size=12, color=TEXT_MUTED, space_after=8)
p_f6.alignment = PP_ALIGN.CENTER

p_f7 = tf_flow.add_paragraph()
format_p(p_f7, "SUCCESS: [Consolidated Output]   ||   FAILURE: [Safety Block & Explanation]", size=14, bold=True, color=RGBColor(220, 38, 38), space_after=2)
p_f7.alignment = PP_ALIGN.CENTER


# ----------------- SLIDE 5: MEDICAL DEBATE ARENA - PERSONAS -----------------
slide5 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide5, LIGHT_BG)
add_slide_header(slide5, "Medical Debate Arena: Specialized Expert Personas", "Medical Domain Details")

card_w = Inches(3.6)
card_h = Inches(4.8)
tops = Inches(1.8)

# Expert A
add_card(slide5, Inches(0.8), tops, card_w, card_h)
box_a = slide5.shapes.add_textbox(Inches(1.0), tops + Inches(0.3), card_w - Inches(0.4), card_h - Inches(0.6))
tf_a = box_a.text_frame
tf_a.word_wrap = True
format_p(tf_a.paragraphs[0], "Expert A: Primary Care", size=18, bold=True, color=ACCENT_BLUE, space_after=12)
p_a = tf_a.add_paragraph()
format_p(p_a, "Focus areas:", size=14, bold=True, color=TEXT_PRIMARY, space_after=6)
bullets_a = [
    "Typical clinical presentations",
    "Standard diagnostic pathways",
    "First-line treatments & guidelines",
    "Patient-friendly explanations",
    "Actionable medication & dosage advice"
]
for b in bullets_a:
    p_b = tf_a.add_paragraph()
    format_p(p_b, "- " + b, size=13, color=TEXT_PRIMARY, space_after=4)

# Expert B
add_card(slide5, Inches(4.8), tops, card_w, card_h)
box_b = slide5.shapes.add_textbox(Inches(5.0), tops + Inches(0.3), card_w - Inches(0.4), card_h - Inches(0.6))
tf_b = box_b.text_frame
tf_b.word_wrap = True
format_p(tf_b.paragraphs[0], "Expert B: Specialist", size=18, bold=True, color=ACCENT_TEAL, space_after=12)
p_b_f = tf_b.add_paragraph()
format_p(p_b_f, "Focus areas:", size=14, bold=True, color=TEXT_PRIMARY, space_after=6)
bullets_b = [
    "Atypical clinical presentations",
    "Complex complications & risk factors",
    "Differential diagnosis analysis",
    "Identifying secondary diagnoses",
    "Less obvious clinical indicators"
]
for b in bullets_b:
    p_b = tf_b.add_paragraph()
    format_p(p_b, "- " + b, size=13, color=TEXT_PRIMARY, space_after=4)

# Expert C
add_card(slide5, Inches(8.8), tops, card_w, card_h)
box_c = slide5.shapes.add_textbox(Inches(9.0), tops + Inches(0.3), card_w - Inches(0.4), card_h - Inches(0.6))
tf_c = box_c.text_frame
tf_c.word_wrap = True
format_p(tf_c.paragraphs[0], "Expert C: Acute/Emergency", size=18, bold=True, color=RGBColor(162, 28, 175), space_after=12) # Purple 600
p_c_f = tf_c.add_paragraph()
format_p(p_c_f, "Focus areas:", size=14, bold=True, color=TEXT_PRIMARY, space_after=6)
bullets_c = [
    "Diagnostic investigations & tests",
    "Conservative & surgical options",
    "Urgent intervention indicators",
    "Critical warning signs (Red Flags)",
    "Safety netting instructions"
]
for b in bullets_c:
    p_b = tf_c.add_paragraph()
    format_p(p_b, "- " + b, size=13, color=TEXT_PRIMARY, space_after=4)


# ----------------- SLIDE 6: THE MULTI-ROUND COLLABORATIVE DEBATE LOOP -----------------
slide6 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide6, LIGHT_BG)
add_slide_header(slide6, "The Multi-Round Collaborative Debate Loop", "Process Details")

# Left Column: Stages description
add_card(slide6, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
lc6_box = slide6.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_lc6 = lc6_box.text_frame
tf_lc6.word_wrap = True

format_p(tf_lc6.paragraphs[0], "Detailed Debate Phases", size=20, bold=True, color=TEXT_PRIMARY, space_after=12)

stages = [
    ("Stage 1: Independent Answer Generation", "Experts produce their initial responses in parallel based on their specialized medical viewpoints (Primary, Specialist, Acute)."),
    ("Stage 2: Peer Review & Critique", "Experts analyze others' responses for clinical errors, omissions, and hallucinations. They revise their own text to defend or update positions."),
    ("Stage 3: Moderator Synthesis", "A consensus editor agent consolidates the debates, resolves conflicting statements, and outputs a single authoritative synthesis.")
]
for title, text in stages:
    p = tf_lc6.add_paragraph()
    format_p(p, "", size=13, space_after=8)
    run_t = p.add_run()
    run_t.text = title + "\n"
    run_t.font.bold = True
    run_t.font.color.rgb = ACCENT_BLUE
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY

# Right Column: Key Benefits
add_card(slide6, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.0))
rc6_box = slide6.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.0), Inches(4.6))
tf_rc6 = rc6_box.text_frame
tf_rc6.word_wrap = True

format_p(tf_rc6.paragraphs[0], "Why Multi-Agent Debate Works", size=20, bold=True, color=ACCENT_TEAL, space_after=12)

benefits = [
    ("Error Correction: ", "Hallucinations made by one LLM are caught and flagged by the other peer models during critique."),
    ("Balanced Reasoning: ", "Ensures a comprehensive view (e.g. including both common first-line treatments and red flags)."),
    ("Consensus Building: ", "Drives the separate expert agents towards alignment, eliminating arbitrary or model-specific biases."),
    ("Dosage & Citations: ", "Forces agents to verify and explicitly state specific regulations, codes, or medical dosages.")
]
for title, text in benefits:
    p = tf_rc6.add_paragraph()
    format_p(p, "", size=13, space_after=8)
    run_t = p.add_run()
    run_t.text = title
    run_t.font.bold = True
    run_t.font.color.rgb = TEXT_PRIMARY
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY


# ----------------- SLIDE 7: SELF-DIRECTED RAG SEARCH -----------------
slide7 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide7, LIGHT_BG)
add_slide_header(slide7, "Self-Directed Search & Verification", "Retrieval & Reranking")

# Left Column: Disagreement analysis
add_card(slide7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
lc7_box = slide7.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_lc7 = lc7_box.text_frame
tf_lc7.word_wrap = True

format_p(tf_lc7.paragraphs[0], "Targeting the Points of Dispute", size=20, bold=True, color=ACCENT_BLUE, space_after=14)

points_lc7 = [
    ("Conflict Identification: ", "When consensus isn't reached, a dedicated coordinator LLM analyzes previous answers to identify precise points of dispute."),
    ("Dynamic Query Generation: ", "Generates 1-4 targeted search queries specifically addressing the contested factual claims."),
    ("Fact-Finding: ", "Retrieves raw evidence to directly resolve conflicts rather than relying on static initial data.")
]
for title, text in points_lc7:
    p = tf_lc7.add_paragraph()
    format_p(p, "", size=14, space_after=10)
    run_t = p.add_run()
    run_t.text = title
    run_t.font.bold = True
    run_t.font.color.rgb = TEXT_PRIMARY
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY

# Right Column: Retriever system
add_card(slide7, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.0))
rc7_box = slide7.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.0), Inches(4.6))
tf_rc7 = rc7_box.text_frame
tf_rc7.word_wrap = True

format_p(tf_rc7.paragraphs[0], "Search & Reranking Stack", size=20, bold=True, color=ACCENT_TEAL, space_after=14)

points_rc7 = [
    ("BM25 Retrieval: ", "Fast, token-based lexical search queries a local domain corpus (e.g. MedCorp) to fetch relevant document candidates."),
    ("MedCPT Cross-Encoder Reranker: ", "A state-of-the-art semantic reranking model evaluates text pairs to yield the most contextually relevant evidence."),
    ("Test-Time Information Scaling: ", "Refines context dynamically round-by-round. Agents incorporate this high-confidence evidence into their subsequent responses.")
]
for title, text in points_rc7:
    p = tf_rc7.add_paragraph()
    format_p(p, "", size=14, space_after=10)
    run_t = p.add_run()
    run_t.text = title
    run_t.font.bold = True
    run_t.font.color.rgb = TEXT_PRIMARY
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY


# ----------------- SLIDE 8: CONSENSUS JUDGE & SAFETY GUARDIAN -----------------
slide8 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide8, LIGHT_BG)
add_slide_header(slide8, "Consensus Judge & Safety Guardian", "Safety & Validation")

# Left Column: Consensus Validation
add_card(slide8, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
lc8_box = slide8.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_lc8 = lc8_box.text_frame
tf_lc8.word_wrap = True

format_p(tf_lc8.paragraphs[0], "Consensus Evaluation", size=20, bold=True, color=ACCENT_BLUE, space_after=14)

points_lc8 = [
    ("Consensus Reached Check: ", "Determines whether all expert agents and the moderator align on the core advice and facts."),
    ("Factual Alignment: ", "Ensures there are no active disputes or contradictions in the final unified response."),
    ("Consolidated Output: ", "If consensus is reached, it yields a single comprehensive, high-quality, and verified response.")
]
for title, text in points_lc8:
    p = tf_lc8.add_paragraph()
    format_p(p, "", size=14, space_after=10)
    run_t = p.add_run()
    run_t.text = title
    run_t.font.bold = True
    run_t.font.color.rgb = TEXT_PRIMARY
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY

# Right Column: Safety Guardian
add_card(slide8, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.0))
rc8_box = slide8.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.0), Inches(4.6))
tf_rc8 = rc8_box.text_frame
tf_rc8.word_wrap = True

format_p(tf_rc8.paragraphs[0], "Guardian Confidence & Blocks", size=20, bold=True, color=RGBColor(220, 38, 38), space_after=14)

points_rc8 = [
    ("Confidence Scoring: ", "Classifies the collective medical or factual confidence into High, Medium, or Low."),
    ("Low-Confidence Safety Block: ", "If confidence is evaluated as Low, the Guardian triggers a safety block, refusing to provide advice."),
    ("Auditability: ", "Rather than failing silently, the Guardian outputs the specific reason for low confidence (e.g. contradictory literature, high uncertainty).")
]
for title, text in points_rc8:
    p = tf_rc8.add_paragraph()
    format_p(p, "", size=14, space_after=10)
    run_t = p.add_run()
    run_t.text = title
    run_t.font.bold = True
    run_t.font.color.rgb = TEXT_PRIMARY
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY


# ----------------- SLIDE 9: MULTI-DOMAIN EXPANSION (LEGAL & FINANCE) -----------------
slide9 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide9, LIGHT_BG)
add_slide_header(slide9, "Multi-Domain Expansion (Legal & Financial)", "System Versatility")

# Left Column: Legal Domain
add_card(slide9, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
lc9_box = slide9.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_lc9 = lc9_box.text_frame
tf_lc9.word_wrap = True

format_p(tf_lc9.paragraphs[0], "Legal Arena (Law-MA)", size=20, bold=True, color=ACCENT_BLUE, space_after=12)

points_lc9 = [
    ("Expert A (General Statutes): ", "Focuses on primary statutory interpretations, standard case precedents, and common guidelines."),
    ("Expert B (Corporate/Constitutional): ", "Focuses on secondary liability, complex statutory clauses, and strategic corporate risks."),
    ("Expert C (Litigation Defense): ", "Focuses on procedural defenses, jurisdictional constraints, and immediate client protection measures.")
]
for title, text in points_lc9:
    p = tf_lc9.add_paragraph()
    format_p(p, "", size=13, space_after=8)
    run_t = p.add_run()
    run_t.text = title
    run_t.font.bold = True
    run_t.font.color.rgb = TEXT_PRIMARY
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY

# Right Column: Financial Domain
add_card(slide9, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.0))
rc9_box = slide9.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.0), Inches(4.6))
tf_rc9 = rc9_box.text_frame
tf_rc9.word_wrap = True

format_p(tf_rc9.paragraphs[0], "Financial Arena (Finance-MA)", size=20, bold=True, color=ACCENT_TEAL, space_after=12)

points_rc9 = [
    ("Expert A (Financial Planner): ", "Focuses on standard asset allocation, retirement savings goals, and general market planning."),
    ("Expert B (Quantitative Analyst): ", "Focuses on modern portfolio theory, risk-adjusted metrics (Sharpe ratio, beta), and tax-optimized structures."),
    ("Expert C (Risk & Compliance): ", "Focuses on downside risk mitigation, wealth protection, regulatory compliance, and fraud detection.")
]
for title, text in points_rc9:
    p = tf_rc9.add_paragraph()
    format_p(p, "", size=13, space_after=8)
    run_t = p.add_run()
    run_t.text = title
    run_t.font.bold = True
    run_t.font.color.rgb = TEXT_PRIMARY
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY


# ----------------- SLIDE 10: RESULTS & CONCLUSION -----------------
slide10 = prs.slides.add_slide(slide_layout)
set_slide_bg(slide10, LIGHT_BG)
add_slide_header(slide10, "Experimental Results & Future Work", "Evaluation & Outlook")

# Left Card: Evaluation Results
add_card(slide10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
lc10_box = slide10.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
tf_lc10 = lc10_box.text_frame
tf_lc10.word_wrap = True

format_p(tf_lc10.paragraphs[0], "Experimental Findings (MedMCQA)", size=20, bold=True, color=ACCENT_TEAL, space_after=14)

points_lc10 = [
    ("Outperforms Baseline models: ", "Achieves significant accuracy improvements over standard zero-shot, multi-agent debate, and single-turn RAG."),
    ("Test-Time Scaling: ", "Performance scales with the number of debate rounds and query-guided retrieval loops, allowing control of inference compute."),
    ("Robust to Noise: ", "The multi-agent debate filters out incorrect or irrelevant evidence retrieved from the corpus.")
]
for title, text in points_lc10:
    p = tf_lc10.add_paragraph()
    format_p(p, "", size=14, space_after=10)
    run_t = p.add_run()
    run_t.text = title
    run_t.font.bold = True
    run_t.font.color.rgb = TEXT_PRIMARY
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY

# Right Card: Conclusion & Future Scope
add_card(slide10, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.0))
rc10_box = slide10.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.0), Inches(4.6))
tf_rc10 = rc10_box.text_frame
tf_rc10.word_wrap = True

format_p(tf_rc10.paragraphs[0], "Key Takeaways & Future Directions", size=20, bold=True, color=TEXT_PRIMARY, space_after=14)

points_rc10 = [
    ("Generalizable Framework: ", "Successfully expanded from Medical queries to Legal and Financial advisor domains."),
    ("Safety First: ", "Demonstrated that low-confidence blocks protect users from medical or legal advice failures."),
    ("Future Extensions: ", "Integration of multi-modal evidence (images, charts) and real-time citation tracking for absolute source auditing.")
]
for title, text in points_rc10:
    p = tf_rc10.add_paragraph()
    format_p(p, "", size=14, space_after=10)
    run_t = p.add_run()
    run_t.text = title
    run_t.font.bold = True
    run_t.font.color.rgb = TEXT_PRIMARY
    run_txt = p.add_run()
    run_txt.text = text
    run_txt.font.color.rgb = TEXT_PRIMARY

# Save the Presentation
prs.save("ma_rag_presentation.pptx")
print("Presentation saved successfully as ma_rag_presentation.pptx")
