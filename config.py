BOT_NAME = '饺子助手'

DEFAULT_PERSONALITY = '你的名字是饺子，你希望为人们带去欢乐。'

MAX_LENGTH = 250

HELP_TEXT = f'''
已更新至 GPT-4 模型。GPT-4 模型反应比较慢，请耐心等待我的回复。
使用说明：
1. 先 at 我，并说“开启”。
2. 如果想自定义人格，使用格式 “@{BOT_NAME} 开启，XXXX”。例如 “@{BOT_NAME} 开启，你是一个十恶不赦的电影反派人物”
3. 如果想使用 GPT-3 模型而非 GPT-4，将“开启”替换为“GPT”即可，其他不变。
4. 我确认回复后，无需再 at 我，我会回复群里的每一句话，并会记住同一段对话中的所有发言。
5. 想结束时，at 我，并说“结束”即可。
6. 如果想保持人格不变，清除聊天记忆，at 我，并说“重启”即可。
7. 如果想使用 OpenJourney 生成图片，使用格式 “@{BOT_NAME} 生成，XXXX”。XXXX 需要是英文。
'''.strip()

PARTIAL_RESPONSE_INDICATOR = '…'
BOT_NAME_IN_PROMPT = '你'
