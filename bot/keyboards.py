from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)




main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='New Chat')],
    [KeyboardButton(text='Options')]
],
                    resize_keyboard=True,
                    input_field_placeholder='Choose an option')



options_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Characters', callback_data='Characters'), 
     InlineKeyboardButton(text='Personas', callback_data='Personas')],
    [InlineKeyboardButton(text='Change API', callback_data='Change_API')]
])


change_options_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Yes', callback_data='Yes'), 
     InlineKeyboardButton(text='No', callback_data='No')],
])


characters_options_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Select a character', callback_data='Change_Character'), 
     InlineKeyboardButton(text='Create a character', callback_data='Create_Character')],
    [InlineKeyboardButton(text='Delete a character', callback_data='Delete_Character')]
])


personas_options_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Select a persona', callback_data='Change_Persona'), 
     InlineKeyboardButton(text='Create a persona', callback_data='Create_Persona')],
    [InlineKeyboardButton(text='Delete a persona', callback_data='Delete_Persona')]
])