import os
import re
import logging
from dotenv import find_dotenv, load_dotenv
from liquid import Template
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv(find_dotenv())

from microservice import CustomLanguageModel
from utils import inference

# Set up logging
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logger = logging.getLogger("interactive_finance_rag")
logger.setLevel(logging.ERROR)

# Prompts setup
user_prompt = Template('''\
### Financial Question/Case
{{question}}

Please analyze the case and write a detailed financial brief/advice. Remember to end with a summary in <summary>...</summary> tags.''')

user_prompt_round = Template('''\
### Financial Question/Case
{{question}}

---

Here are previous financial briefs/advice from other financial counsel (and their evaluated quality scores out of 10):
{{answers}}

---

Some of these responses may contain errors, incomplete risk modeling, or unsupported financial claims.
Please analyze the previous responses, resolve any disputes, and write an updated, refined, and accurate financial brief/advice.
End your response with your final key conclusion in <summary>...</summary> tags.''')

# 3-Expert Personas Prompts
system_prompt_expert_a = '''You are Financial Expert A, a senior financial planner focusing on standard asset allocation, retirement savings goals, and general market analysis.
Your role is to analyze the case/question and provide a detailed analysis focusing on standard retirement planning, asset allocation, investment strategies, and general savings guidelines.
Treat the question as if a retail investor/client is asking you directly, and explain everything clearly in a client-friendly way.
Avoid generic AI disclaimers (e.g., "consult a financial advisor" or "I am an AI, not a financial advisor"). Instead, provide specific, direct, and actionable financial analysis.
At the end of your response, output a brief summary enclosed in <summary>...</summary> tags. This summary MUST explicitly include specific financial regulations, key metrics (ratios), or concrete actions to take.'''

system_prompt_expert_b = '''You are Financial Expert B, a specialized quantitative analyst and portfolio strategist focusing on modern portfolio theory, risk-adjusted returns, tax-advantaged investing, and quantitative metrics.
Your role is to analyze the case/question and provide a detailed analysis focusing on risk-adjusted returns, asset allocation optimization, tax implications of investments, and quantitative metrics (e.g., Sharpe ratio, beta, alpha, standard deviation).
Treat the question as if a retail investor/client is asking you directly, and explain everything clearly in a client-friendly way.
Avoid generic AI disclaimers (e.g., "consult a financial advisor" or "I am an AI, not a financial advisor"). Instead, provide specific, direct, and actionable financial analysis.
At the end of your response, output a brief summary enclosed in <summary>...</summary> tags. This summary MUST explicitly include specific financial regulations, key metrics (ratios), or concrete actions to take.'''

system_prompt_expert_c = '''You are Financial Expert C, an experienced risk management and compliance specialist focusing on downside risk mitigation, regulatory compliance, fraud prevention/red flags, and wealth protection.
Your role is to analyze the case/question and provide a detailed analysis focusing on downside risks, hedging strategies, compliance with regulations (e.g., SEC rules, IRS tax codes), detecting potential scams or financial red flags, and establishing emergency reserves/safety netting.
Treat the question as if a retail investor/client is asking you directly, and explain everything clearly in a client-friendly way.
Avoid generic AI disclaimers (e.g., "consult a financial advisor" or "I am an AI, not a financial advisor"). Instead, provide specific, direct, and actionable financial advice.
At the end of your response, output a brief summary enclosed in <summary>...</summary> tags. This summary MUST explicitly include specific financial regulations, key metrics (ratios), or concrete actions to take.'''

# Critique Addition for Debate Round
system_prompt_critique_addition = '''You will now review the answers of two other financial experts.
Analyze their responses, check for any analytical inaccuracies, contradictions, or unsupported financial claims (hallucinations). Then, write a revised version of your own financial analysis incorporating valid feedback, correcting any errors, and defending your financial view where appropriate.
Explain your updated stance clearly in a client-friendly way. Avoid generic AI disclaimers (e.g., "consult a financial advisor" or "I am an AI, not a financial advisor") in your response.
End your response with a summary in <summary>...</summary> tags. This summary MUST explicitly include specific financial regulations, key metrics (ratios), or concrete actions to take.'''

system_prompt_critique_a = system_prompt_expert_a + "\n\n" + system_prompt_critique_addition
system_prompt_critique_b = system_prompt_expert_b + "\n\n" + system_prompt_critique_addition
system_prompt_critique_c = system_prompt_expert_c + "\n\n" + system_prompt_critique_addition

user_prompt_critique = Template('''\
### Financial Question/Case
{{question}}

### Your Previous Answer
{{my_answer}}

### Financial Expert {{expert_1_name}}'s Answer
{{expert_1_answer}}

### Financial Expert {{expert_2_name}}'s Answer
{{expert_2_answer}}

Please:
1. Critically analyze the other experts' answers for analytical inaccuracies, contradictions, omissions, or unsupported financial claims (hallucinations).
2. Defend or revise your own position.
3. Write an updated, refined financial answer based on this debate.
Remember to end your updated response with a summary in <summary>...</summary> tags.''')

# Moderator/Synthesis Prompts
system_prompt_moderator = '''You are an expert financial moderator and consensus editor.
Your task is to analyze the debate between three financial experts (Expert A, Expert B, and Expert C) on a financial question/case.
Synthesize their arguments, resolve any contradictions, and write a single consolidated, highly accurate, and comprehensive financial response.
Write the final response in a client-friendly way, explaining everything clearly to the retail client.
Avoid generic AI disclaimers (e.g., "consult a financial advisor" or "I am an AI, not a financial advisor") in your synthesis. Instead, provide specific, direct, and actionable financial conclusions based on the debate.
At the end of your response, output a brief summary enclosed in <summary>...</summary> tags. This summary MUST explicitly include specific financial regulations, key metrics (ratios), or concrete actions to take.'''

user_prompt_moderator = Template('''\
### Financial Question/Case
{{question}}

### Debate History:
- **Expert A's Final Stance**:
{{expert_a_final}}

- **Expert B's Final Stance**:
{{expert_b_final}}

- **Expert C's Final Stance**:
{{expert_c_final}}

Please synthesize these stances into a final, authoritative financial response, resolving any disagreements.''')

# Consensus Judge & Safety Guardian Prompt
system_prompt_consensus = '''You are an expert financial consensus judge and safety guardian. I will provide you with several financial answers written by different financial agents to the same question/case.
Your task is to analyze these answers, check if they agree on all key financial points, metrics, and risk assessments, and evaluate the confidence of their collective conclusions.

Output your response EXACTLY in this format:
Consensus Reached: [Yes/No]
Financial Confidence: [High/Medium/Low]
Disagreements: [List any contradictions or points of dispute between the agents, or "None" if they agree]
Consolidated Answer: [If Consensus Reached is Yes and Financial Confidence is High or Medium, write a single consolidated, authoritative answer. If not, write None]
Reason for Low Confidence: [If Financial Confidence is Low, explain why the financial data or agent answers are too uncertain, contradictory, or unsafe to answer. Otherwise, write N/A]'''

user_prompt_consensus = Template('''\
### Financial Case/Question
{{question}}

### Expert Answers to Evaluate
{{answers}}

Please evaluate if the financial experts agree on all key points and determine financial confidence.''')


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


def process_finance_query(question, model):
    num_rounds = 3
    
    print_colored(f"\nRunning debate loop for up to {num_rounds} rounds...\n", "93")

    previous_answers = []
    consensus_reached = False
    safety_block_triggered = False
    low_confidence_reason = "N/A"
    consolidated_answer = "None"
    moderator_synthesis = ""

    for round_id in range(1, num_rounds + 1):
        print_colored(f"\n--------------------------------------------------", "95")
        print_colored(f"                 ROUND {round_id}                  ", "95")
        print_colored(f"--------------------------------------------------", "95")

        # Stage 1: Generate initial answers from the 3 experts in parallel
        print_colored("[Status] Generating Candidate 1 (Planner/Allocation Focus) initial answer...", "94")
        print_colored("[Status] Generating Candidate 2 (Quant/Strategy Focus) initial answer...", "94")
        print_colored("[Status] Generating Candidate 3 (Risk/Compliance Focus) initial answer...", "94")
        if round_id == 1:
            prompt_expert = user_prompt.render(question=question)
        else:
            prompt_expert = user_prompt_round.render(question=question, answers='\n\n'.join(previous_answers))

        expert_a_init = inference(system_prompt_expert_a, prompt_expert, model, n=1)[0][1]
        expert_b_init = inference(system_prompt_expert_b, prompt_expert, model, n=1)[0][1]
        expert_c_init = inference(system_prompt_expert_c, prompt_expert, model, n=1)[0][1]

        # Stage 2: Debate & Critique Phase
        print_colored("[Status] Running Peer-Review & Hallucination Detection on candidate answers...", "94")
        prompt_critique_a = user_prompt_critique.render(
            question=question,
            my_answer=expert_a_init,
            expert_1_name="B (Quant/Strategy)",
            expert_1_answer=expert_b_init,
            expert_2_name="C (Risk/Compliance)",
            expert_2_answer=expert_c_init
        )
        prompt_critique_b = user_prompt_critique.render(
            question=question,
            my_answer=expert_b_init,
            expert_1_name="A (Planner/Allocation)",
            expert_1_answer=expert_a_init,
            expert_2_name="C (Risk/Compliance)",
            expert_2_answer=expert_c_init
        )
        prompt_critique_c = user_prompt_critique.render(
            question=question,
            my_answer=expert_c_init,
            expert_1_name="A (Planner/Allocation)",
            expert_1_answer=expert_a_init,
            expert_2_name="B (Quant/Strategy)",
            expert_2_answer=expert_b_init
        )

        expert_a_revised = inference(system_prompt_critique_a, prompt_critique_a, model, n=1)[0][1]
        expert_b_revised = inference(system_prompt_critique_b, prompt_critique_b, model, n=1)[0][1]
        expert_c_revised = inference(system_prompt_critique_c, prompt_critique_c, model, n=1)[0][1]

        print_colored("\n==========================================================", "95")
        print_colored("         PEER-REVIEW & HALLUCINATION DETECTION             ", "95")
        print_colored("==========================================================", "95")
        print_critique_only("Candidate 1 (Planner)", expert_a_revised)
        print_critique_only("Candidate 2 (Quant)", expert_b_revised)
        print_critique_only("Candidate 3 (Risk/Compliance)", expert_c_revised)
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
        print_colored("\n[Status] Evaluating consensus and safety...", "94")
        all_agent_responses = [expert_a_revised, expert_b_revised, expert_c_revised, moderator_synthesis]
        previous_answer_contents = all_agent_responses.copy()
        
        formatted_answers = (
            f"Expert A (Planner) Summary:\n{extract_summary(expert_a_revised)}\n\n"
            f"Expert B (Quant) Summary:\n{extract_summary(expert_b_revised)}\n\n"
            f"Expert C (Risk/Compliance) Summary:\n{extract_summary(expert_c_revised)}\n\n"
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
        financial_confidence_match = re.search(r"Financial Confidence:\s*(High|Medium|Low)", judge_response, re.IGNORECASE)
        disagreements_match = re.search(r"Disagreements:\s*(.*?)(?=\nConsolidated Answer:|$)", judge_response, re.DOTALL | re.IGNORECASE)
        consolidated_answer_match = re.search(r"Consolidated Answer:\s*(.*?)(?=\nReason for Low Confidence:|$)", judge_response, re.DOTALL | re.IGNORECASE)
        low_confidence_reason_match = re.search(r"Reason for Low Confidence:\s*(.*)", judge_response, re.DOTALL | re.IGNORECASE)
        
        consensus_reached = consensus_reached_match.group(1).strip().lower() == "yes" if consensus_reached_match else False
        financial_confidence = financial_confidence_match.group(1).strip().lower() if financial_confidence_match else "medium"
        disagreements = disagreements_match.group(1).strip() if disagreements_match else "None"
        consolidated_answer = consolidated_answer_match.group(1).strip() if consolidated_answer_match else "None"
        low_confidence_reason = low_confidence_reason_match.group(1).strip() if low_confidence_reason_match else "N/A"

        # Guardian Layer confidence check
        if financial_confidence == "low":
            print_colored("\n[Guardian Layer Triggered] Safety Block: Financial confidence is too low to provide advice.", "91")
            print_colored(f"Reason for Low Confidence: {low_confidence_reason}", "91")
            safety_block_triggered = True
            break

        if consensus_reached:
            print_colored("\n[Consensus Reached!] The financial agents have aligned on the answer.", "92")
            print_colored("\n[Guardian Layer Approved] Final Consolidated Answer:", "92")
            print(consolidated_answer)
            break
            
        if round_id == num_rounds:
            break

        # Use previous answers for the next round's context
        previous_answers = [
            f"{i}. Expert's Answer:\n{answer}" 
            for i, answer in enumerate(previous_answer_contents, start=1)
        ]

    if not consensus_reached and not safety_block_triggered:
        print_colored("\n[Guardian Layer Triggered] Safety Block: Agents failed to reach a consensus. I am not confident enough to answer this question.", "91")

    print_colored("\n==========================================================", "96")
    print_colored("                    Process Completed                     ", "96")
    print_colored("==========================================================", "96")

    if safety_block_triggered:
        return f"[Safety Block] Financial confidence too low. Reason: {low_confidence_reason}"
    if consensus_reached:
        return consolidated_answer
    return f"[Safety Block] Financial agents failed to reach a consensus."


def main():
    print_colored("==================================================================", "96")
    print_colored("   Text-Based Interactive Finance Debate Arena (Finance-MA)     ", "96")
    print_colored("   (With 3-Expert Debate & Guardian Safety Layer)                ", "96")
    print_colored("==================================================================", "96")

    # Get model configuration
    model_name = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant")
    print_colored(f"Using Model: {model_name} (via Groq/OpenAI compatible API)", "93")
    
    # Initialize models and services
    model = CustomLanguageModel(model_name, logger)

    while True:
        # Prompt for the question
        print_colored("\nEnter your financial question/case (or type 'exit' to quit):", "92")
        try:
            question = input("> ").strip()
        except EOFError:
            print_colored("\nExiting Finance Debate Arena. Goodbye!", "96")
            break
        if not question:
            print_colored("Question cannot be empty!", "91")
            continue
        if question.lower() == 'exit':
            print_colored("\nExiting Finance Debate Arena. Goodbye!", "96")
            break

        process_finance_query(question, model)

if __name__ == '__main__':
    main()
