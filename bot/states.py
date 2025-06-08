
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup



class RegAPI(StatesGroup):
    api_key = State()


class Character(StatesGroup):
    character_name = State()
    character_prompt = State()


class Persona(StatesGroup):
    persona_name = State()
    persona_prompt = State()
    


class PersonaState(StatesGroup):
    active_persona = State()

class CharacterState(StatesGroup):
    active_character = State()



class ChatState(StatesGroup):
    llm_chat = State()





