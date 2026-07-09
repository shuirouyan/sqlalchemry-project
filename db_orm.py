#!/usr/bin/env python3
# -*- coding: utf8 -*-

from fastapi import FastAPI, Depends
from sqlalchemy import DateTime, func, String, Float, select, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


async_database_url = "mysql+aiomysql://root:Aa##123456@127.0.0.1:3307/fastapidb?charset=utf8"
async_engine=create_async_engine(
        async_database_url,
        echo=True,
        pool_size=10,
        max_overflow=20
        )

class Base(DeclarativeBase):
    create_time: Mapped['datetime'] = mapped_column(DateTime, insert_default=func.now(), default=func.now, comment='创建时间')
    update_time: Mapped['datetime'] = mapped_column(DateTime, insert_default=func.now(), default=func.now, onupdate=func.now(), comment='修改时间')

class Book(Base):
    __tablename__='book'
    id: Mapped[int] = mapped_column(primary_key=True, comment="Id主键，书籍Id")
    bookname: Mapped[str] = mapped_column(String(255), comment="书籍名称")
    author: Mapped[str] = mapped_column(String(255), comment="书籍作者")
    price: Mapped[float] = mapped_column(Float, comment="书籍作者")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")

class BookReq(BaseModel):
    id: int
    bookname: str
    author: str
    publisher: str

async def create_schema():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def create_shema_event():
    await create_schema()


async_session_local = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

async def get_db():
    async with async_session_local() as session:
        try:
            yield session
            await session.commit()
        except Excetpion:
            await session.rollback()
            raise
        finally:
            await session.close()


@app.get("/")
async def hello():
    return {"msg":"hello fastapi","now":datetime.now()}


@app.get("/book/list")
async def get_book_list_method(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Book))
    return result.scalars().all()

@app.post("/book/update")
async def update_book_method(book: BookReq, db: AsyncSession=Depends(get_db)):
    result = await db.execute(update(Book).where(Book.id==book.id).values(bookname=book.bookname,publisher=book.publisher,author=book.author))
    return {"time":datetime.now(), "result":result.rowcount}
