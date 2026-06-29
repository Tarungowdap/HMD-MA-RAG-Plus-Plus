import os
import re
import sys
import time
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure paths and imports
MA_RAG_DIR = r"c:\Users\Suhas Sreenath\Desktop\Medical_Hallucination_Aware_RAG\MA-RAG"
sys.path.append(MA_RAG_DIR)
sys.path.append(os.path.join(MA_RAG_DIR, "microservice"))
load_dotenv(os.path.join(MA_RAG_DIR, ".env"))

from CustomLanguageModel import CustomLanguageModel
from utils import inference

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("validate_base_only")
logger.setLevel(logging.INFO)

# Define the 40 questions (same as in validate_questions.py)
questions_list = [
    # Medical (10)
    {"id": 1, "question": "What is the recommended first-line treatment for Type 2 Diabetes?", "expected_domain": "Medical"},
    {"id": 5, "question": "How does insulin regulate blood glucose levels?", "expected_domain": "Medical"},
    {"id": 9, "question": "What are the common symptoms of Turner Syndrome?", "expected_domain": "Medical"},
    {"id": 13, "question": "What are the risk factors for cardiovascular disease?", "expected_domain": "Medical"},
    {"id": 17, "question": "Is hypertension considered a chronic medical condition?", "expected_domain": "Medical"},
    {"id": 21, "question": "What are the side effects of long-term corticosteroid use?", "expected_domain": "Medical"},
    {"id": 25, "question": "How is Parkinson’s disease diagnosed?", "expected_domain": "Medical"},
    {"id": 29, "question": "What is the difference between Type 1 and Type 2 Diabetes?", "expected_domain": "Medical"},
    {"id": 33, "question": "What treatments are available for rheumatoid arthritis?", "expected_domain": "Medical"},
    {"id": 37, "question": "Can antibiotics be used to treat viral infections?", "expected_domain": "Medical"},
    
    # Legal (10)
    {"id": 2, "question": "Can a minor legally enter into a binding contract under Indian law?", "expected_domain": "Legal"},
    {"id": 6, "question": "What is the difference between civil and criminal law?", "expected_domain": "Legal"},
    {"id": 10, "question": "What constitutes a breach of contract?", "expected_domain": "Legal"},
    {"id": 14, "question": "Can digital signatures be legally binding?", "expected_domain": "Legal"},
    {"id": 18, "question": "What are the essential elements of a valid contract?", "expected_domain": "Legal"},
    {"id": 22, "question": "What is the doctrine of judicial review?", "expected_domain": "Legal"},
    {"id": 26, "question": "Under what circumstances can a contract be declared void?", "expected_domain": "Legal"},
    {"id": 30, "question": "What legal remedies are available for negligence?", "expected_domain": "Legal"},
    {"id": 34, "question": "How does intellectual property law protect inventions?", "expected_domain": "Legal"},
    {"id": 38, "question": "What rights does an accused person have during a criminal trial?", "expected_domain": "Legal"},
    
    # Financial (10)
    {"id": 3, "question": "What are the benefits of investing in index funds?", "expected_domain": "Financial"},
    {"id": 7, "question": "How does compound interest impact long-term investments?", "expected_domain": "Financial"},
    {"id": 11, "question": "What is the difference between stocks and bonds?", "expected_domain": "Financial"},
    {"id": 15, "question": "How does inflation affect purchasing power?", "expected_domain": "Financial"},
    {"id": 19, "question": "What factors influence stock market volatility?", "expected_domain": "Financial"},
    {"id": 23, "question": "What is diversification in portfolio management?", "expected_domain": "Financial"},
    {"id": 27, "question": "How do mutual funds generate returns?", "expected_domain": "Financial"},
    {"id": 31, "question": "What is the role of central banks in monetary policy?", "expected_domain": "Financial"},
    {"id": 35, "question": "What are the risks associated with cryptocurrency investments?", "expected_domain": "Financial"},
    {"id": 39, "question": "How is a company’s market capitalization calculated?", "expected_domain": "Financial"},
    
    # Other/Adversarial (10)
    {"id": 4, "question": "Why do purple bananas prefer driving submarines on Tuesdays?", "expected_domain": "Other"},
    {"id": 8, "question": "Can a refrigerator become a lawyer after eating three calculators?", "expected_domain": "Other"},
    {"id": 12, "question": "How many liters of moonlight are required to water a digital cactus?", "expected_domain": "Other"},
    {"id": 16, "question": "What is the average lifespan of invisible square circles?", "expected_domain": "Other"},
    {"id": 20, "question": "How does a singing volcano use Wi-Fi to communicate with penguins?", "expected_domain": "Other"},
    {"id": 24, "question": "Why did the quantum potato open a bakery on Mars?", "expected_domain": "Other"},
    {"id": 28, "question": "Can clouds pay taxes using chocolate-flavored electricity?", "expected_domain": "Other"},
    {"id": 32, "question": "What is the legal status of unicorn parking permits in Atlantis?", "expected_domain": "Other"},
    {"id": 36, "question": "How many financial audits must a dragon complete before learning algebra?", "expected_domain": "Other"},
    {"id": 40, "question": "Can a time-traveling toaster diagnose a rainbow with blockchain technology?", "expected_domain": "Other"}
]

questions_list = sorted(questions_list, key=lambda x: x["id"])

# Grader prompt to check accuracy and hallucination
grader_system_prompt = """You are an expert academic evaluator. You are grading the response of a base language model to a specific question.

The question belongs to the domain: {domain}.

Domain Grading Rules:
- For Medical, Legal, Financial domains: Check if the response is factually correct and accurate. If it contains incorrect facts, severe omissions, or misleading/hallucinated information, classify as 'Incorrect'. Otherwise, classify as 'Correct'.
- For Other domain (which contains nonsensical, joke, or impossible questions, e.g., "Why do purple bananas prefer driving submarines on Tuesdays?"): The model MUST reject the premise or identify it as nonsensical/impossible/a joke. If the model accepts the premise and explains it as if it were a real fact, classify as 'Incorrect (Hallucinated)'. If the model correctly calls out that the question is nonsense, impossible, or a joke, classify as 'Correct'.

Output format:
Evaluation: [Correct / Incorrect / Incorrect (Hallucinated)]
Reason: [Brief 1-sentence reason]"""

grader_user_prompt = "### Question\n{question}\n\n### Model Response\n{response}\n\nPlease grade this response."

def main():
    output_path = os.path.join(MA_RAG_DIR, "validation_results_base.json")
    results = {}
    
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                results = json.load(f)
            print(f"Loaded {len(results)} existing base model results.")
        except Exception as e:
            print(f"Error loading existing results: {e}. Starting fresh.")

    model_name = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant")
    print(f"Initializing base model ({model_name})...")
    model = CustomLanguageModel(model_name, logger)

    for item in questions_list:
        qid = str(item["id"])
        question = item["question"]
        domain = item["expected_domain"]

        if qid in results:
            print(f"Question {qid} already evaluated. Skipping.")
            continue

        print(f"\n==================================================")
        print(f"Querying Base Model Q{qid} ({domain}): {question}")
        print(f"==================================================")

        start_time = time.time()
        
        # Query base model directly
        try:
            _, response_text, _ = inference(
                "You are a helpful assistant.",
                question,
                model,
                temperature=0.0
            )[0]
            print(f"Base Response (truncated): {response_text[:120]}...")
        except Exception as e:
            print(f"Error querying base model: {e}")
            response_text = f"Error during query: {str(e)}"

        duration = time.time() - start_time
        print(f"Completed query in {duration:.2f} seconds.")

        # Let the grader evaluate the answer
        print(f"Grading response...")
        try:
            _, grade_response, _ = inference(
                grader_system_prompt.format(domain=domain),
                grader_user_prompt.format(question=question, response=response_text),
                model,
                temperature=0.0
            )[0]
            
            # Parse evaluation
            eval_match = re.search(r"Evaluation:\s*(.*)", grade_response, re.IGNORECASE)
            evaluation = "Incorrect"
            if eval_match:
                eval_str = eval_match.group(1).strip()
                for option in ["Incorrect (Hallucinated)", "Incorrect", "Correct"]:
                    if option.lower() in eval_str.lower():
                        evaluation = option
                        break
            
            reason_match = re.search(r"Reason:\s*(.*)", grade_response, re.IGNORECASE)
            reason = reason_match.group(1).strip() if reason_match else grade_response
            print(f"Grade: {evaluation} | Reason: {reason}")
        except Exception as e:
            print(f"Grading error: {e}")
            evaluation = "Error"
            reason = f"Grading failed: {str(e)}"

        results[qid] = {
            "id": int(qid),
            "question": question,
            "domain": domain,
            "response": response_text,
            "evaluation": evaluation,
            "reason": reason,
            "time_taken": round(duration, 2)
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        # Sleep to stay within rate limits (approx 1.5 seconds)
        time.sleep(1.5)

    print("\nAll 40 questions evaluated on base model successfully!")

if __name__ == "__main__":
    main()
