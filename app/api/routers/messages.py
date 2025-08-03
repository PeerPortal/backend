from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.schemas.message_schema import MessageCreate, Message, ConversationListItem, MessageListResponse, ConversationListResponse
from app.crud.crud_message import message_crud
from app.schemas.user_schema import User

router = APIRouter()

@router.post("/", response_model=Message, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_in: MessageCreate,
    db: dict = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    发送一条新消息。

    如果未提供 `conversation_id`，系统将根据发送者和接收者自动查找或创建新的对话。
    """
    if current_user.id == message_in.recipient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能给自己发送消息。"
        )
    
    message = await message_crud.create_message(db, sender_id=current_user.id, message_data=message_in)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送消息失败。"
        )
    return message

@router.get("/conversations", response_model=ConversationListResponse)
async def get_user_conversations(
    db: dict = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """
    获取当前用户的对话列表。
    """
    conversations = await message_crud.get_conversations(db, user_id=current_user.id, limit=limit, offset=offset)
    total = len(conversations) # This is a simplification. A proper count would require another query.
    return {"conversations": conversations, "total": total}

@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def get_conversation_messages(
    conversation_id: int,
    db: dict = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """
    获取指定对话的消息列表。
    """
    messages = await message_crud.get_conversation_messages(
        db, conversation_id=conversation_id, user_id=current_user.id, limit=limit, offset=offset
    )
    total = len(messages) # Simplification
    return {"messages": messages, "total": total, "has_next": len(messages) == limit}