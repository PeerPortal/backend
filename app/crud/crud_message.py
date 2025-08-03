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
            # Supabase 不直接支持数组包含操作，需要变通
            # 查找包含这两个用户的对话
            res = await client.rpc('get_conversation_between_users', {'user1_id': user1_id, 'user2_id': user2_id}).execute()

            if res.data:
                return res.data[0]['id']
                
            # 如果没有，则创建新的对话
            new_conv_res = await client.table('conversations').insert({}).execute()
            if not new_conv_res.data:
                return None
                
            # 添加对话参与者
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

            # 将多模态内容序列化为JSON字符串
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
                # 更新对话的 last_message_id 和 updated_at
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
                
                return [
                    Message(
                        id=row['id'],
                        conversation_id=row['conversation_id'],
                        sender_id=row['sender_id'],
                        recipient_id=row['recipient_id'],
                        content=row['content'],
                        message_type=MessageType(row['message_type']),
                        status=MessageStatus(row['status']),
                        is_read=row['is_read'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        read_at=row['read_at']
                    )
                    for row in results
                ]
                
            else:
                # Supabase 实现
                result = await connection.table("messages").select("*").or_(
                    f"sender_id.eq.{user_id},recipient_id.eq.{user_id}"
                ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
                
                if result.data:
                    return [
                        Message(
                            id=msg['id'],
                            conversation_id=msg['conversation_id'],
                            sender_id=msg['sender_id'],
                            recipient_id=msg['recipient_id'],
                            content=msg['content'],
                            message_type=MessageType(msg['message_type']),
                            status=MessageStatus(msg['status']),
                            is_read=msg.get('is_read', False),
                            created_at=datetime.fromisoformat(msg['created_at']),
                            updated_at=datetime.fromisoformat(msg['updated_at']),
                            read_at=datetime.fromisoformat(msg['read_at']) if msg.get('read_at') else None
                        )
                        for msg in result.data
                    ]
                    
        except Exception as e:
            print(f"获取消息列表失败: {e}")
            
        return []
    
    async def get_conversation_messages(self, db_conn: Dict[str, Any], conversation_id: int, user_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        """获取特定对话的消息列表"""
        client = db_conn["connection"]
        try:
            # 验证用户是否是该对话的参与者
            part_res = await client.table('conversation_participants').select('user_id').eq('conversation_id', conversation_id).eq('user_id', user_id).execute()
            if not part_res.data:
                return [] # 或者抛出权限错误

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
            # 使用RPC函数来获取对话列表，这样更高效
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
                
        except Exception as e:
            print(f"获取对话列表失败: {e}")
            
        return []
    
    # 以下是之前的实现，现在已经被上面的代码替代
    # async def get_conversations_old(self, db_conn: Dict[str, Any], user_id: int, limit: int = 20, offset: int = 0):
    #     # 如果使用asyncpg连接池
    #     if db_conn["type"] == "asyncpg":
    #         connection = db_conn["connection"]
    #         query = """
    #             SELECT 
    #                 cu.conversation_id,
    #                 cu.other_user_id,
    #                 u.username,
    #                 u.avatar_url,
    #                 u.role,
    #                 m.content as last_message,
    #                 m.created_at as last_message_time,
    #                 COALESCE(unread.count, 0) as unread_count
    #             FROM (
    #                 SELECT 
    #                     cp.conversation_id,
    #                     CASE 
    #                         WHEN cp.user_id = $1 THEN cp2.user_id
    #                         ELSE cp.user_id
    #                     END as other_user_id,
    #                     c.last_message_id,
    #                     c.updated_at as last_message_time
    #                 FROM conversation_participants cp
    #                 JOIN conversations c ON cp.conversation_id = c.id
    #                 JOIN conversation_participants cp2 ON cp2.conversation_id = cp.conversation_id AND cp2.user_id != cp.user_id
    #                 WHERE cp.user_id = $1
    #             ) cu
    #             JOIN users u ON u.id = cu.other_user_id
    #             LEFT JOIN messages m ON m.id = cu.last_message_id
    #             LEFT JOIN (
    #                 SELECT 
    #                     sender_id,
    #                     COUNT(*) as count
    #                 FROM messages 
    #                 WHERE recipient_id = $1 AND is_read = false
    #                 GROUP BY sender_id
    #             ) unread ON unread.sender_id = cu.other_user_id
    #             ORDER BY cu.last_message_time DESC
    #             LIMIT $2
    #         """
    #         results = await connection.fetch(query, user_id, limit)
                
#                 conversations = []
#                 for row in results:
#                     # 根据角色判断是导师还是学生
#                     if row['role'] == 'mentor':
#                         conversations.append(ConversationListItem(
#                             id=row['conversation_id'],
#                             other_user=ConversationParticipant(
#                                 id=row['other_user_id'],
#                                 username=row['username'],
#                                 avatar_url=row['avatar_url'],
#                                 role=row['role']
#                             ),
#                             last_message=row['last_message'],
#                             last_message_time=row['last_message_time'],
#                             unread_count=row['unread_count']
#                         ))
#                     else:
#                         conversations.append(ConversationListItem(
#                             id=row['conversation_id'],
#                             other_user=ConversationParticipant(
#                                 id=row['other_user_id'],
#                                 username=row['username'],
#                                 avatar_url=row['avatar_url'],
#                                 role=row['role']
#                             ),
#                             last_message=row['last_message'],
                            last_message_time=row['last_message_time'],
                            unread_count=row['unread_count']
                        ))
                
                return conversations
            else:
                # Supabase 实现 - 简化版本
                # 这里需要复杂的子查询，暂时返回基础数据
                return []
                
        except Exception as e:
            print(f"获取对话列表失败: {e}")
            
        return []
    
    async def get_conversation_messages(self, db_conn: Dict[str, Any], 
                                      conversation_id: int, user_id: int,
                                      limit: int = 50, offset: int = 0) -> List[Message]:
        """获取对话中的消息"""
        try:
            client = db_conn["connection"]
            
            # 验证用户是否是该对话的参与者
            part_res = await client.table('conversation_participants').select('user_id').eq('conversation_id', conversation_id).eq('user_id', user_id).execute()
            if not part_res.data:
                return [] # 或者抛出权限错误

            result = await client.table("messages").select("*").eq(
                'conversation_id', conversation_id
            ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()

            if result.data:
                return [Message.model_validate(msg) for msg in result.data]
            return []
            
            # 以下是asyncpg实现，目前未完全实现
            # if db_conn["type"] == "asyncpg":
                # # 基于用户ID获取双方的消息
                # query = """
                #     SELECT id, conversation_id, sender_id, recipient_id, content, 
                #            message_type, status, is_read, created_at, updated_at, read_at
                #     FROM messages 
                #     WHERE (sender_id = $1 AND recipient_id = $2) 
                #        OR (sender_id = $2 AND recipient_id = $1)
                #     ORDER BY created_at ASC
                #     LIMIT $3 OFFSET $4
                # """
                # results = await connection.fetch(query, user_id, conversation_id, limit, offset)
                
                return [
                    Message(
                        id=row['id'],
                        conversation_id=row['conversation_id'] or 0,
                        sender_id=row['sender_id'],
                        recipient_id=row['recipient_id'],
                        content=row['content'],
                        message_type=MessageType(row['message_type']),
                        status=MessageStatus(row['status']),
                        is_read=row['is_read'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        read_at=row['read_at']
                    )
                    for row in results
                ]
                
            else:
                # Supabase 实现
                result = await connection.table("messages").select("*").or_(
                    f"and(sender_id.eq.{user_id},recipient_id.eq.{conversation_id}),"
                    f"and(sender_id.eq.{conversation_id},recipient_id.eq.{user_id})"
                ).order("created_at", desc=False).range(offset, offset + limit - 1).execute()
                
                if result.data:
                    return [
                        Message(
                            id=msg['id'],
                            conversation_id=msg.get('conversation_id', 0),
                            sender_id=msg['sender_id'],
                            recipient_id=msg['recipient_id'],
                            content=msg['content'],
                            message_type=MessageType(msg['message_type']),
                            status=MessageStatus(msg['status']),
                            is_read=msg.get('is_read', False),
                            created_at=datetime.fromisoformat(msg['created_at']),
                            updated_at=datetime.fromisoformat(msg['updated_at']),
                            read_at=datetime.fromisoformat(msg['read_at']) if msg.get('read_at') else None
                        )
                        for msg in result.data
                    ]
                    
        except Exception as e:
            print(f"获取对话消息失败: {e}")
            
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
                # Supabase 实现
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

# 创建全局实例
message_crud = MessageCRUD()