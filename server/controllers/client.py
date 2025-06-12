from fastapi import APIRouter, Request
from models import Account, App, History
from uuid import uuid4
from service.common import get_dict
import requests
from datetime import datetime
from httpx import AsyncClient
import os

router = APIRouter(prefix="/client")


@router.post("/login")
async def login(request: Request):
    data = await request.json()
    account = await Account.get_or_none(
        account=data.get("account"), password=data.get("password")
    )
    if not account:
        return {"success": False, "message": "账号或密码错误"}
    token = uuid4()
    account.token = str(token)
    await account.save(update_fields=["token"])
    return {"success": True, "message": "登录成功", "data": account}


@router.post("/check")
async def logout(request: Request):
    token = request.headers.get("token")
    if not token:
        return {"success": False, "message": "尚未登录"}
    account = await Account.get_or_none(token=token)
    if account:
        return {"success": True, "message": "已登录"}
    else:
        return {"success": False, "message": "尚未登录"}


@router.post("/chat")
async def chat(request: Request):
    api_base = await get_dict("api_base")
    if not api_base:
        return {"success": False, "message": "请先在后台配置api地址"}

    data = await request.json()
    conversation_id = data.get("conversation_id", "")
    app_id = data.get("app_id")
    app = await App.get_or_none(id=app_id)

    if not app:
        return {"success": False, "message": "应用不存在"}

    token = app.token
    account_id = data.get("account_id")
    question = data.get("question")
    history = {
        "account_id": account_id,
        "app_id": app_id,
        "question": question,
        "question_time": datetime.now(),
    }
    url = f"{api_base}/chat-messages"
    data = {
        "conversation_id": conversation_id,
        "user": account_id,
        "inputs": {},
        "query": question,
        "response_mode": "blocking",
    }
    headers = {
        "Authorization": f"Bearer {token}",
    }
    async with AsyncClient(timeout=None) as client:
        res = await client.post(url, json=data, headers=headers)
        res = res.json()
    conversation_id = res.get("conversation_id", None)
    text = res.get("answer", None)
    if not text:
        return {
            "success": False,
            "message": "聊天失败，未获取到回答",
            "data": "服务器异常",
        }
    history["answer"] = text
    history["answer_time"] = datetime.now()
    await History.create(**history)
    return {
        "success": True,
        "message": "聊天成功",
        "data": {"conversation_id": conversation_id, "text": text},
    }


@router.post("/conversations")
async def conversations(request: Request):
    api_base = await get_dict("api_base")
    if not api_base:
        return {"success": False, "message": "请先在后台配置api地址"}

    data = await request.json()

    app_id = data.get("app_id")
    account_id = data.get("account_id")

    app = await App.get_or_none(id=app_id)

    if not app:
        return {"success": False, "message": "应用不存在"}

    token = app.token
    headers = {
        "Authorization": f"Bearer {token}",
    }

    url = f"{api_base}/conversations?user={account_id}&limit=10"
    async with AsyncClient(timeout=None) as client:
        res = await client.get(url, headers=headers)
        res = res.json()

    data = []
    conversations = res.get("data", [])
    for item in conversations:
        conversation_id = item.get("id")
        url = f"{api_base}/messages?user={account_id}&conversation_id={conversation_id}&limit=100"
        async with AsyncClient(timeout=None) as client:
            res = await client.get(url, headers=headers)
            res = res.json()
            query = res.get("data")[0].get("query")
            data.append({"id": conversation_id, "query": query})

    return {
        "success": True,
        "message": "获取成功",
        "data": data,
    }


@router.post("/messages")
async def messages(request: Request):
    api_base = await get_dict("api_base")
    if not api_base:
        return {"success": False, "message": "请先在后台配置api地址"}

    data = await request.json()

    app_id = data.get("app_id")
    account_id = data.get("account_id")
    conversation_id = data.get("conversation_id")

    app = await App.get_or_none(id=app_id)

    if not app:
        return {"success": False, "message": "应用不存在"}

    token = app.token

    headers = {
        "Authorization": f"Bearer {token}",
    }
    url = f"{api_base}/messages?user={account_id}&conversation_id={conversation_id}&limit=100"
    async with AsyncClient(timeout=None) as client:
        res = await client.get(url, headers=headers)
        res = res.json()
    return {
        "success": True,
        "message": "获取成功",
        "data": res.get("data"),
    }
