from bot.database.models import async_session
from bot.database.models import User, Character, Persona
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List



async def set_user(tg_id: int) -> User | None:
    async with async_session() as session:
        try:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            
            if not user:
                user = User(tg_id=tg_id)
                session.add(user)
                await session.commit()
                await session.refresh(user)
            
            return user
        except Exception as e:
            print(f"Error in set_user: {e}")
            await session.rollback()
            return None
    


''' API requests'''

async def set_api(tg_id: int, api_key: str) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if not user:
            user = User(tg_id=tg_id, api_key=api_key)
            session.add(user)
        else:
            user.api_key = api_key
        
        await session.commit()
        await session.refresh(user)
        return user
    


async def get_api(tg_id: int) -> str | None:
    async with async_session() as session:
        try:
            user = await session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            return user.api_key if user else None
        except Exception as e:
            print(f"Error getting API key: {e}")
            return None
    

''' Character requests '''


async def set_character(tg_id: int,  character_name: str, character_prompt: str) -> Character:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            raise SQLAlchemyError
            
        character = Character(
            name=character_name,
            prompt=character_prompt,
            owner_id=user.id)
        
        session.add(character)
        await session.commit()
            
        return Character
    
    

async def get_characters_list(tg_id: int) -> Optional[List[dict]]:
    async with async_session() as session:
        try:

            result = await session.execute(
                select(User)
                .where(User.tg_id == tg_id)
                .options(selectinload(User.characters))
            )
            user = result.scalar_one()
                
            if not user.characters:
                return None
                    
            return [
                    {
                    'id': char.id,
                    'name': char.name,
                    'prompt': char.prompt,
                    }
                    for char in user.characters]
        
        except Exception as e:
            print(f'Error fetching characters: {e}')
            return None
        

async def delete_character(tg_id: int, character_id: int) -> bool:
    async with async_session() as session:
        try:
            result = await session.execute(
                select(User)
                .where(User.tg_id == tg_id)
                .options(selectinload(User.characters))
            )
            user = result.scalar_one()
            
            character_to_delete = next(
                (char for char in user.characters if char.id == character_id), 
                None
            )
            
            if not character_to_delete:
                return False
                
            await session.delete(character_to_delete)
            await session.commit()
            return True
            
        except Exception as e:
            print(f"Error deleting character: {e}")
            await session.rollback()
            return False
   
            


''' Persona requests '''
    


async def set_persona(tg_id: int,  persona_name: str, persona_prompt: str) -> Persona:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            raise SQLAlchemyError
            
        persona = Persona(
            name=persona_name,
            prompt=persona_prompt,
            owner_id=user.id)
        
        session.add(persona)
        await session.commit()
            
        return Persona
    
    

async def get_personas_list(tg_id: int) -> Optional[List[dict]]:
    async with async_session() as session:
        try:

            result = await session.execute(
                select(User)
                .where(User.tg_id == tg_id)
                .options(selectinload(User.personas))
            )
            user = result.scalar_one()
                
            if not user.personas:
                return None
                    
            return [
                    {
                    'id': char.id,
                    'name': char.name,
                    'prompt': char.prompt,
                    }
                    for char in user.personas]
        
        except Exception as e:
            print(f'Error fetching personas: {e}')
            return None
        

async def delete_persona(tg_id: int, persona_id: int) -> bool:
    async with async_session() as session:
        try:
            result = await session.execute(
                select(User)
                .where(User.tg_id == tg_id)
                .options(selectinload(User.personas))
            )
            user = result.scalar_one()
            
            persona_to_delete = next(
                (char for char in user.personas if char.id == persona_id), 
                None
            )
            
            if not persona_to_delete:
                return False
                
            await session.delete(persona_to_delete)
            await session.commit()
            return True
            
        except Exception as e:
            print(f"Error deleting persona: {e}")
            await session.rollback()
            return False
   