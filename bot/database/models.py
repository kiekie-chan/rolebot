import os
from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///db.sqlite3')

engine = create_async_engine(url=DATABASE_URL)

async_session = async_sessionmaker(engine)



class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, unique=True)
    api_key: Mapped[str | None] = mapped_column(String(100), nullable=True) 

    characters: Mapped[list["Character"]] = relationship(back_populates="owner")
    
    personas: Mapped[list["Persona"]] = relationship(back_populates="owner")



class Character(Base):

    __tablename__ = 'characters'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))  
    prompt: Mapped[str] = mapped_column(Text)  
    
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="characters")



class Persona(Base):

    __tablename__ = 'personas'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100)) 
    prompt: Mapped[str] = mapped_column(Text)
    
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="personas")



async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)