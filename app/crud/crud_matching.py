from typing import Optional, List, Dict, Any
from app.schemas.matching_schema import MatchingRequest, MatchingFilter, RecommendationRequest
import asyncpg
from supabase import Client
import uuid
from datetime import datetime

async def create_matching_request(db_conn: Dict[str, Any], student_user_id: int, request: MatchingRequest) -> str:
    """创建匹配请求并返回请求ID"""
    try:
        request_id = str(uuid.uuid4())
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            await conn.execute(
                """
                INSERT INTO mentor_matches 
                (id, student_id, target_universities, target_majors, degree_level, service_categories, 
                 budget_min, budget_max, preferred_languages, urgency, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'pending')
                """,
                request_id, student_user_id, request.target_universities, request.target_majors,
                request.degree_level, request.service_categories, request.budget_min,
                request.budget_max, request.preferred_languages, request.urgency
            )
        else:
            client: Client = db_conn["connection"]
            client.table('mentor_matches').insert({
                'id': request_id,
                'student_id': student_user_id,
                'target_universities': request.target_universities,
                'target_majors': request.target_majors,
                'degree_level': request.degree_level,
                'service_categories': request.service_categories,
                'budget_min': request.budget_min,
                'budget_max': request.budget_max,
                'preferred_languages': request.preferred_languages,
                'urgency': request.urgency,
                'status': 'pending'
            }).execute()
        return request_id
    except Exception as e:
        print(f"创建匹配请求失败: {e}")
        return None

async def calculate_match_scores(db_conn: Dict[str, Any], request: MatchingRequest) -> List[Dict]:
    """计算匹配分数"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 复杂的匹配算法查询
            results = await conn.fetch(
                """
                SELECT 
                    mr.*,
                    u.username,
                    p.full_name,
                    p.avatar_url,
                    -- 大学匹配度
                    CASE 
                        WHEN mr.university = ANY($1) THEN 0.3
                        ELSE 0.0
                    END as university_match,
                    -- 专业匹配度
                    CASE 
                        WHEN mr.major = ANY($2) THEN 0.25
                        ELSE 0.0
                    END as major_match,
                    -- 学位匹配度
                    CASE 
                        WHEN mr.degree_level = $3 THEN 0.2
                        ELSE 0.0
                    END as degree_match,
                    -- 评分权重
                    COALESCE(mr.rating / 5.0, 0) * 0.15 as rating_score,
                    -- 语言匹配度
                    CASE 
                        WHEN $4 IS NULL OR mr.languages && $4 THEN 0.1
                        ELSE 0.0
                    END as language_match,
                    -- 总分计算
                    (
                        CASE WHEN mr.university = ANY($1) THEN 0.3 ELSE 0.0 END +
                        CASE WHEN mr.major = ANY($2) THEN 0.25 ELSE 0.0 END +
                        CASE WHEN mr.degree_level = $3 THEN 0.2 ELSE 0.0 END +
                        COALESCE(mr.rating / 5.0, 0) * 0.15 +
                        CASE WHEN $4 IS NULL OR mr.languages && $4 THEN 0.1 ELSE 0.0 END
                    ) as total_score
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr.verification_status = 'verified'
                ORDER BY total_score DESC, mr.rating DESC
                LIMIT 50
                """,
                request.target_universities, request.target_majors, request.degree_level,
                request.preferred_languages
            )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            # 简化版匹配逻辑
            result = client.table('mentorship_relationships').select(
                '*, users:user_id(username), profiles:user_id(full_name, avatar_url)'
            ).eq('verification_status', 'verified').order('rating', desc=True).limit(50).execute()
            
            # 在Python中计算匹配分数
            matches = []
            for mentor in result.data:
                score = 0.0
                if mentor['university'] in request.target_universities:
                    score += 0.3
                if mentor['major'] in request.target_majors:
                    score += 0.25
                if mentor['degree_level'] == request.degree_level:
                    score += 0.2
                if mentor['rating']:
                    score += (mentor['rating'] / 5.0) * 0.15
                if not request.preferred_languages or any(lang in mentor.get('languages', []) for lang in request.preferred_languages):
                    score += 0.1
                
                mentor['total_score'] = score
                mentor['university_match'] = 0.3 if mentor['university'] in request.target_universities else 0.0
                mentor['major_match'] = 0.25 if mentor['major'] in request.target_majors else 0.0
                mentor['degree_match'] = 0.2 if mentor['degree_level'] == request.degree_level else 0.0
                mentor['rating_score'] = (mentor['rating'] / 5.0) * 0.15 if mentor['rating'] else 0.0
                mentor['language_match'] = 0.1 if not request.preferred_languages or any(lang in mentor.get('languages', []) for lang in request.preferred_languages) else 0.0
                matches.append(mentor)
            
            # 按分数排序
            matches.sort(key=lambda x: x['total_score'], reverse=True)
            return matches
    except Exception as e:
        print(f"计算匹配分数失败: {e}")
        return []

async def save_matching_result(db_conn: Dict[str, Any], request_id: str, student_id: int, matches: List[Dict]) -> bool:
    """保存匹配结果"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 更新匹配请求状态
            await conn.execute(
                "UPDATE mentor_matches SET status = 'completed', updated_at = NOW() WHERE id = $1",
                request_id
            )
            
            # 保存匹配历史
            for i, match in enumerate(matches[:20]):  # 只保存前20个匹配
                await conn.execute(
                    """
                    INSERT INTO mentorship_relationships 
                    (student_id, mentor_id, match_score, status, created_at)
                    VALUES ($1, $2, $3, 'pending', NOW())
                    ON CONFLICT (student_id, mentor_id) DO UPDATE SET
                    match_score = $3, updated_at = NOW()
                    """,
                    student_id, match['id'], match['total_score']
                )
        else:
            client: Client = db_conn["connection"]
            # 更新匹配请求状态
            client.table('mentor_matches').update({'status': 'completed'}).eq('id', request_id).execute()
            
            # 保存匹配历史（简化版）
            for match in matches[:20]:
                try:
                    client.table('mentorship_relationships').insert({
                        'student_id': student_id,
                        'mentor_id': match['id'],
                        'match_score': match['total_score'],
                        'status': 'pending'
                    }).execute()
                except:
                    # 如果已存在则更新
                    client.table('mentorship_relationships').update({
                        'match_score': match['total_score']
                    }).eq('student_id', student_id).eq('mentor_id', match['id']).execute()
        return True
    except Exception as e:
        print(f"保存匹配结果失败: {e}")
        return False

async def get_matching_history(db_conn: Dict[str, Any], student_user_id: int, limit: int = 20) -> List[Dict]:
    """获取匹配历史"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            results = await conn.fetch(
                """
                SELECT 
                    mr_rel.*,
                    mr.university, mr.major, mr.degree_level, mr.rating,
                    u.username, p.full_name, p.avatar_url
                FROM mentorship_relationships mr_rel
                JOIN mentorship_relationships mr ON mr_rel.mentor_id = mr.id
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr_rel.student_id = $1
                ORDER BY mr_rel.created_at DESC
                LIMIT $2
                """,
                student_user_id, limit
            )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_relationships').select('*').eq('student_id', student_user_id).order('created_at', desc=True).limit(limit).execute()
            return result.data
    except Exception as e:
        print(f"获取匹配历史失败: {e}")
        return []

async def get_advanced_filters(db_conn: Dict[str, Any]) -> Dict:
    """获取高级筛选选项"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 获取所有可用的筛选选项
            universities = await conn.fetch(
                "SELECT DISTINCT university FROM mentorship_relationships WHERE verification_status = 'verified' ORDER BY university"
            )
            majors = await conn.fetch(
                "SELECT DISTINCT major FROM mentorship_relationships WHERE verification_status = 'verified' ORDER BY major"
            )
            degree_levels = await conn.fetch(
                "SELECT DISTINCT degree_level FROM mentorship_relationships WHERE verification_status = 'verified' ORDER BY degree_level"
            )
            
            return {
                'universities': [row['university'] for row in universities],
                'majors': [row['major'] for row in majors],
                'degree_levels': [row['degree_level'] for row in degree_levels],
                'rating_range': {'min': 1, 'max': 5},
                'graduation_year_range': {'min': 2015, 'max': 2030}
            }
        else:
            client: Client = db_conn["connection"]
            # 简化版筛选选项
            mentors = client.table('mentorship_relationships').select('university, major, degree_level').eq('verification_status', 'verified').execute()
            
            universities = list(set([m['university'] for m in mentors.data if m['university']]))
            majors = list(set([m['major'] for m in mentors.data if m['major']]))
            degree_levels = list(set([m['degree_level'] for m in mentors.data if m['degree_level']]))
            
            return {
                'universities': sorted(universities),
                'majors': sorted(majors),
                'degree_levels': sorted(degree_levels),
                'rating_range': {'min': 1, 'max': 5},
                'graduation_year_range': {'min': 2015, 'max': 2030}
            }
    except Exception as e:
        print(f"获取筛选选项失败: {e}")
        return {}

async def apply_advanced_filters(db_conn: Dict[str, Any], filters: MatchingFilter, limit: int = 20, offset: int = 0) -> List[Dict]:
    """应用高级筛选"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            where_clauses = ["mr.verification_status = 'verified'"]
            params = []
            param_count = 0
            
            if filters.universities:
                param_count += 1
                where_clauses.append(f"mr.university = ANY(${param_count})")
                params.append(filters.universities)
                
            if filters.majors:
                param_count += 1
                where_clauses.append(f"mr.major = ANY(${param_count})")
                params.append(filters.majors)
                
            if filters.degree_levels:
                param_count += 1
                where_clauses.append(f"mr.degree_level = ANY(${param_count})")
                params.append(filters.degree_levels)
                
            if filters.graduation_year_min:
                param_count += 1
                where_clauses.append(f"mr.graduation_year >= ${param_count}")
                params.append(filters.graduation_year_min)
                
            if filters.graduation_year_max:
                param_count += 1
                where_clauses.append(f"mr.graduation_year <= ${param_count}")
                params.append(filters.graduation_year_max)
                
            if filters.rating_min:
                param_count += 1
                where_clauses.append(f"mr.rating >= ${param_count}")
                params.append(filters.rating_min)
                
            if filters.min_sessions:
                param_count += 1
                where_clauses.append(f"mr.total_sessions >= ${param_count}")
                params.append(filters.min_sessions)
                
            if filters.specialties:
                param_count += 1
                where_clauses.append(f"mr.specialties && ${param_count}")
                params.append(filters.specialties)
                
            if filters.languages:
                param_count += 1
                where_clauses.append(f"mr.languages && ${param_count}")
                params.append(filters.languages)
            
            where_clause = " AND ".join(where_clauses)
            param_count += 1
            limit_param = f"${param_count}"
            param_count += 1
            offset_param = f"${param_count}"
            
            query = f"""
                SELECT mr.*, u.username, p.full_name, p.avatar_url
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE {where_clause}
                ORDER BY mr.rating DESC, mr.total_sessions DESC
                LIMIT {limit_param} OFFSET {offset_param}
            """
            
            results = await conn.fetch(query, *params, limit, offset)
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            query = client.table('mentorship_relationships').select(
                '*, users:user_id(username), profiles:user_id(full_name, avatar_url)'
            ).eq('verification_status', 'verified')
            
            # 应用筛选条件
            if filters.universities:
                query = query.in_('university', filters.universities)
            if filters.majors:
                query = query.in_('major', filters.majors)
            if filters.degree_levels:
                query = query.in_('degree_level', filters.degree_levels)
            if filters.graduation_year_min:
                query = query.gte('graduation_year', filters.graduation_year_min)
            if filters.graduation_year_max:
                query = query.lte('graduation_year', filters.graduation_year_max)
            if filters.rating_min:
                query = query.gte('rating', filters.rating_min)
            if filters.min_sessions:
                query = query.gte('total_sessions', filters.min_sessions)
                
            result = query.order('rating', desc=True).order('total_sessions', desc=True).range(offset, offset + limit - 1).execute()
            return result.data
    except Exception as e:
        print(f"应用高级筛选失败: {e}")
        return []

async def get_recommendation_for_context(db_conn: Dict[str, Any], request: RecommendationRequest, user_id: int) -> List[Dict]:
    """根据上下文获取推荐"""
    try:
        if request.context == "homepage":
            # 首页推荐：热门指导者
            return await get_popular_mentors(db_conn, request.limit, request.exclude_ids)
        elif request.context == "search":
            # 搜索页推荐：基于用户偏好
            return await get_preference_based_recommendations(db_conn, user_id, request.user_preferences, request.limit, request.exclude_ids)
        elif request.context == "profile":
            # 个人资料页推荐：相似背景
            return await get_similar_background_mentors(db_conn, user_id, request.limit, request.exclude_ids)
        elif request.context == "service":
            # 服务页推荐：相关服务提供者
            return await get_service_related_mentors(db_conn, request.user_preferences, request.limit, request.exclude_ids)
        else:
            return []
    except Exception as e:
        print(f"获取上下文推荐失败: {e}")
        return []

async def get_popular_mentors(db_conn: Dict[str, Any], limit: int, exclude_ids: List[int] = None) -> List[Dict]:
    """获取热门指导者"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            exclude_clause = ""
            params = []
            if exclude_ids:
                exclude_clause = "AND mr.id != ALL($1)"
                params.append(exclude_ids)
            
            query = f"""
                SELECT mr.*, u.username, p.full_name, p.avatar_url
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr.verification_status = 'verified' {exclude_clause}
                ORDER BY mr.rating DESC, mr.total_sessions DESC
                LIMIT ${len(params) + 1}
            """
            
            results = await conn.fetch(query, *params, limit)
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            query = client.table('mentorship_relationships').select(
                '*, users:user_id(username), profiles:user_id(full_name, avatar_url)'
            ).eq('verification_status', 'verified')
            
            if exclude_ids:
                query = query.not_.in_('id', exclude_ids)
                
            result = query.order('rating', desc=True).order('total_sessions', desc=True).limit(limit).execute()
            return result.data
    except Exception as e:
        print(f"获取热门指导者失败: {e}")
        return []

async def get_preference_based_recommendations(db_conn: Dict[str, Any], user_id: int, preferences: Dict, limit: int, exclude_ids: List[int] = None) -> List[Dict]:
    """基于用户偏好的推荐"""
    try:
        # 这里可以实现复杂的偏好匹配算法
        # 简化版：基于目标学校和专业推荐
        target_universities = preferences.get('target_universities', [])
        target_majors = preferences.get('target_majors', [])
        
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            exclude_clause = ""
            params = [target_universities, target_majors]
            if exclude_ids:
                exclude_clause = "AND mr.id != ALL($3)"
                params.append(exclude_ids)
            
            query = f"""
                SELECT mr.*, u.username, p.full_name, p.avatar_url,
                       CASE WHEN mr.university = ANY($1) THEN 1 ELSE 0 END +
                       CASE WHEN mr.major = ANY($2) THEN 1 ELSE 0 END as preference_score
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr.verification_status = 'verified' {exclude_clause}
                ORDER BY preference_score DESC, mr.rating DESC
                LIMIT ${len(params) + 1}
            """
            
            results = await conn.fetch(query, *params, limit)
            return [dict(row) for row in results]
        else:
            # 简化版Supabase实现
            return await get_popular_mentors(db_conn, limit, exclude_ids)
    except Exception as e:
        print(f"获取偏好推荐失败: {e}")
        return []

async def get_similar_background_mentors(db_conn: Dict[str, Any], user_id: int, limit: int, exclude_ids: List[int] = None) -> List[Dict]:
    """获取相似背景的指导者"""
    try:
        # 获取用户背景信息
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            user_bg = await conn.fetchrow(
                "SELECT target_universities, target_majors, target_degree FROM user_learning_needs WHERE user_id = $1",
                user_id
            )
            
            if user_bg:
                exclude_clause = ""
                params = [user_bg['target_universities'], user_bg['target_majors'], user_bg['target_degree']]
                if exclude_ids:
                    exclude_clause = "AND mr.id != ALL($4)"
                    params.append(exclude_ids)
                
                query = f"""
                    SELECT mr.*, u.username, p.full_name, p.avatar_url
                    FROM mentorship_relationships mr
                    JOIN users u ON mr.user_id = u.id
                    LEFT JOIN profiles p ON u.id = p.user_id
                    WHERE mr.verification_status = 'verified' 
                    AND (mr.university = ANY($1) OR mr.major = ANY($2) OR mr.degree_level = $3)
                    {exclude_clause}
                    ORDER BY mr.rating DESC
                    LIMIT ${len(params) + 1}
                """
                
                results = await conn.fetch(query, *params, limit)
                return [dict(row) for row in results]
        
        # 如果没有背景信息或使用Supabase，返回热门推荐
        return await get_popular_mentors(db_conn, limit, exclude_ids)
    except Exception as e:
        print(f"获取相似背景推荐失败: {e}")
        return []

async def get_service_related_mentors(db_conn: Dict[str, Any], preferences: Dict, limit: int, exclude_ids: List[int] = None) -> List[Dict]:
    """获取相关服务的指导者"""
    try:
        service_category = preferences.get('service_category')
        if not service_category:
            return await get_popular_mentors(db_conn, limit, exclude_ids)
            
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            exclude_clause = ""
            params = [service_category]
            if exclude_ids:
                exclude_clause = "AND mr.id != ALL($2)"
                params.append(exclude_ids)
            
            query = f"""
                SELECT DISTINCT mr.*, u.username, p.full_name, p.avatar_url
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                JOIN services s ON s.mentor_id = mr.id
                WHERE mr.verification_status = 'verified' 
                AND s.category = $1 AND s.is_active = true
                {exclude_clause}
                ORDER BY mr.rating DESC, s.rating DESC
                LIMIT ${len(params) + 1}
            """
            
            results = await conn.fetch(query, *params, limit)
            return [dict(row) for row in results]
        else:
            # 简化版Supabase实现
            return await get_popular_mentors(db_conn, limit, exclude_ids)
    except Exception as e:
        print(f"获取服务相关推荐失败: {e}")
        return [] 