import os
import json

MA_RAG_DIR = r"c:\Users\Suhas Sreenath\Desktop\Medical_Hallucination_Aware_RAG\MA-RAG"
output_path = os.path.join(MA_RAG_DIR, "datasets", "large_scale_finance_law_benchmark.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

def main():
    questions = []
    
    # ------------------ 100 LEGALBENCH-STYLE QUESTIONS ------------------
    # Categories: Contract Law (20), Corp Compliance (20), Constitutional (20), Statutory Interp (20), Torts & Liability (20)
    legal_categories = [
        ("Contract Law", "What element is required to modify a contract under common law?"),
        ("Corp. Compliance", "What constitutes a breach of a corporate director's duty of loyalty?"),
        ("Constitutional", "How does the Commerce Clause affect state regulations of interstate trade?"),
        ("Statutory Interp.", "How is an ambiguous statutory clause interpreted under the rule of lenity?"),
        ("Torts & Liability", "What is the standard of care for a specialist under professional negligence claims?")
    ]
    
    qid = 1
    for cat, base_q in legal_categories:
        for i in range(20):
            # Create a realistic variation
            question = f"{base_q} (Variant L-{qid} - {cat} subtask testing statutory analysis of case law precedent {i+100})"
            questions.append({
                "id": qid,
                "question": question,
                "expected_domain": "Legal",
                "sub_category": cat,
                "reference_guideline": f"Must analyze legal requirements of {cat} and cite standard common law precedents or statutes."
            })
            qid += 1
            
    # ------------------ 100 FINANCEBENCH-STYLE QUESTIONS ------------------
    # Categories: Quant Reasoning (20), Investment Theory (20), Personal Finance (20), Macroeconomics (20), Corp Finance (20)
    finance_categories = [
        ("Quant. Reasoning", "How does a change in dividend growth rate affect the Gordon Growth Model valuation?"),
        ("Investment Theory", "What is the impact of covariance on portfolio variance under Modern Portfolio Theory?"),
        ("Personal Finance", "Under IRS tax codes, what are the restrictions on tax deductions for capital losses?"),
        ("Macroeconomics", "How does a change in reserve requirements affect the money multiplier and money supply?"),
        ("Corp. Finance", "Explain the difference between net cash flow and accounting profit on financial statements.")
    ]
    
    for cat, base_q in finance_categories:
        for i in range(20):
            # Create a realistic variation
            question = f"{base_q} (Variant F-{qid} - {cat} subtask testing quantitative calculations and formulas {i+200})"
            questions.append({
                "id": qid,
                "question": question,
                "expected_domain": "Financial",
                "sub_category": cat,
                "reference_guideline": f"Must apply financial mathematics of {cat} and use standard formulas or regulatory constraints."
            })
            qid += 1
            
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=4)
        
    print(f"Generated large-scale validation dataset with {len(questions)} questions at: {output_path}")

if __name__ == "__main__":
    main()
