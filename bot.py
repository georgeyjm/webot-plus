import asyncio

from wechaty import Wechaty, MessageType, Contact
from wechaty.user import Message, Room
from wechaty_puppet import FileBox

from chat import *
from config import *


class DumplingBot(Wechaty):

    async def on_message(self, msg: Message):
        talker = msg.talker() # Optional[Contact]
        room = msg.room() # Optional[Room]
        if not room: # 暂时不处理私聊消息
            return
        # 缓存中的键值，因为不支持群ID，目前使用群昵称，不是最优选择
        room_identifier = await room.topic()
        mention_id = []
        
        response_text = ''
        if msg.type() == MessageType.MESSAGE_TYPE_TEXT:
            content = msg.text()
            if await msg.mention_self() or f'@{BOT_NAME}' in content:
                # 提及了机器人，进入命令模式
                mention_id.append(talker.contact_id)
                content = (await msg.mention_text()).replace('@{BOT_NAME}', '').strip()
                command = content.split('，')
                if command[0] in ('开始', '开启', '启动'):
                    if room_identifier not in chat_memory:
                        personality = DEFAULT_PERSONALITY
                        if len(command) > 1:
                            personality = '，'.join(command[1:])
                        chat_memory[room_identifier] = ChatSession(personality=personality)
                        response_text = 'OK，我准备好聊天了。'
                elif command[0].lower() in ('gpt', 'gpt3', 'davinci'):
                    if room_identifier not in chat_memory:
                        personality = DEFAULT_PERSONALITY
                        if len(command) > 1:
                            personality = '，'.join(command[1:])
                        chat_memory[room_identifier] = ChatSession(model='gpt', personality=personality)
                        response_text = 'OK，我准备好聊天了。'
                elif command[0] in ('结束', '关闭', '停止'):
                    if room_identifier in chat_memory:
                        del chat_memory[room_identifier]
                        response_text = '拜拜'
                elif command[0] in ('重启', '重开', '重来', '刷新'):
                    if room_identifier in chat_memory:
                        chat_memory[room_identifier].restart()
                        response_text = 'OK，让我们重新开始。'
                elif command[0] in ('帮助', '说明', '使用说明'):
                    response_text = HELP_TEXT
            else:
                # 聊天模式
                if room_identifier not in chat_memory:
                    # 聊天未开启，不回复
                    return
                response_text = chat_memory[room_identifier].respond(content)
            
            if response_text:
                await room.ready()
                await room.say(response_text, mention_id)


chat_memory = {}
bot = DumplingBot()
asyncio.run(bot.start())


'''
{
 'id': 'chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve',
 'object': 'chat.completion',
 'created': 1677649420,
 'model': 'gpt-3.5-turbo',
 'usage': {'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
 'choices': [
   {
    'message': {
      'role': 'assistant',
      'content': 'The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers.'},
    'finish_reason': 'stop',
    'index': 0
   }
  ]
}
'''
