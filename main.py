#!/usr/bin/env python3
# -*- coding: utf8 -*-

from fastapi import FastAPI, Query, Path, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from datetime import datetime


app = FastAPI()

async def common_parameters(skip:int=Query(0, gte=0), limiter: int=Query(10, lte=50)):
    return {"skip":skip, "limiter":limiter}

@app.middleware("http")
async def handler_middleware_method(request, call_next):
    print(f"start time:{datetime.utcnow()}")
    response = await call_next(request) 
    print(f"end time:{datetime.utcnow()}")
    return response

@app.get("/")
async def hello_method():
    return {"msg":"hello python fastapi framework", "code":200,"title":"我是fastapi框架"}

@app.get("/name/{id}")
async def name_method(id:int=Path(...,description="路径参数Id")):
    return {"name":"name value", "id":id}

@app.get("/html", response_class=HTMLResponse)
async def get_html_method():
    return '<h1>response h1 tags</h1>'


@app.get('/file')
async def get_file_method():
    return FileResponse('./log/a.log')


class News(BaseModel):
    id: int
    title: str
    content: str

@app.get("/news/{id}", response_model=News)
async def get_news_method(id: int):
    return {
        "id":id,
        "title": f"这里还有{id}本书",
        "content": "这是content的值"
    }


@app.get("/news/exception/{id}")
async def get_news_exception_method(id: int):
    id_list = [item for item in range(1,20)]
    if id not in id_list:
        raise HTTPException(status_code=404, detail="查找的信息不存在")
    return {"id": id}

@app.get("/news_list")
async def get_news_list_method(common=Depends(common_parameters)):
    return common
