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

# Standalone imports from domain modules
from interactive_ma_rag import process_medical_query, print_colored
from interactive_law_rag import process_legal_query
from interactive_finance_rag import process_finance_query

# Set up logging
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logger = logging.getLogger("interactive_master_rag")
logger.setLevel(logging.ERROR)

# Routing Prompts setup
system_prompt_router = '''You are a master domain classification agent. Your task is to analyze the user's query and classify it into one or more of these four categories:
1. "Medical": If the query is about health symptoms, medical diagnoses, clinical guidelines, first aid, medications, or health advice.
2. "Legal": If the query is about laws, statutes, litigation, court cases, regulations, legal advice, or client protection measures.
3. "Financial": If the query is about investing, tax, retirement planning, budgeting, asset allocation, portfolio strategies, or risk management.
4. "Other": If the query does not fit any of the above domains.

Output your classification strictly in this format:
Domains: [List of domains, comma-separated, e.g. Medical, Legal]
Reason: [Brief explanation of why the query belongs to these categories]'''

user_prompt_router = Template('''### User Query
{{query}}

Please classify this query.''')

# Summarizer Prompts setup
system_prompt_summarizer = '''You are a master synthesis and summarization agent. 
Your task is to analyze the user's original query and the comprehensive answers provided by specialized domain-specific agents (Medical, Legal, and Financial).
Compile these answers into a single, cohesive, structured, and easy-to-read response. 
Make sure to:
1. Retain the critical details, guidelines, citations, and specific advice from each domain.
2. Group the information logically (e.g., under headers like "Medical Analysis", "Legal Implications", "Financial Plan").
3. Provide a unified executive summary at the very end of your response.
4. Avoid generic AI disclaimers (e.g., "consult a professional"). Act as the final consolidated expert advisor.'''

user_prompt_summarizer = Template('''### Original User Query
{{query}}

### Answers from Domain Agents
{{answers}}

Please synthesize the above answers.''')

# Lazily initialized medical services
retriever = None
reranker = None

def main():
    global retriever, reranker

    print_colored("==================================================================", "96")
    print_colored("   Text-Based Multi-Domain Master Agent (Medical/Legal/Finance) ", "96")
    print_colored("   (With Multi-Agent Debate Arena & Guardian Safety Layers)      ", "96")
    print_colored("==================================================================", "96")

    # Get model configuration
    model_name = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant")
    print_colored(f"Using Model: {model_name} (via Groq/OpenAI compatible API)", "93")
    
    # Initialize master routing model
    model = CustomLanguageModel(model_name, logger)

    while True:
        # Prompt for the question
        print_colored("\nEnter your question/case (or type 'exit' to quit):", "92")
        try:
            question = input("> ").strip()
        except EOFError:
            print_colored("\nExiting Master Agent. Goodbye!", "96")
            break
        if not question:
            print_colored("Question cannot be empty!", "91")
            continue
        if question.lower() == 'exit':
            print_colored("\nExiting Master Agent. Goodbye!", "96")
            break

        # Classify the query using the Router Agent
        print_colored("[Status] Routing query to domain classifier...", "94")
        _, router_response, _ = inference(
            system_prompt_router,
            user_prompt_router.render(query=question),
            model,
            temperature=0.0
        )[0]

        # Parse classification response
        domains_match = re.search(r"Domains?:\s*(.*)", router_response, re.IGNORECASE)
        detected_domains = []
        if domains_match:
            domains_str = domains_match.group(1)
            for d in ["Medical", "Legal", "Financial", "Other"]:
                if re.search(r"\b" + d + r"\b", domains_str, re.IGNORECASE):
                    detected_domains.append(d)
        if not detected_domains:
            detected_domains = ["Other"]

        # If there are multiple domains and "Other" is in there, remove "Other"
        if len(detected_domains) > 1 and "Other" in detected_domains:
            detected_domains.remove("Other")

        print_colored(f"[Status] Router classified query as: {', '.join(detected_domains)}", "93")

        domain_answers = {}

        # Lazy initialize medical retrieval to maintain isolation
        if "Medical" in detected_domains and retriever is None:
            print_colored("[Status] Lazily initializing Medical database & reranker...", "94")
            from utils import RetrievalService, RerankerSyetem
            retriever = RetrievalService()
            reranker = RerankerSyetem()

        # Helper function to execute a single domain agent in a thread
        def run_domain_agent(dom):
            if dom == "Medical":
                print_colored(f"\n[Starting Medical domain agent...]", "96")
                ans = process_medical_query(question, model, retriever, reranker)
                return dom, ans
            elif dom == "Legal":
                print_colored(f"\n[Starting Legal domain agent...]", "96")
                ans = process_legal_query(question, model)
                return dom, ans
            elif dom == "Financial":
                print_colored(f"\n[Starting Financial domain agent...]", "96")
                ans = process_finance_query(question, model)
                return dom, ans
            return dom, None

        # Execute corresponding isolated domain flows in parallel
        valid_domains = [d for d in detected_domains if d in ["Medical", "Legal", "Financial"]]
        if valid_domains:
            print_colored(f"\n[Status] Executing domains in parallel: {', '.join(valid_domains)}...", "94")
            with ThreadPoolExecutor(max_workers=len(valid_domains)) as executor:
                futures = [executor.submit(run_domain_agent, d) for d in valid_domains]
                for future in futures:
                    dom_name, ans = future.result()
                    if ans is not None:
                        domain_answers[dom_name] = ans
        else:
            if "Other" in detected_domains or not detected_domains:
                print_colored("\n[Router Message] Sorry, I can only assist with Medical, Legal, or Financial queries.", "91")
                print_colored("Please try asking a question within one of those domains.", "91")

        # Synthesize answers if there are multiple domains
        if len(domain_answers) > 1:
            print_colored("\n[Status] Running Summarize Agent to synthesize responses across domains...", "94")
            formatted_answers = "\n".join([
                f"---\n#### {domain} Agent Answer:\n{answer}"
                for domain, answer in domain_answers.items()
            ])
            _, summary_response, _ = inference(
                system_prompt_summarizer,
                user_prompt_summarizer.render(query=question, answers=formatted_answers),
                model,
                temperature=0.0
            )[0]
            print_colored("\n==========================================================", "96")
            print_colored("                FINAL MULTI-DOMAIN SUMMARY                 ", "96")
            print_colored("==========================================================", "96")
            print(summary_response)
            print_colored("==========================================================", "96")
        elif len(domain_answers) == 1:
            domain_name = list(domain_answers.keys())[0]
            print_colored(f"\n[Status] Showing final response from {domain_name} Agent:", "92")
            print(domain_answers[domain_name])

if __name__ == '__main__':
    main()
