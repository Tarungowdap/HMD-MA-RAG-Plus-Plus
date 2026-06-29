import os
import re
import numpy as np
from copy import deepcopy
from logging import Logger
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from time import sleep
from typing import List, Dict, Optional


EXTRA_BODY_MAP = {
    'qwen3-8b': {'chat_template_kwargs': {'enable_thinking': False}},
}

DEFAULT_EXTRA_BODY = {}

class CustomLanguageModel:
    def __init__(self, model_name_or_path: str, logger: Logger, base_url: Optional[str] = None):
        self.llm_name = model_name_or_path.split('/')[-1]
        self.max_retry_times = 30
        self.logger = logger
        actual_base_url = os.getenv('BASE_URL') if base_url is None else base_url
        self.is_groq = actual_base_url is not None and "groq.com" in actual_base_url
        self.client = OpenAI(
            api_key=os.getenv('API_KEY'),
            base_url=actual_base_url,
        )

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.6, max_new_tokens: int = 2048, top_logprobs: int = 0, enable_thinking: bool = False, continue_final_message: bool = False,  **kwargs) -> ChatCompletion:
        '''
        :param top_logprobs: 0 means not use logprobs, defaults to 0.
        '''
        extra_body = deepcopy(EXTRA_BODY_MAP.get(self.llm_name.lower(), DEFAULT_EXTRA_BODY))

        if self.is_groq:
            # Groq does not support vLLM's extra_body fields or logprobs
            extra_body = {}
            kwargs.pop('logprobs', None)
            kwargs.pop('top_logprobs', None)
        else:
            if enable_thinking:
                if 'chat_template_kwargs' not in extra_body:
                    extra_body['chat_template_kwargs'] = {}
                extra_body['chat_template_kwargs']['enable_thinking'] = True

            if 'top_k' in kwargs:
                extra_body['top_k'] = kwargs['top_k']
                del kwargs['top_k']

            if continue_final_message:
                extra_body['continue_final_message'] = True
                if 'chat_template_kwargs' not in extra_body:
                    extra_body['chat_template_kwargs'] = {}
                extra_body['chat_template_kwargs']['add_generation_prompt'] = False

            if top_logprobs:
                kwargs['logprobs'] = True
                kwargs['top_logprobs'] = top_logprobs

        for attempt in range(self.max_retry_times):
            try:
                params = {
                    "model": self.llm_name,
                    "messages": messages,
                    "temperature": temperature,
                    "max_completion_tokens": max_new_tokens,
                    "timeout": 600,
                    **kwargs,
                }
                if extra_body:
                    params["extra_body"] = extra_body

                if self.is_groq and params.get('n', 1) > 1:
                    n_times = params.pop('n')
                    from concurrent.futures import ThreadPoolExecutor

                    def run_single_request():
                        for att in range(self.max_retry_times):
                            try:
                                return self.client.chat.completions.create(**params)
                            except KeyboardInterrupt:
                                raise
                            except Exception as ex:
                                self.logger.warning(f"Error in single Groq request: {ex}. Retrying...")
                                match = re.search(r"try again in ([\d\.]+)s", str(ex), re.IGNORECASE)
                                if match:
                                    wait_time = float(match.group(1)) + 1.5
                                    sleep(wait_time)
                                else:
                                    sleep(min(30, 2 ** att * np.random.uniform(1.5, 3.0)))
                        raise TimeoutError(f"Failed to generate single Groq response after {self.max_retry_times} retries.")

                    with ThreadPoolExecutor(max_workers=n_times) as executor:
                        responses = list(executor.map(lambda _: run_single_request(), range(n_times)))

                    merged_choices = []
                    for i, resp in enumerate(responses):
                        choice = resp.choices[0]
                        choice.index = i
                        merged_choices.append(choice)

                    try:
                        final_response = responses[0].model_copy(update={"choices": merged_choices})
                    except AttributeError:
                        final_response = responses[0].copy(update={"choices": merged_choices})
                    return final_response
                else:
                    response = self.client.chat.completions.create(**params)
                    return response
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.logger.warning(f"Timeout/Error in generating response using {self.llm_name} model: {e}")
                match = re.search(r"try again in ([\d\.]+)s", str(e), re.IGNORECASE)
                if match:
                    wait_time = float(match.group(1)) + 1.5
                    sleep(wait_time)
                else:
                    sleep(min(30, 2 ** attempt * np.random.uniform(1.5, 3.0)))
        else:
            raise TimeoutError(f"Failed to generate response using {self.llm_name} model after {self.max_retry_times} retries.")

    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        '''
        Only return the generated response, without any additional information. Same parameters as `generate` method. (messages, temperature, max_new_tokens, top_logprobs, enable_thinking).

        :return: Generated response.
        '''
        response = self.generate(messages=messages, **kwargs)
        answer = response.choices[0].message.content
        if 'stop_reason' in response.choices[0].model_extra and response.choices[0].model_extra['stop_reason'] and answer:
            answer += response.choices[0].model_extra['stop_reason']
        return answer.strip()


if __name__ == '__main__':
    llm_name = 'qwen3-8b'
    model = CustomLanguageModel(llm_name)
    response = model.generate([{'role': 'user', 'content': 'Hello, how are you?'}], use_logprob=False)
    print(response)