"""
消息系统的数据库操作
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from app.schemas.message_schema import (
    MessageCreate, MessageUpdate, Message, ConversationCreate,
    ConversationListItem, MessageType, MessageStatus, ConversationParticipant,
    MultiModalMessageCreate, MultiModalContent
)

class MessageCRUD:
    """消息CRUD操作类"""

    async def get_or_create_conversation(self, db_conn: Dict[str, Any], user1_id: int, user2_id: int) -> Optional[int]:
        """获取或创建两人对话，返回对话ID"""
        client = db_conn["connection"]
        try:
            res = await client.rpc('get_conversation_between_users', {'user1_id_in': user1_id, 'user2_id_in': user2_id}).execute()

            if res.data:
                return res.data[0]['id']
                
            new_conv_res = await client.table('conversations').insert({}).execute()
            if not new_conv_res.data:
                return None
                
            conv_id = new_conv_res.data[0]['id']
            await client.table('conversation_participants').insert([
                {'conversation_id': conv_id, 'user_id': user1_id},
                {'conversation_id': conv_id, 'user_id': user2_id}
            ]).execute()
            
            return conv_id
        except Exception as e:
            print(f"获取或创建对话失败: {e}")
            return None

    async def create_multi_modal_message(self, db_conn: Dict[str, Any], sender_id: int, message_data: MultiModalMessageCreate) -> Optional[Message]:
        """创建新的多模态消息"""
        client = db_conn["connection"]
        try:
            conversation_id = message_data.conversation_id
            if not conversation_id:
                conversation_id = await self.get_or_create_conversation(db_conn, sender_id, message_data.recipient_id)
            
            if not conversation_id:
                raise Exception("无法获取或创建对话")

            content_str = json.dumps([item.dict() for item in message_data.content])
            now = datetime.now().isoformat()
            insert_data = {
                "conversation_id": conversation_id,
                "sender_id": sender_id,
                "recipient_id": message_data.recipient_id,
                "content": content_str,
                "message_type": MessageType.multi_modal.value,
                "status": MessageStatus.sent.value,
                "created_at": now,
                "updated_at": now
            }
            
            result = await client.table("messages").insert(insert_data).execute()
            
            if result.data:
                msg_data = result.data[0]
                await client.table('conversations').update({
                    'last_message_id': msg_data['id'],
                    'updated_at': now
                }).eq('id', conversation_id).execute()
                return Message.model_validate(msg_data)
                    
        except Exception as e:
            print(f"创建多模态消息失败: {e}")
        return None

    async def create_message(self, db_conn: Dict[str, Any], sender_id: int, message_data: MessageCreate) -> Optional[Message]:
        """创建新消息"""
        client = db_conn["connection"]
        try:
            conversation_id = message_data.conversation_id
            if not conversation_id:
                conversation_id = await self.get_or_create_conversation(db_conn, sender_id, message_data.recipient_id)
            
            if not conversation_id:
                raise Exception("无法获取或创建对话")

            now = datetime.now().isoformat()
            insert_data = {
                "conversation_id": conversation_id,
                "sender_id": sender_id,
                "recipient_id": message_data.recipient_id,
                "content": message_data.content,
                "message_type": message_data.message_type.value,
                "status": MessageStatus.sent.value,
                "created_at": now,
                "updated_at": now
            }
            
            result = await client.table("messages").insert(insert_data).execute()
            
            if result.data:
                msg_data = result.data[0]
                await client.table('conversations').update({
                    'last_message_id': msg_data['id'],
                    'updated_at': now
                }).eq('id', conversation_id).execute()
                return Message.model_validate(msg_data)
                    
        except Exception as e:
            print(f"创建消息失败: {e}")
        return None
    
    async def get_messages(self, db_conn: Tuple[Any, str], user_id: int, 
                          limit: int = 20, offset: int = 0) -> List[Message]:
        """获取用户的消息列表"""
        connection, db_type = db_conn
        
        try:
            if db_type == "postgres":
                query = """
                    SELECT id, conversation_id, sender_id, recipient_id, content, 
                           message_type, status, is_read, created_at, updated_at, read_at
                    FROM messages 
                    WHERE sender_id = $1 OR recipient_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2 OFFSET $3
                """
                results = await connection.fetch(query, user_id, limit, offset)
                return [Message.model_validate(row) for row in results]
            else:
                result = await connection.table("messages").select("*").or_(
                    f"sender_id.eq.{user_id},recipient_id.eq.{user_id}"
                ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
                
                if result.data:
                    return [Message.model_validate(msg) for msg in result.data]
                    
        except Exception as e:
            print(f"获取消息列表失败: {e}")
        return []
    
    async def get_conversation_messages(self, db_conn: Dict[str, Any], conversation_id: int, user_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        """获取特定对话的消息列表"""
        client = db_conn["connection"]
        try:
            part_res = await client.table('conversation_participants').select('user_id').eq('conversation_id', conversation_id).eq('user_id', user_id).execute()
            if not part_res.data:
                return []

            result = await client.table("messages").select("*").eq(
                'conversation_id', conversation_id
            ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()

            if result.data:
                return [Message.model_validate(msg) for msg in result.data]
        except Exception as e:
            print(f"获取对话消息失败: {e}")
        return []

    async def get_conversations(self, db_conn: Dict[str, Any], user_id: int, limit: int = 20, offset: int = 0) -> List[ConversationListItem]:
        """获取用户的对话列表"""
        client = db_conn["connection"]
        try:
            res = await client.rpc('get_user_conversations', {'p_user_id': user_id, 'p_limit': limit, 'p_offset': offset}).execute()
            
            if not res.data:
                return []

            conversations = []
            for row in res.data:
                other_user_data = row.get('other_user_details', {})
                other_user = ConversationParticipant(
                    id=other_user_data.get('id'),
                    username=other_user_data.get('username', '未知用户'),
                    avatar_url=other_user_data.get('avatar_url'),
                    role=other_user_data.get('role')
                )
                conversations.append(ConversationListItem(
                    id=row['conversation_id'],
                    other_user=other_user,
                    last_message=row.get('last_message_content'),
                    last_message_time=datetime.fromisoformat(row['last_message_time']) if row.get('last_message_time') else None,
                    unread_count=row.get('unread_count', 0)
                ))
            return conversations
        except Exception as e:
            print(f"获取对话列表失败: {e}")
            return []
    
    async def mark_message_as_read(self, db_conn: Tuple[Any, str], message_id: int, user_id: int) -> bool:
        """标记消息为已读"""
        connection, db_type = db_conn
        
        try:
            if db_type == "postgres":
                query = """
                    UPDATE messages 
                    SET is_read = true, read_at = $1, updated_at = $1
                    WHERE id = $2 AND recipient_id = $3
                """
                now = datetime.now()
                result = await connection.execute(query, now, message_id, user_id)
                return result == "UPDATE 1"
            else:
                now = datetime.now().isoformat()
                result = await connection.table("messages").update({
                    "is_read": True,
                    "read_at": now,
                    "updated_at": now
                }).eq("id", message_id).eq("recipient_id", user_id).execute()
                
                return len(result.data) > 0
                
        except Exception as e:
            print(f"标记消息已读失败: {e}")
        return False

message_crud = MessageCRUD()
