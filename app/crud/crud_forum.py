"""
论坛系统的数据库操作
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.schemas.forum_schema import (
    PostCreate, PostUpdate, ReplyCreate, ReplyUpdate,
    ForumPost, ForumReply, ForumCategory, PopularTag, ForumAuthor, UserRole
)
import asyncpg


async def _map_post_record_to_schema(record: Dict[str, Any]) -> ForumPost:
    author_data = record.get('author', {})
    if not isinstance(author_data, dict):
        author_data = {
            "id": record.get('author_id'), "username": record.get('author_username'), "role": record.get('author_role'),
            "university": record.get('author_university'), "major": record.get('author_major'),
            "avatar_url": record.get('author_avatar_url'), "reputation": record.get('author_reputation', 0),
        }

    author = ForumAuthor(
        id=author_data.get('id') or record.get('author_id'),
        username=author_data.get('username', '未知用户'), role=author_data.get('role'),
        university=author_data.get('university'), major=author_data.get('major'),
        avatar_url=author_data.get('avatar_url'), reputation=author_data.get('reputation', 0),
    )
    
    replies_count = record.get('replies_count', 0)
    if isinstance(replies_count, list) and replies_count:
        replies_count = replies_count[0].get('count', 0)

    likes_count = record.get('likes_count', 0)
    if isinstance(likes_count, list) and likes_count:
        likes_count = likes_count[0].get('count', 0)

    return ForumPost(
        id=record['id'], title=record['title'], content=record['content'], author_id=record['author_id'], author=author,
        category=record['category'], tags=record.get('tags', []),
        replies_count=replies_count, likes_count=likes_count,
        views_count=record.get('views_count', 0), is_pinned=record.get('is_pinned', False),
        is_hot=record.get('is_hot', False), is_liked=record.get('is_liked', False),
        created_at=record['created_at'], updated_at=record['updated_at'],
        last_activity=record.get('last_activity', record['created_at'])
    )

async def _map_reply_record_to_schema(record: Dict[str, Any], user_id: Optional[int] = None) -> ForumReply:
    user_info = record.get('author', {})
    if not isinstance(user_info, dict):
        user_info = {}
    author = ForumAuthor(
        id=record.get('author_id'), username=user_info.get('username', '未知用户'),
        role=user_info.get('role'), avatar_url=user_info.get('avatar_url')
    )
    return ForumReply(
        id=record['id'], post_id=record['post_id'], author_id=record['author_id'], author=author,
        content=record['content'], parent_reply_id=record.get('parent_reply_id'),
        likes_count=record.get('likes_count', 0), is_liked=record.get('is_liked', False),
        created_at=record['created_at'], updated_at=record['updated_at'],
    )


async def get_user_by_id(db_conn, user_id: int) -> Optional[Dict[str, Any]]:
    if db_conn["type"] == "asyncpg":
        conn = db_conn["connection"]
        return await conn.fetchrow("SELECT id, username, role, avatar_url FROM users WHERE id = $1", user_id)
    else:
        client = db_conn["connection"]
        result = client.table('users').select("id, username, role, avatar_url").eq('id', user_id).execute()
        return result.data[0] if result.data else None

class ForumCRUD:
    async def get_post_by_id(self, db_conn: Dict[str, Any], post_id: int, user_id: Optional[int] = None) -> Optional[ForumPost]:
        """通过ID获取单个帖子，如果找不到则返回None"""
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                
                # 使用 .single() 可能会在找不到时抛出异常
                result = client.table("forum_posts").select("*, author:users(*), likes_count:forum_likes(count), replies_count:forum_replies(count)").eq('id', post_id).execute()

                # 检查是否有数据返回
                if not result.data:
                    return None
                
                record = result.data[0]

                if user_id:
                    liked_res = client.table('forum_likes').select('post_id').eq('user_id', user_id).eq('post_id', post_id).execute()
                    record['is_liked'] = len(liked_res.data) > 0
                else:
                    record['is_liked'] = False

                return await _map_post_record_to_schema(record)
            else:
                # asyncpg 的逻辑 (如果需要实现)
                return None
        except Exception as e:
            # 捕获预料之外的异常并打印日志
            print(f"获取帖子详情时发生异常: {e}")
            return None

    async def increment_post_views(self, db_conn: Dict[str, Any], post_id: int):
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                post_res = client.table("forum_posts").select("views_count").eq('id', post_id).execute()
                if post_res.data:
                    new_views = post_res.data[0]['views_count'] + 1
                    client.table("forum_posts").update({'views_count': new_views}).eq('id', post_id).execute()
        except Exception as e:
            print(f"增加浏览量失败: {e}")
    
    async def get_post_replies(self, db_conn: Dict[str, Any], post_id: int, user_id: Optional[int] = None, 
                               limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """获取帖子的回复列表"""
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                query = client.table("forum_replies").select("*, author:users(*)", count='exact').eq('post_id', post_id).order('created_at').range(offset, offset + limit - 1)
                result = query.execute()

                if user_id and result.data:
                    reply_ids = [r['id'] for r in result.data]
                    liked_res = client.table('forum_reply_likes').select('reply_id').eq('user_id', user_id).in_('reply_id', reply_ids).execute()
                    liked_reply_ids = {item['reply_id'] for item in liked_res.data}
                    for reply in result.data:
                        reply['is_liked'] = reply['id'] in liked_reply_ids
                
                replies = [await _map_reply_record_to_schema(r) for r in result.data]
                return {"replies": replies, "total": result.count or 0}
            else:
                return {"replies": [], "total": 0}
        except Exception as e:
            print(f"获取帖子回复失败: {e}")
            return {"replies": [], "total": 0}

    async def toggle_reply_like(self, db_conn: Dict[str, Any], reply_id: int, user_id: int) -> Dict[str, Any]:
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                query = client.table("forum_reply_likes").select("id").eq('reply_id', reply_id).eq('user_id', user_id)
                result = query.execute()
                if result.data:
                    client.table("forum_reply_likes").delete().eq('reply_id', reply_id).eq('user_id', user_id).execute()
                    is_liked = False
                else:
                    client.table("forum_reply_likes").insert({'reply_id': reply_id, 'user_id': user_id}).execute()
                    is_liked = True
                count_res = client.table("forum_reply_likes").select("id", count='exact').eq('reply_id', reply_id).execute()
                return {"is_liked": is_liked, "likes_count": count_res.count}
            else:
                return {"is_liked": False, "likes_count": 0}
        except Exception as e:
            print(f"切换回复点赞失败: {e}")
            return {"is_liked": False, "likes_count": 0}

    async def delete_reply(self, db_conn: Dict[str, Any], reply_id: int, user_id: int) -> bool:
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                result = client.table("forum_replies").delete().eq('id', reply_id).eq('author_id', user_id).execute()
                return len(result.data) > 0
            else:
                return False
        except Exception as e:
            print(f"删除回复失败: {e}")
            return False

    async def update_reply(self, db_conn: Dict[str, Any], reply_id: int, user_id: int, reply_data: ReplyUpdate) -> Optional[ForumReply]:
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                update_values = reply_data.model_dump(exclude_unset=True)
                update_values['updated_at'] = datetime.now().isoformat()
                result = client.table("forum_replies").update(update_values).eq('id', reply_id).eq('author_id', user_id).execute()
                if result.data:
                    return await self.get_reply_by_id(db_conn, reply_id)
                return None
            else:
                return None
        except Exception as e:
            print(f"更新回复失败: {e}")
            return None

    async def get_reply_by_id(self, db_conn: Dict[str, Any], reply_id: int) -> Optional[ForumReply]:
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                result = client.table("forum_replies").select("*, author:users(*)").single().eq('id', reply_id).execute()
                if result.data:
                    return await _map_reply_record_to_schema(result.data)
                return None
            else:
                return None
        except Exception as e:
            print(f"获取回复详情失败: {e}")
            return None

    async def create_reply(self, db_conn: Dict[str, Any], post_id: int, user_id: int, reply_data: ReplyCreate) -> Optional[ForumReply]:
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                user_info = await get_user_by_id(db_conn, user_id)
                if not user_info:
                    return None
                insert_data = {'post_id': post_id, 'author_id': user_id, 'content': reply_data.content}
                if reply_data.parent_id:
                    insert_data['parent_reply_id'] = reply_data.parent_id
                result = client.table("forum_replies").insert(insert_data).execute()
                if result.data:
                    record = result.data[0]
                    record['author'] = user_info
                    return await _map_reply_record_to_schema(record)
                return None
            else:
                return None
        except Exception as e:
            print(f"创建回复失败: {e}")
            return None

    async def toggle_post_like(self, db_conn: Dict[str, Any], post_id: int, user_id: int) -> Dict[str, Any]:
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                query = client.table("forum_likes").select("id").eq('post_id', post_id).eq('user_id', user_id)
                result = query.execute()
                if result.data:
                    client.table("forum_likes").delete().eq('post_id', post_id).eq('user_id', user_id).execute()
                    is_liked = False
                else:
                    client.table("forum_likes").insert({'post_id': post_id, 'user_id': user_id}).execute()
                    is_liked = True
                count_res = client.table("forum_likes").select("id", count='exact').eq('post_id', post_id).execute()
                return {"is_liked": is_liked, "likes_count": count_res.count}
            else:
                return {"is_liked": False, "likes_count": 0}
        except Exception as e:
            print(f"切换点赞失败: {e}")
            return {"is_liked": False, "likes_count": 0}

    async def delete_post(self, db_conn: Dict[str, Any], post_id: int, user_id: int) -> bool:
        """删除帖子，成功返回True，失败返回False"""
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                
                # 首先检查帖子是否存在且属于该用户
                post_check = client.table("forum_posts").select("id").eq('id', post_id).eq('author_id', user_id).execute()
                if not post_check.data:
                    return False  # 帖子不存在或不属于该用户

                # 执行删除
                result = client.table("forum_posts").delete().eq('id', post_id).eq('author_id', user_id).execute()
                
                # Supabase V1 的 delete 在成功时通常返回包含已删除内容的 data 列表
                return result.data is not None and len(result.data) > 0
            else:
                # asyncpg 的逻辑 (如果需要实现)
                return False
        except Exception as e:
            print(f"删除帖子时发生异常: {e}")
            return False

    async def update_post(self, db_conn: Dict[str, Any], post_id: int, user_id: int, post_data: PostUpdate) -> Optional[ForumPost]:
        try:
            if db_conn["type"] != "asyncpg":
                client = db_conn["connection"]
                update_values = post_data.model_dump(exclude_unset=True)
                update_values['updated_at'] = datetime.now().isoformat()
                result = client.table("forum_posts").update(update_values).eq('id', post_id).eq('author_id', user_id).execute()
                if result.data:
                    return await self.get_post_by_id(db_conn, post_id)
                return None
            else:
                return None
        except Exception as e:
            print(f"更新帖子失败: {e}")
            return None

    async def get_categories(self) -> List[ForumCategory]:
        return [
            ForumCategory(id="application", name="申请经验", description="分享申请经验、文书写作、面试技巧", post_count=156, icon="📝"),
            ForumCategory(id="university", name="院校讨论", description="各大学校信息、专业介绍、校园生活", post_count=234, icon="🏫"),
        ]
        
    async def create_post(self, db_conn: Dict[str, Any], user_id: int, post_data: PostCreate) -> Optional[ForumPost]:
        try:
            user_info = await get_user_by_id(db_conn, user_id)
            if not user_info:
                print(f"创建帖子失败: 无法找到ID为 {user_id} 的用户")
                return None
            if db_conn["type"] == "asyncpg":
                conn = db_conn["connection"]
                query = """
                    INSERT INTO forum_posts (title, content, author_id, category, tags, is_anonymous)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING *;
                """
                record = await conn.fetchrow(query, post_data.title, post_data.content, user_id, post_data.category, post_data.tags, post_data.is_anonymous)
            else:
                client = db_conn["connection"]
                insert_data = {'title': post_data.title, 'content': post_data.content, 'author_id': user_id, 'category': post_data.category, 'tags': post_data.tags, 'is_anonymous': post_data.is_anonymous}
                result = client.table('forum_posts').insert(insert_data).execute()
                record = result.data[0] if result.data else None

            if record:
                full_record = dict(record)
                full_record.update({
                    'author_username': user_info.get('username', '未知用户'), 'author_role': user_info.get('role'),
                    'author_avatar_url': user_info.get('avatar_url'), 'author_university': None, 
                    'author_major': None, 'author_reputation': 0, 'is_liked': False
                })
                return await _map_post_record_to_schema(full_record)
            return None
        except Exception as e:
            print(f"创建帖子失败: {e}")
            return None
    
    async def get_posts(self, db_conn: Dict[str, Any], 
                       category: Optional[str] = None, author_id: Optional[int] = None, search: Optional[str] = None,
                       sort_by: str = "latest", sort_order: str = "desc", limit: int = 20, offset: int = 0,
                       user_id: Optional[int] = None) -> Dict[str, Any]:
        if db_conn["type"] != "asyncpg":
            client = db_conn["connection"]
            try:
                query = client.table("forum_posts").select("*, author:users(*), likes_count:forum_likes(count), replies_count:forum_replies(count)", count='exact')
                if category:
                    query = query.eq('category', category)
                if author_id:
                    query = query.eq('author_id', author_id)
                if search:
                    query = query.or_(f"title.ilike.%{search}%,content.ilike.%{search}%")
                order_map = {"latest": "last_activity", "hot": "views_count", "replies": "replies_count", "created_at": "created_at"}
                order_col = order_map.get(sort_by, "last_activity")
                query = query.order('is_pinned', desc=True).order(order_col, desc=(sort_order == "desc")).range(offset, offset + limit - 1)
                result = query.execute()

                if user_id and result.data:
                    post_ids = [p['id'] for p in result.data]
                    liked_res = client.table('forum_likes').select('post_id').eq('user_id', user_id).in_('post_id', post_ids).execute()
                    liked_post_ids = {item['post_id'] for item in liked_res.data}
                    for post in result.data:
                        post['is_liked'] = post['id'] in liked_post_ids
                
                posts = [await _map_post_record_to_schema(p) for p in result.data]
                return {"posts": posts, "total": result.count or 0}
            except Exception as e:
                print(f"获取帖子列表失败 (Supabase): {e}")
                return {"posts": [], "total": 0}
        
        return {"posts": [], "total": 0}

    async def get_popular_tags(self, db_conn: Dict[str, Any], limit: int = 20) -> List[PopularTag]:
        return []
        
    async def get_user_posts(self, db_conn: Dict[str, Any], user_id: int, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return {"posts": [], "total": 0}
        
    async def get_user_replies(self, db_conn: Dict[str, Any], user_id: int, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return {"replies": [], "total": 0}
        
    async def report_post(self, db_conn: Dict[str, Any], post_id: int, user_id: int, reason: str) -> bool:
        return False
        
    async def report_reply(self, db_conn: Dict[str, Any], reply_id: int, user_id: int, reason: str) -> bool:
        return False

forum_crud = ForumCRUD()
