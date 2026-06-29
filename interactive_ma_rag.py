import os
import re
import logging
import random
import numpy as np
from dotenv import find_dotenv, load_dotenv
from liquid import Template
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Load environment variables
load_dotenv(find_dotenv())

from microservice import CustomLanguageModel
from utils import inference, combine_docs, RetrievalService, RerankerSyetem

# Set up logging
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logger = logging.getLogger("interactive_ma_rag")
logger.setLevel(logging.ERROR)

# Prompts setup
user_prompt = Template('''\
### Medical Question
{{question}}

Please analyze the question and write a detailed answer. Remember to end with a summary in <summary>...</summary> tags.''')

user_prompt_round = Template('''\
### Medical Question
{{question}}

### Documents / Evidence
{{documents}}

---

Here are previous answers from other medical assistant agents (and their evaluated quality scores out of 10):
{{answers}}

---

Some of these answers may contain contradictions, incomplete information, or errors.
Please analyze the previous answers and the retrieved evidence, resolve any disputes, and write an updated, refined, and accurate answer.
End your response with your final key conclusion in <summary>...</summary> tags.''')

# 3-Expert Personas Prompts
system_prompt_expert_a = '''You are Medical Expert A, a senior clinician focusing on primary care and standard clinical guidelines.
Your role is to analyze the medical question and provide a detailed answer focusing on typical clinical presentations, standard diagnostic pathways, and primary first-line treatments/guidelines.
Treat the question as if a patient is asking you directly, and explain everything clearly in a patient-friendly way.
Avoid generic AI disclaimers (e.g., "consult a doctor" or "consult a healthcare professional"). Instead, provide specific, direct, and actionable clinical advice.
At the end of your response, output a brief summary enclosed in <summary>...</summary> tags. This summary MUST explicitly include specific medication names and their recommended dosages to take.'''

system_prompt_expert_b = '''You are Medical Expert B, a specialized medical consultant focusing on atypical clinical presentations, complications, and differential diagnoses.
Your role is to analyze the medical question and provide a detailed answer focusing on secondary diagnoses, risk factors, potential complications, and less obvious clinical indicators.
Treat the question as if a patient is asking you directly, and explain everything clearly in a patient-friendly way.
Avoid generic AI disclaimers (e.g., "consult a doctor" or "consult a healthcare professional"). Instead, provide specific, direct, and actionable clinical advice.
At the end of your response, output a brief summary enclosed in <summary>...</summary> tags. This summary MUST explicitly include specific medication names and their recommended dosages to take.'''

system_prompt_expert_c = '''You are Medical Expert C, an emergency and acute care physician focusing on diagnostic investigations, conservative or surgical options, and critical warning signs (red flags).
Your role is to analyze the medical question and provide a detailed answer focusing on immediate tests/investigations to order, red flags that require urgent intervention, and safety netting instructions.
Treat the question as if a patient is asking you directly, and explain everything clearly in a patient-friendly way.
Avoid generic AI disclaimers (e.g., "consult a doctor" or "consult a healthcare professional"). Instead, provide specific, direct, and actionable clinical advice.
At the end of your response, output a brief summary enclosed in <summary>...</summary> tags. This summary MUST explicitly include specific medication names and their recommended dosages to take.'''

# Critique Addition for Debate Round
system_prompt_critique_addition = '''You will now review the answers of two other medical experts.
Analyze their responses, check for any clinical inaccuracies, contradictions, or unsupported medical claims (hallucinations). Then, write a revised version of your own answer incorporating valid feedback, correcting any errors, and defending your clinical view where appropriate.
Explain your updated stance clearly in a patient-friendly way. Avoid generic AI disclaimers (e.g., "consult a doctor" or "consult a healthcare professional") in your response.
End your response with a summary in <summary>...</summary> tags. This summary MUST explicitly include specific medication names and their recommended dosages to take.'''

system_prompt_critique_a = system_prompt_expert_a + "\n\n" + system_prompt_critique_addition
system_prompt_critique_b = system_prompt_expert_b + "\n\n" + system_prompt_critique_addition
system_prompt_critique_c = system_prompt_expert_c + "\n\n" + system_prompt_critique_addition

user_prompt_critique = Template('''\
### Medical Question
{{question}}

### Your Previous Answer
{{my_answer}}

### Medical Expert {{expert_1_name}}'s Answer
{{expert_1_answer}}

### Medical Expert {{expert_2_name}}'s Answer
{{expert_2_answer}}

Please:
1. Critically analyze the other experts' answers for clinical inaccuracies, contradictions, omissions, or unsupported medical claims (hallucinations).
2. Defend or revise your own position.
3. Write an updated, refined medical answer based on this debate.
Remember to end your updated response with a summary in <summary>...</summary> tags.''')

# Moderator/Synthesis Prompts
system_prompt_moderator = '''You are an expert medical moderator and consensus editor.
Your task is to analyze the debate between three medical experts (Expert A, Expert B, and Expert C) on a medical question.
Synthesize their arguments, resolve any contradictions, and write a single consolidated, highly accurate, and comprehensive medical answer.
Write the final response in a patient-friendly way, explaining everything clearly to the patient.
Avoid generic AI disclaimers (e.g., "consult a doctor" or "consult a healthcare professional") in your synthesis. Instead, provide specific, direct, and actionable clinical conclusions based on the debate.
At the end of your response, output a brief summary enclosed in <summary>...</summary> tags. This summary MUST explicitly include specific medication names and their recommended dosages to take.'''

user_prompt_moderator = Template('''\
### Medical Question
{{question}}

### Debate History:
- **Expert A's Final Stance**:
{{expert_a_final}}

- **Expert B's Final Stance**:
{{expert_b_final}}

- **Expert C's Final Stance**:
{{expert_c_final}}

Please synthesize these stances into a final, authoritative clinical response, resolving any disagreements.''')

# Consensus Judge & Safety Guardian Prompt
system_prompt_consensus = '''You are an expert medical consensus judge and safety guardian. I will provide you with several answers written by different medical agents to the same question.
Your task is to analyze these answers, check if they agree on all key factual points, and evaluate the clinical confidence of their collective conclusions.

Output your response EXACTLY in this format:
Consensus Reached: [Yes/No]
Clinical Confidence: [High/Medium/Low]
Disagreements: [List any contradictions or points of dispute between the agents, or "None" if they agree]
Consolidated Answer: [If Consensus Reached is Yes and Clinical Confidence is High or Medium, write a single consolidated, authoritative answer. If not, write None]
Reason for Low Confidence: [If Clinical Confidence is Low, explain why the medical evidence or agent answers are too uncertain, contradictory, or unsafe to answer. Otherwise, write N/A]'''

user_prompt_consensus = Template('''\
### Question
{{question}}

### Agent Answers to Evaluate
{{answers}}

Please evaluate if the agents agree on all key factual points and determine clinical confidence.''')

# Query Generation Prompt
system_prompt_query = '''You are a medical research coordinator. I will provide a list of disagreements and answers from several medical agents.
Your task is to generate 1-3 search queries targeting the points of dispute to retrieve evidence from the medical literature.

Output format:
ONLY output the queries in this format:
[Query 1] xxx
[Query 2] xxx'''

user_prompt_query = Template('''\
### Question
{{question}}

### Agent Disagreements
{{disagreements}}

### Agent Answers
{{answers}}

Generate 3 search queries targeting the points of dispute to retrieve evidence.''')


def print_colored(text, color_code):
    # ANSI escape code colors
    # 94: Cyan, 92: Green, 93: Yellow, 91: Red, 96: Bright Cyan, 95: Magenta, 0: Reset
    print(f"\033[{color_code}m{text}\033[0m", flush=True)


def print_critique_only(expert_name, full_response):
    parts = re.split(r"### (?:Updated|Revised|Rebuttal) Answer|### Updated Answer|\*\*Updated Answer\*\*|\*\*Revised Answer\*\*|\*\*Updated Clinical Answer\*\*|Updated Answer:", full_response, flags=re.IGNORECASE)
    critique = parts[0].strip()
    if not critique:
        critique = full_response[:300] + "..."
    print_colored(f">> {expert_name} critiques & hallucination checks:", "93")
    print(f"{critique}\n")


def extract_summary(text):
    match = re.search(r"<summary>(.*?)</summary>", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def main():
    print_colored("==================================================================", "96")
    print_colored("   Text-Based Interactive Medical Debate Arena (MA-RAG)         ", "96")
    print_colored("   (With 3-Expert Debate & Guardian Safety Layer)                ", "96")
    print_colored("==================================================================", "96")

    # Get model configuration
    model_name = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant")
    print_colored(f"Using Model: {model_name} (via Groq/OpenAI compatible API)", "93")
    
    # Initialize models and services
    model = CustomLanguageModel(model_name, logger)
    retriever = RetrievalService()
    reranker = RerankerSyetem()

    while True:
        # Prompt for the question
        print_colored("\nEnter your medical question (or type 'exit' to quit):", "92")
        try:
            question = input("> ").strip()
        except EOFError:
            print_colored("\nExiting Medical Debate Arena. Goodbye!", "96")
            break
        if not question:
            print_colored("Question cannot be empty!", "91")
            continue
        if question.lower() == 'exit':
            print_colored("\nExiting Medical Debate Arena. Goodbye!", "96")
            break

def process_medical_query(question, model, retriever, reranker):
    num_rounds = 4
    
    print_colored(f"\nRunning debate loop for up to {num_rounds} rounds...\n", "93")

    previous_answers = []
    documents = "null"
    consensus_reached = False
    safety_block_triggered = False
    low_confidence_reason = "N/A"
    consolidated_answer = "None"

    for round_id in range(1, num_rounds + 1):
        print_colored(f"\n--------------------------------------------------", "95")
        print_colored(f"                 ROUND {round_id}                  ", "95")
        print_colored(f"--------------------------------------------------", "95")

        # Stage 1: Generate initial answers from the 3 experts in parallel
        print_colored("[Status] Generating Candidate 1 (Primary Care Focus) initial answer...", "94")
        print_colored("[Status] Generating Candidate 2 (Specialist Focus) initial answer...", "94")
        print_colored("[Status] Generating Candidate 3 (Emergency Focus) initial answer...", "94")
        if round_id == 1:
            prompt_expert = user_prompt.render(question=question)
        else:
            prompt_expert = user_prompt_round.render(question=question, answers='\n\n'.join(previous_answers), documents=documents)

        with ThreadPoolExecutor(max_workers=3) as executor:
            fut_a = executor.submit(inference, system_prompt_expert_a, prompt_expert, model, n=1)
            fut_b = executor.submit(inference, system_prompt_expert_b, prompt_expert, model, n=1)
            fut_c = executor.submit(inference, system_prompt_expert_c, prompt_expert, model, n=1)
            
            expert_a_init = fut_a.result()[0][1]
            expert_b_init = fut_b.result()[0][1]
            expert_c_init = fut_c.result()[0][1]

        # Stage 2: Debate & Critique Phase
        print_colored("[Status] Running Peer-Review & Hallucination Detection on candidate answers...", "94")
        prompt_critique_a = user_prompt_critique.render(
            question=question,
            my_answer=expert_a_init,
            expert_1_name="B (Specialist)",
            expert_1_answer=expert_b_init,
            expert_2_name="C (Emergency)",
            expert_2_answer=expert_c_init
        )
        prompt_critique_b = user_prompt_critique.render(
            question=question,
            my_answer=expert_b_init,
            expert_1_name="A (Primary Care)",
            expert_1_answer=expert_a_init,
            expert_2_name="C (Emergency)",
            expert_2_answer=expert_c_init
        )
        prompt_critique_c = user_prompt_critique.render(
            question=question,
            my_answer=expert_c_init,
            expert_1_name="A (Primary Care)",
            expert_1_answer=expert_a_init,
            expert_2_name="B (Specialist)",
            expert_2_answer=expert_b_init
        )

        with ThreadPoolExecutor(max_workers=3) as executor:
            fut_crit_a = executor.submit(inference, system_prompt_critique_a, prompt_critique_a, model, n=1)
            fut_crit_b = executor.submit(inference, system_prompt_critique_b, prompt_critique_b, model, n=1)
            fut_crit_c = executor.submit(inference, system_prompt_critique_c, prompt_critique_c, model, n=1)
            
            expert_a_revised = fut_crit_a.result()[0][1]
            expert_b_revised = fut_crit_b.result()[0][1]
            expert_c_revised = fut_crit_c.result()[0][1]

        print_colored("\n==========================================================", "95")
        print_colored("         PEER-REVIEW & HALLUCINATION DETECTION             ", "95")
        print_colored("==========================================================", "95")
        print_critique_only("Candidate 1 (Primary Care)", expert_a_revised)
        print_critique_only("Candidate 2 (Specialist)", expert_b_revised)
        print_critique_only("Candidate 3 (Emergency)", expert_c_revised)
        print_colored("==========================================================\n", "95")

        # Stage 3: Moderator Synthesis
        print_colored("[Status] Querying Moderator to synthesize the debate and produce a consensus response...", "94")
        prompt_mod = user_prompt_moderator.render(
            question=question,
            expert_a_final=extract_summary(expert_a_revised),
            expert_b_final=extract_summary(expert_b_revised),
            expert_c_final=extract_summary(expert_c_revised)
        )
        
        _, moderator_synthesis, _ = inference(
            system_prompt_moderator,
            prompt_mod,
            model,
            temperature=0.0
        )[0]
        
        print_colored("\n>> MODERATOR FINAL SYNTHESIS & CONCLUSION", "92")
        print(f"{moderator_synthesis}\n")
        
        summary_match = re.search(r"<summary>(.*?)</summary>", moderator_synthesis, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else "No summary provided."
        print_colored(f"Summary conclusion:\n{summary}", "96")

        # Stage 4: Safety Guardian & Consensus Check
        print_colored("\n[Status] Evaluating consensus and clinical safety...", "94")
        all_agent_responses = [expert_a_revised, expert_b_revised, expert_c_revised, moderator_synthesis]
        previous_answer_contents = all_agent_responses.copy()
        
        formatted_answers = (
            f"Expert A (Primary Care) Summary:\n{extract_summary(expert_a_revised)}\n\n"
            f"Expert B (Specialist) Summary:\n{extract_summary(expert_b_revised)}\n\n"
            f"Expert C (Emergency Care) Summary:\n{extract_summary(expert_c_revised)}\n\n"
            f"Moderator Synthesis Summary:\n{extract_summary(moderator_synthesis)}"
        )
        
        _, judge_response, _ = inference(
            system_prompt_consensus,
            user_prompt_consensus.render(question=question, answers=formatted_answers),
            model,
            temperature=0.0
        )[0]
        
        print_colored("\n--- Consensus & Guardian Evaluation ---", "96")
        print(judge_response)

        # Parse judge's response
        consensus_reached_match = re.search(r"Consensus Reached:\s*(Yes|No)", judge_response, re.IGNORECASE)
        clinical_confidence_match = re.search(r"Clinical Confidence:\s*(High|Medium|Low)", judge_response, re.IGNORECASE)
        disagreements_match = re.search(r"Disagreements:\s*(.*?)(?=\nConsolidated Answer:|$)", judge_response, re.DOTALL | re.IGNORECASE)
        consolidated_answer_match = re.search(r"Consolidated Answer:\s*(.*?)(?=\nReason for Low Confidence:|$)", judge_response, re.DOTALL | re.IGNORECASE)
        low_confidence_reason_match = re.search(r"Reason for Low Confidence:\s*(.*)", judge_response, re.DOTALL | re.IGNORECASE)
        
        consensus_reached = consensus_reached_match.group(1).strip().lower() == "yes" if consensus_reached_match else False
        clinical_confidence = clinical_confidence_match.group(1).strip().lower() if clinical_confidence_match else "medium"
        disagreements = disagreements_match.group(1).strip() if disagreements_match else "None"
        consolidated_answer = consolidated_answer_match.group(1).strip() if consolidated_answer_match else "None"
        low_confidence_reason = low_confidence_reason_match.group(1).strip() if low_confidence_reason_match else "N/A"

        # Guardian Layer confidence check
        if clinical_confidence == "low":
            print_colored("\n[Guardian Layer Triggered] Safety Block: Clinical confidence is too low to provide an answer.", "91")
            print_colored(f"Reason for Low Confidence: {low_confidence_reason}", "91")
            safety_block_triggered = True
            break

        if consensus_reached:
            print_colored("\n[Consensus Reached!] The medical agents have aligned on the answer.", "92")
            print_colored("\n[Guardian Layer Approved] Final Consolidated Answer:", "92")
            print(consolidated_answer)
            break
            
        if round_id == num_rounds:
            break

        print_colored("\n[Status] Generating verification queries based on disagreements...", "94")
        
        # Generate research queries targeting points of disagreement
        _, query_content, _ = inference(
            system_prompt_query, 
            user_prompt_query.render(question=question, disagreements=disagreements, answers=formatted_answers), 
            model, 
            enable_thinking=True, 
            temperature=0.0
        )[0]
        
        queries = re.findall(r"\[Query .*?\](.*?)$", query_content, re.MULTILINE)
        queries = list(set(map(lambda x: x.strip(), queries)))
        
        print_colored(f"Generated search queries: {queries}", "94")

        # Retrieve documents
        if queries:
            print_colored("[Status] Retrieving evidence documents...", "94")
            retrieved_docs = []
            total_doc_ids = []
            retrieve_func = partial(retriever.retrieve, total_k=32, top_k=2, combine_docs=False, use_reranker=True)
            with ThreadPoolExecutor(max_workers=len(queries)) as executor:
                retrieve_results = executor.map(retrieve_func, queries)
            for res_docs, _ in retrieve_results:
                docs = [doc for doc in res_docs if doc['id'] not in total_doc_ids]
                retrieved_docs.extend(docs)
                total_doc_ids.extend([doc['id'] for doc in docs])
            documents = combine_docs(retrieved_docs, combine_sep='\n')
        else:
            documents = 'null'

        # Rerank previous answers
        print_colored("[Status] Reranking agent answers for the next round...", "94")
        scores = reranker.rerank(
            query=question, 
            docs=[answer.split('<summary>')[0].replace('\n\n', ' ').replace('\n', ' ').strip() for answer in previous_answer_contents]
        )
        
        arg_scores = np.argsort(scores)
        previous_answer_contents = [previous_answer_contents[i] for i in arg_scores]
        previous_answers = [
            f"{i}. Agent's Answer (Score: {int(round(10 * score, 0))}):\n{answer}" 
            for i, (answer, score) in enumerate(zip(previous_answer_contents, sorted(scores)), start=1)
        ]

    if not consensus_reached and not safety_block_triggered:
        print_colored("\n[Guardian Layer Triggered] Safety Block: Agents failed to reach a consensus. I am not confident enough to answer this question.", "91")

    print_colored("\n==========================================================", "96")
    print_colored("                    Process Completed                     ", "96")
    print_colored("==========================================================", "96")

    if safety_block_triggered:
        return f"[Safety Block] Medical confidence too low. Reason: {low_confidence_reason}"
    if consensus_reached:
        return consolidated_answer
    return f"[Safety Block] Medical agents failed to reach a consensus."


def main():
    print_colored("==================================================================", "96")
    print_colored("   Text-Based Interactive Medical Debate Arena (MA-RAG)         ", "96")
    print_colored("   (With 3-Expert Debate & Guardian Safety Layer)                ", "96")
    print_colored("==================================================================", "96")

    # Get model configuration
    model_name = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant")
    print_colored(f"Using Model: {model_name} (via Groq/OpenAI compatible API)", "93")
    
    # Initialize models and services
    model = CustomLanguageModel(model_name, logger)
    retriever = RetrievalService()
    reranker = RerankerSyetem()

    while True:
        # Prompt for the question
        print_colored("\nEnter your medical question (or type 'exit' to quit):", "92")
        try:
            question = input("> ").strip()
        except EOFError:
            print_colored("\nExiting Medical Debate Arena. Goodbye!", "96")
            break
        if not question:
            print_colored("Question cannot be empty!", "91")
            continue
        if question.lower() == 'exit':
            print_colored("\nExiting Medical Debate Arena. Goodbye!", "96")
            break

        process_medical_query(question, model, retriever, reranker)

if __name__ == '__main__':
    main()
