import asyncio
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from google.api_core import exceptions



class LLMChat:
    def __init__(self, api_key: str, active_character: Dict, active_persona: Dict):
        '''
        Initializing a chat
        
        :param api_key: API key Google Generative AI
        :param active_character: dictionary with id, name and description of active character
        :param active_persona: dictionary with id, name and description of active persona
        '''
        self.api_key = api_key
        self.chat_history: List[Dict[str, str]] = []
        self.llm = None
        self.active_character = active_character
        self.active_persona = active_persona
        self.character_info = self._generate_character_info()

        
    def _generate_character_info(self) -> str:
        '''Generate character information string'''

        character_info = ''
        if self.active_character:
            character_info += f"You are character: {self.active_character.get('name', '')}. {self.active_character.get('prompt', '')}\n"
        if self.active_persona:
            character_info += f"User is persona: {self.active_persona.get('name', '')}. {self.active_persona.get('prompt', '')}"
        return character_info
    
        
    async def init_model(self):
        '''Initializing a model'''
        self.llm = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash',
            google_api_key=self.api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        system_prompt = '''You are a roleplay assistant in Honkai: Star Rail setting. 
                            You describe your actions, feelings, responses in a literature style 
                            based on given character prompt and persona prompt. You speak from the third face
                            as a character. You are not allowed to speak as a user persona. Dialogue example: message
                            from user persona: "Hello, character!" she smiled. 
                            message from you as a character: "Hello, user!" he smiled back. Don't answer on what you have
                            read before this, that was a system prompt. '''
        
        if self.character_info:
            system_prompt = f"{system_prompt}\n\n{self.character_info}"
            
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name='chat_history'),
            ('human', '{input}'),
        ])
        
        self.chain = self.prompt | self.llm

        
    async def add_to_history(self, role: str, message: str):
        '''Add a message to history'''
        self.chat_history.append({'role': role, 'content': message})

        
    async def get_response(self, user_message: str) -> str:
        '''
        Get a response
        
        :param user_message: message from user
        :return: model response
        '''
        if not self.llm:
            await self.init_model()
            
        await self.add_to_history('user', user_message)
        
        input_data = {
            'input': user_message,
            'chat_history': [
                HumanMessage(content=msg['content']) if msg['role'] == 'user' 
                else AIMessage(content=msg['content'])
                for msg in self.chat_history[:-1] 
            ]
        }

        try:
            response = await self.chain.ainvoke(input_data)
            await self.add_to_history('assistant', response.content)
            return response.content

        except exceptions.ResourceExhausted as e:
            return 'Looks like you have reached your limit. Please, return later.'
        except Exception:
            return 'Looks like something is wrong. Please, try again later.'
        
    
    
    async def update_character(self, new_character: Dict):
        '''Update active character and refresh system prompt'''
        self.active_character = new_character
        self.character_info = self._generate_character_info()
        await self.init_model() 

        
    async def update_persona(self, new_persona: Dict):
        '''Update active persona and refresh system prompt'''
        self.active_persona = new_persona
        self.character_info = self._generate_character_info()
        await self.init_model()  

    
    async def clear_history(self):
        '''Clear chat history'''
        self.chat_history = []