from aiogram.filters import Command, CommandStart
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

import google.generativeai as genai

import bot.keyboards as kb
import bot.states as states
import bot.database.requests as rq 
from LLM.llm import LLMChat

from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           Message, CallbackQuery)



router = Router()



''' Start Command '''

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    try:
        user = await rq.set_user(message.from_user.id)
        if not user:
            await message.answer("Error creating user profile")
            return

        name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
        greeting = (
            f"My sincerest greetings, {name}. "
            "I am Sunday. It is an honour for me to help you delve into "
            "yet another Trailblaze within Honkai: Star Rail universe."
        )
        await message.answer(greeting)

        api_key = await rq.get_api(message.from_user.id)
        if not api_key:
            await message.answer("Please, send me your Google Gemini API-key to proceed.")
            await state.set_state(states.RegAPI.api_key)
        else:
            await message.answer(
                "You are free to set your story. Please, consider creating a "
                "new character and persona for a better experience.",
                reply_markup=kb.main_keyboard
            )

    except Exception as e:
        print(f"Error in cmd_start: {e}")
        await message.answer("An error occurred. Please try again later.")
    
    


''' API-key check'''

async def test_gemini_api(api_key: str) -> bool:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        await model.generate_content_async('Test', request_options={'timeout': 5})
        return True
    
    except Exception as e:
        print(f'API validation failed: {e}')
        return False
    

@router.message(states.RegAPI.api_key)
async def process_api_key(message: Message, state: FSMContext):
    api_key = message.text.strip()
    
    is_valid = await test_gemini_api(api_key)
    
    if not is_valid:
        await message.answer('Ah, it seems like the key you have sent is not corrent. Please, try again.')
        return
    
    try:
        await rq.set_api(message.from_user.id, api_key)
        await state.clear()
        await message.answer('New API-key has been saved.')
        await message.answer(
                "You are free to set your story. Please, consider creating a "
                "new character and persona for a better experience.",
                reply_markup=kb.main_keyboard
            )

    except Exception as e:
        await message.answer('Ah, it seems something is wrong. My apologies. Please, try again later.')
        print(f'Error saving API key: {e}')

    


''' Main Keyboard New Chat responses '''

@router.message(F.text=='New Chat')
async def new_chat(message: Message):
    await message.reply('Would you like to change persona or character?',
                        reply_markup=kb.change_options_inline)


@router.callback_query(F.data=='Yes')
async def change_char_persona(callback: CallbackQuery):
    await callback.answer('Change')
    await callback.message.edit_text('Select an option:',
                        reply_markup=kb.options_inline)
    

@router.callback_query(F.data=='No')
async def not_change_char_persona(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Leave it be')
    
    data = await state.get_data()
    active_persona = data.get('active_persona')
    active_character = data.get('active_character')

    if active_persona and active_character:
        active_persona = data.get('active_persona')
        active_character = data.get('active_character')
        API_KEY = await rq.get_api(callback.from_user.id)
        
        new_chat = LLMChat(
            api_key=API_KEY,
            active_character=active_character,
            active_persona=active_persona
        )
        await state.update_data(llm_chat=new_chat)
        
        await callback.message.edit_text('You may now start a fresh chat.')
    
    elif active_persona:
        await callback.message.edit_text("Please, select a character first.")
        return

    elif active_character:
        await callback.message.edit_text("Please, select a persona first.")
        return
    
    else:
        await callback.message.edit_text("Please, select a persona and a character first.")
        return
    




''' Main Keyboard Story Options responses '''

@router.message(F.text=='Options')
async def story_options(message: Message):
    await message.answer('Select an option:', 
                        reply_markup=kb.options_inline)


@router.callback_query(F.data=='Characters')
async def character(callback: CallbackQuery):
    await callback.message.edit_text('Select an option:',
                                     reply_markup=kb.characters_options_inline)


@router.callback_query(F.data=='Personas')
async def persona(callback: CallbackQuery):
    await callback.message.edit_text('Select an option:',
                                     reply_markup=kb.personas_options_inline)


@router.callback_query(F.data=='Change_API')
async def change_api(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Please, send me your Google Gemini API-key to proceed.')
    await state.set_state(states.RegAPI.api_key)
    return




''' Characters Options responses'''

'''New Character'''

@router.callback_query(F.data=='Create_Character')
async def new_char(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Create Character')
    await callback.message.answer('Please, set a name for a character.')
    await state.set_state(states.Character.character_name)


@router.message(states.Character.character_name)
async def process_character_name(message: Message, state: FSMContext):
    await state.update_data(character_name=message.text.strip())
    await message.answer('''Now, please, describe your character as if you speak with them. 
                         For example: "You are 27 years old, you have got blue eyes and brown hair, you are kind and sweet." 
                         You may also add some background and biography.''')
    await state.set_state(states.Character.character_prompt)


@router.message(states.Character.character_prompt)
async def process_character_prompt(message: Message, state: FSMContext):
    data = await state.get_data()
    character_name = data['character_name']
    character_prompt = message.text.strip()

    try:
        await rq.set_character(message.from_user.id, character_name, character_prompt)
        await state.clear()
        await message.answer('New character has been saved.')

    except Exception as e:
        await message.answer('Ah, it seems something is wrong. My apologies. Please, try again later.')
        print(f'Error saving character: {e}')



''' Select Character'''


@router.callback_query(F.data == 'Change_Character')
async def select_character(callback: CallbackQuery):
    await callback.answer('Change Character')
    try:
    
        characters = await rq.get_characters_list(callback.from_user.id)

        if characters is None or not characters:
            await callback.message.edit_text('It seems you have not created any characters yet. Please, proceed with creating one.')
            return
        
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=char['name'],  
                callback_data=f"select_char_{char['id']}"  
            )] for char in characters
        ])
        
        await callback.message.edit_text(
            'Select a character:',
            reply_markup=keyboard
        )

    except Exception as e:
        await callback.answer('It seems something is wrong. Please, try again later.')


@router.callback_query(F.data.startswith('select_char_'))
async def process_selected_character(callback: CallbackQuery, state: FSMContext):
    character_id = int(callback.data.split('_')[-1])
    
    try:
        characters = await rq.get_characters_list(callback.from_user.id)

        if not characters:
            await callback.answer('It seems something is wrong. Please, try again later.')
            return
            
        selected_character = next((char for char in characters if char['id'] == character_id), None)

            
        if selected_character:
            await callback.message.answer(
                f"Selected character: {selected_character['name']}\n"
                f"Description: {selected_character['prompt'][:100]}...")

            await state.update_data(active_character=selected_character)
            await callback.answer(f"Character '{selected_character['name']}' is now active!")
        else:
            await callback.answer('Character not found!')
        
    except Exception as e:
        await callback.answer('It seems something is wrong. Please, try again later.')



''' Delete Character'''


@router.callback_query(F.data == 'Delete_Character')
async def delete_character_start(callback: CallbackQuery):
    await callback.answer('Delete Character')
    try:
        characters = await rq.get_characters_list(callback.from_user.id)

        if not characters or characters is None:
            await callback.message.edit_text('You have no characters to delete.')
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"❌ {char['name']}",
                callback_data=f"delete_char_{char['id']}"
            )] for char in characters
        ])
        
        await callback.message.edit_text(
            'Select character to delete:',
            reply_markup=keyboard
        )

    except Exception as e:
        await callback.answer('It seems something is wrong. Please, try again later.', show_alert=True)


@router.callback_query(F.data.startswith('delete_char_'))
async def process_delete_character(callback: CallbackQuery):
    character_id = int(callback.data.split('_')[-1])
    
    try:
        success = await rq.delete_character(callback.from_user.id, character_id)
        
        if success:
            await callback.answer('Character deleted successfully!', show_alert=True)
            await delete_character_start(callback)
        else:
            await callback.answer('Character not found or deletion failed.', show_alert=True)
            
    except Exception as e:
        await callback.answer('Error deleting character', show_alert=True)
    





''' Personas Options responses'''

'''New Persona'''

@router.callback_query(F.data=='Create_Persona')
async def new_persona(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Create Persona')
    await callback.message.answer('Please, set a name for a persona.')
    await state.set_state(states.Persona.persona_name)


@router.message(states.Persona.persona_name)
async def process_api_key(message: Message, state: FSMContext):
    await state.update_data(persona_name=message.text.strip())
    await message.answer(f'Now, please, describe your persona as if you talk about yourself.')
    await state.set_state(states.Persona.persona_prompt)


@router.message(states.Persona.persona_prompt)
async def process_persona_prompt(message: Message, state: FSMContext):
    data = await state.get_data()
    persona_name = data['persona_name']
    persona_prompt = message.text.strip()

    try:
        await rq.set_persona(message.from_user.id, persona_name, persona_prompt)
        await state.clear()
        await message.answer('New persona has been saved.')

    except Exception as e:
        await message.answer('Ah, it seems something is wrong. My apologies. Please, try again later.')
        print(f'Error saving persona: {e}')



''' Select Persona'''


@router.callback_query(F.data == 'Change_Persona')
async def select_persona(callback: CallbackQuery):
    await callback.answer('Change Persona')
    try:
    
        personas = await rq.get_personas_list(callback.from_user.id)

        if personas is None or not personas:
            await callback.message.edit_text('It seems you have not created any personas yet. Please, proceed with creating one.')
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=persona['name'],  
                callback_data=f"select_persona_{persona['id']}"  
            )] for persona in personas
        ])
        
        await callback.message.edit_text(
            'Select a persona:',
            reply_markup=keyboard
        )

    except Exception as e:
        await callback.answer('It seems something is wrong. Please, try again later.')


@router.callback_query(F.data.startswith('select_persona_'))
async def process_selected_persona(callback: CallbackQuery, state: FSMContext):
    persona_id = int(callback.data.split('_')[-1])
    
    try:
        personas = await rq.get_personas_list(callback.from_user.id)

        if not personas:
            await callback.answer('It seems something is wrong. Please, try again later.')
            return
            
        selected_persona = next((persona for persona in personas if persona['id'] == persona_id), None)
        
        if selected_persona:
            await callback.message.answer(
                f"Selected persona: {selected_persona['name']}\n"
                f"Description: {selected_persona['prompt'][:100]}...")

            await state.update_data(active_persona=selected_persona)
            await callback.answer(f"Persona '{selected_persona['name']}' is now active!")
        else:
            await callback.answer('Persona not found!')
        
    except Exception as e:
        await callback.answer('It seems something is wrong. Please, try again later.')



''' Delete Persona'''


@router.callback_query(F.data == 'Delete_Persona')
async def delete_persona_start(callback: CallbackQuery):
    await callback.answer('Delete Persona')
    try:
        personas = await rq.get_personas_list(callback.from_user.id)

        if not personas or personas is None:
            await callback.message.edit_text('You have no personas to delete.')
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f"❌ {persona['name']}",
                callback_data=f"delete_persona_{persona['id']}"
            )] for persona in personas
        ])
        
        await callback.message.edit_text(
            'Select persona to delete:',
            reply_markup=keyboard
        )

    except Exception as e:
        await callback.answer('It seems something is wrong. Please, try again later.', show_alert=True)


@router.callback_query(F.data.startswith('delete_persona_'))
async def process_delete_persona(callback: CallbackQuery):
    persona_id = int(callback.data.split('_')[-1])
    
    try:
        success = await rq.delete_persona(callback.from_user.id, persona_id)
        
        if success:
            await callback.answer('Persona deleted successfully!', show_alert=True)
            await delete_persona_start(callback)
        else:
            await callback.answer('Persona not found or deletion failed.', show_alert=True)
            
    except Exception as e:
        await callback.answer('Error deleting persona', show_alert=True)



''' Active Character/Persona check '''

@router.message(Command('status'))
async def check_status(message: Message, state: FSMContext):
    data = await state.get_data()
    active_persona = data.get('active_persona')
    active_character = data.get('active_character')
    
    status_msg = []
    
    if active_persona:
        status_msg.append(f"Active persona: {active_persona['name']}")
    if active_character:
        status_msg.append(f"Active character: {active_character['name']}")
    
    if not status_msg:
        status_msg.append("No active persona or character selected.")
    
    await message.answer("\n".join(status_msg))



''' Message Responses'''

@router.message()
async def handle_message(message: Message, state: FSMContext):

    data = await state.get_data()
    active_persona = data.get('active_persona')
    active_character = data.get('active_character')

    if active_persona and active_character:

        chat: LLMChat = data.get('llm_chat')
        if not chat:
            active_persona = data.get('active_persona')
            active_character = data.get('active_character')
            API_KEY = await rq.get_api(message.from_user.id)
        
            chat = LLMChat(
                api_key=API_KEY,
                active_character=active_character,
                active_persona=active_persona
            )
            await state.update_data(llm_chat=chat)
    
        response = await chat.get_response(message.text)
        await message.answer(response)
          
    elif active_persona:
        await message.answer("Please, select a character first.")
        return

    elif active_character:
        await message.answer("Please, select a persona first.")
        return
    
    else:
        await message.answer("Please, select a persona and a character first.")
        return
    
