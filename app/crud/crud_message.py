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
        """获取或创建两人对话，返回对话ID (无RPC)"""
        client = db_conn["connection"]
        try:
            # 1. 获取 user1 的所有对话ID
            user1_convs_res = client.table('conversation_participants').select('conversation_id').eq('user_id', user1_id).execute()
            if user1_convs_res.data:
                user1_conv_ids = [c['conversation_id'] for c in user1_convs_res.data]
                
                # 2. 在 user1 的对话中查找也包含 user2 的对话
                if user1_conv_ids:
                    common_convs_res = client.table('conversation_participants').select('conversation_id').in_('conversation_id', user1_conv_ids).eq('user_id', user2_id).execute()
                    
                    if common_convs_res.data:
                        # 假设第一个就是我们想要的1对1对话
                        return common_convs_res.data[0]['conversation_id']

            # 3. 如果没有找到共同对话，则创建新的
            new_conv_res = client.table('conversations').insert({}).execute()
            if not new_conv_res.data:
                return None
                
            conv_id = new_conv_res.data[0]['id']
            
            # 4. 添加参与者
            client.table('conversation_participants').insert([
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
            
            result = client.table("messages").insert(insert_data).execute()
            
            if result.data:
                msg_data = result.data[0]
                client.table('conversations').update({
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
            
            result = client.table("messages").insert(insert_data).execute()
            
            if result.data:
                msg_data = result.data[0]
                client.table('conversations').update({
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
                result = connection.table("messages").select("*").or_(
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
            part_res = client.table('conversation_participants').select('user_id').eq('conversation_id', conversation_id).eq('user_id', user_id).execute()
            if not part_res.data:
                return []

            result = client.table("messages").select("*").eq(
                'conversation_id', conversation_id
            ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()

            if result.data:
                return [Message.model_validate(msg) for msg in result.data]
        except Exception as e:
            print(f"获取对话消息失败: {e}")
        return []

    async def get_conversations(self, db_conn: Dict[str, Any], user_id: int, limit: int = 20, offset: int = 0) -> List[ConversationListItem]:
        """获取用户的对话列表 (无RPC)"""
        client = db_conn["connection"]
        try:
            # 1. 获取用户参与的所有对话ID
            user_conv_res = client.table('conversation_participants').select('conversation_id').eq('user_id', user_id).order('conversation_id', desc=True).range(offset, offset + limit - 1).execute()
            if not user_conv_res.data:
                return []

            conv_ids = [c['conversation_id'] for c in user_conv_res.data]
            
            # 2. 获取这些对话的详细信息
            conv_details_res = client.table('conversations').select('id, last_message_id').in_('id', conv_ids).execute()
            if not conv_details_res.data:
                return []
            
            conv_details_map = {c['id']: c for c in conv_details_res.data}
            
            # 3. 获取所有相关的参与者
            participants_res = client.table('conversation_participants').select('conversation_id, user_id, profiles(id, username, avatar_url, role)').in_('conversation_id', conv_ids).execute()
            if not participants_res.data:
                return []

            conv_participants_map = {}
            for p in participants_res.data:
                conv_id = p['conversation_id']
                if conv_id not in conv_participants_map:
                    conv_participants_map[conv_id] = []
                conv_participants_map[conv_id].append(p)

            # 4. 获取所有相关的最后一条消息
            last_message_ids = [c['last_message_id'] for c in conv_details_res.data if c.get('last_message_id')]
            last_messages_map = {}
            if last_message_ids:
                messages_res = client.table('messages').select('id, content, created_at').in_('id', last_message_ids).execute()
                last_messages_map = {m['id']: m for m in messages_res.data}

            # 5. 获取所有对话的未读消息数
            unread_counts_map = {}
            for conv_id in conv_ids:
                 unread_res = client.table('messages').select('id', count='exact').eq('conversation_id', conv_id).eq('recipient_id', user_id).eq('is_read', False).execute()
                 unread_counts_map[conv_id] = unread_res.count or 0

            # 6. 组装最终结果
            conversations = []
            for conv_id in conv_ids:
                participants = conv_participants_map.get(conv_id, [])
                other_participant_data = next((p for p in participants if p['user_id'] != user_id), None)
                
                if not other_participant_data or not other_participant_data.get('profiles'):
                    continue

                other_user_profile = other_participant_data.get('profiles') or {}
                # 确保核心字段存在，否则跳过
                if not other_user_profile.get('id') or not other_user_profile.get('username'):
                    continue
                
                other_user = ConversationParticipant(
                    id=other_user_profile['id'],
                    username=other_user_profile['username'],
                    avatar_url=other_user_profile.get('avatar_url'),
                    role=other_user_profile.get('role', 'user') # 提供一个默认角色
                )
                
                last_message_id = conv_details_map.get(conv_id, {}).get('last_message_id')
                last_message_data = last_messages_map.get(last_message_id)
                last_time = None
                if last_message_data and last_message_data.get('created_at'):
                    last_time = datetime.fromisoformat(last_message_data['created_at'])

                conversations.append(ConversationListItem(
                    id=conv_id,
                    other_user=other_user,
                    last_message=last_message_data.get('content') if last_message_data else None,
                    last_message_time=last_time,
                    unread_count=unread_counts_map.get(conv_id, 0)
                ))
            
            return conversations
        except Exception as e:
            print(f"获取对话列表失败: {e}")
            return []
    
    async def mark_message_as_read(self, db_conn: Dict[str, Any], message_id: int, user_id: int) -> bool:
        """标记消息为已读"""
        client = db_conn["connection"]
        try:
            now = datetime.now().isoformat()
            result = client.table("messages").update({
                "is_read": True,
                "read_at": now,
                "updated_at": now
            }).eq("id", message_id).eq("recipient_id", user_id).execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"标记消息已读失败: {e}")
            return False

    async def update_message(self, db_conn: Dict[str, Any], message_id: int, user_id: int, new_content: str) -> Optional[Message]:
        """编辑消息"""
        client = db_conn["connection"]
        try:
            # First, verify the user is the sender
            message_res = client.table("messages").select("sender_id").eq("id", message_id).single().execute()
            if not message_res.data or message_res.data['sender_id'] != user_id:
                return None

            now = datetime.now().isoformat()
            update_data = {
                "content": new_content,
                "updated_at": now
            }
            
            result = client.table("messages").update(update_data).eq("id", message_id).execute()
            
            if result.data:
                return Message.model_validate(result.data[0])
        except Exception as e:
            print(f"编辑消息失败: {e}")
        return None

    async def delete_message(self, db_conn: Dict[str, Any], message_id: int, user_id: int) -> bool:
        """删除消息（软删除）"""
        client = db_conn["connection"]
        try:
            # Verify the user is the sender
            message_res = client.table("messages").select("sender_id").eq("id", message_id).single().execute()
            if not message_res.data or message_res.data['sender_id'] != user_id:
                return False

            now = datetime.now().isoformat()
            update_data = {
                "content": "此消息已删除",
                "updated_at": now
            }
            
            result = client.table("messages").update(update_data).eq("id", message_id).execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"删除消息失败: {e}")
            return False

    async def get_unread_message_count(self, db_conn: Dict[str, Any], user_id: int) -> int:
        """获取用户未读消息总数"""
        client = db_conn["connection"]
        try:
            result = client.table("messages").select("id", count='exact').eq("recipient_id", user_id).eq("is_read", False).execute()
            
            return result.count if result.count is not None else 0
        except Exception as e:
            print(f"获取未读消息数失败: {e}")
            return 0

message_crud = MessageCRUD()
