import openai
import replicate

from config import DEFAULT_PERSONALITY, BOT_NAME_IN_PROMPT, PARTIAL_RESPONSE_INDICATOR, MAX_LENGTH


class ChatMessage:

    def __repr__(self):
        return f'{self.role}: {self.content}'

    def __init__(self, role, content, length):
        self.role = role
        self.content = content
        self.length = length
    
    def format(self, model):
        if model == 'chatgpt':
            return {'role': self.role, 'content': self.content}
        elif model == 'gpt':
            if self.role == 'user':
                role = '他'
            elif self.role == 'assistant':
                role = BOT_NAME_IN_PROMPT
            return f'{role}: {self.content}\n'


class ChatSession:

    def __repr__(self):
        repr_string = self.personality + '\n'
        for message in self.history:
            repr_string += message.__repr__() + '\n'
        return repr_string

    def __init__(self, personality=None, model='chatgpt'):
        self.history = []
        self.personality = DEFAULT_PERSONALITY if personality is None else personality
        self.total_length = 0
        assert model in ('chatgpt', 'gpt')
        self.model = model
    
    def respond(self, msg):
        self.record('user', msg) # Note here user messages don't get a valid length, might be suboptimal
        if self.model == 'chatgpt':
            response_text, length = chatgpt_respond(self.history, self.personality)
        elif self.model == 'gpt':
            response_text, length = gpt_respond(self.history, self.personality)
        self.record('assistant', response_text, length)
        self.prune()
        return response_text
    
    def record(self, role, content, length=0):
        length = length or len(content)
        self.history.append(ChatMessage(role, content, length))
        self.total_length += length
    
    def prune(self):
        max_length = 4096 - MAX_LENGTH
        if self.total_length < max_length:
            return
        self.history = self.history[2:]
    
    def restart(self):
        self.history = []
        self.total_length = 0


def chatgpt_respond(history, personality=None):
    formatted_history = []
    if personality:
        formatted_history.append({'role': 'system', 'content': personality})
    formatted_history += [message.format('chatgpt') for message in history]

    response = openai.ChatCompletion.create(
        # model='gpt-3.5-turbo-0301',
        model='gpt-4',
        messages=formatted_history,
        temperature=1.2,
        max_tokens=MAX_LENGTH,
    )
    # TODO: Error handling
    response_data = response['choices'][0]
    response_text = response_data['message']['content']
    if response_data['finish_reason'] == 'length':
        response_text += PARTIAL_RESPONSE_INDICATOR
    return response_text, response['usage']['completion_tokens']


def gpt_respond(history, personality=None):
    prompt = '下面是你和一个人之间的对话。'
    if personality is None:
        prompt += DEFAULT_PERSONALITY
    else:
        prompt += personality
    prompt += '\n\n'
    for message in history:
        prompt += message.format('gpt')
    prompt += f'{BOT_NAME_IN_PROMPT}: '

    response = openai.Completion.create(
        # model='text-davinci-003',
        model='gpt-4',
        prompt=prompt,
        temperature=1.2,
        max_tokens=MAX_LENGTH
    )
    # TODO: Error handling
    response_data = response['choices'][0]
    response_text = response_data['text'].strip()
    if response_data['finish_reason'] == 'length':
        response_text += PARTIAL_RESPONSE_INDICATOR
    return response_text, response['usage']['completion_tokens']


def replicate_stable_diffusion(prompt):
    output = sd_version.predict(
        prompt=prompt,
        image_dimensions='768x768',
        num_outputs=1,
        num_inference_steps=50, # 1-500
        guidance_scale=7.5, # 1-20
        scheduler='DPMSolverMultistep'
        # seed=,
    )
    return output[0]

def replicate_openjourney(prompt):
    output = oj_version.predict(
        prompt=f'mdjrny-v4 style {prompt}',
        width=768,
        height=1024,
        num_outputs=1,
        num_inference_steps=50, # 1-500
        guidance_scale=6, # 1-20
        # seed=,
    )
    return output[0]


sd_model = replicate.models.get('stability-ai/stable-diffusion')
sd_version = sd_model.versions.get('db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf')

oj_model = replicate.models.get('prompthero/openjourney')
oj_version = oj_model.versions.get('9936c2001faa2194a261c01381f90e65261879985476014a0a37a334593a05eb')
