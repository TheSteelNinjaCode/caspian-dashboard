"""Auto-generated Async Prisma-style Database Client - Direct SQL for FastAPI"""
import os
import json
import asyncio
from enum import Enum as PyEnum
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable, AsyncGenerator, Union, Tuple, Mapping, cast, Set, Awaitable
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from dotenv import load_dotenv
import contextvars

import aiosqlite
from aiosqlite import Connection, Cursor

from .models import (
    User, UserRole,
    UserWhereInput, UserWhereUniqueInput, UserSelect, UserOmit, UserInclude, UserOrderBy, UserCreateInput, UserUpdateInput, UserRoleWhereInput, UserRoleWhereUniqueInput, UserRoleSelect, UserRoleOmit, UserRoleInclude, UserRoleOrderBy, UserRoleCreateInput, UserRoleUpdateInput,
    generate_cuid,
    generate_uuid,
    generate_nanoid,
    generate_ulid,
    utc_now_str,
    get_datetime_value,
    SelectDict,
    IncludeDict,
)

load_dotenv()


class AsyncConnectionPool:
    """Async connection pool for database connections"""

    def __init__(
        self,
        create_conn: Callable[[], Awaitable[Connection]],
        size: int = 5
    ) -> None:
        self._create = create_conn
        self._size = size
        self._pool: asyncio.Queue[Connection] = asyncio.Queue(maxsize=size)
        self._lock = asyncio.Lock()
        self._initialized = False
        self._connections: List[Connection] = []

    async def _init_pool(self) -> None:
        if self._initialized:
            return
        async with self._lock:
            if self._initialized:
                return
            for _ in range(self._size):
                conn = await self._create()
                self._connections.append(conn)
                await self._pool.put(conn)
            self._initialized = True

    async def get(self) -> Connection:
        await self._init_pool()
        return await self._pool.get()

    async def put(self, conn: Connection) -> None:
        try:
            self._pool.put_nowait(conn)
        except asyncio.QueueFull:
            await conn.close()

    async def close_all(self) -> None:
        for conn in self._connections:
            try:
                await conn.close()
            except Exception:
                pass
        self._connections.clear()
        self._initialized = False


class PreparedStatementCache:
    """LRU cache for prepared SQL statements"""

    def __init__(self, max_size: int = 100) -> None:
        from collections import OrderedDict
        self._cache: "OrderedDict[str, str]" = OrderedDict()
        self._max_size = max_size

    def get(self, key: str) -> Optional[str]:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def set(self, key: str, sql: str) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            self._cache[key] = sql

    def clear(self) -> None:
        self._cache.clear()


class RecordNotFoundError(Exception):
    """Raised when a required record is not found"""
    pass


class SQLBuilder:
    """Build SQL queries from Prisma-style inputs"""

    PROVIDER = "sqlite"
    PARAM_STYLE = "?"

    @classmethod
    def placeholder(cls, index: int = 0) -> str:
        if cls.PROVIDER == "postgresql":
            return f"${index + 1}"
        return cls.PARAM_STYLE

    @classmethod
    def _convert_value(cls, value: Any) -> Any:
        """Convert Python types to database-compatible values"""
        if isinstance(value, PyEnum):
            return value.value
        return value

    @classmethod
    def build_where(cls, where: Dict[str, Any], table: str = "", param_offset: int = 0) -> Tuple[str, List[Any], int]:
        """Build WHERE clause from Prisma-style where dict. Returns (sql, params, next_param_index)"""
        if not where:
            return "", [], param_offset

        conditions: List[str] = []
        params: List[Any] = []
        idx = param_offset

        for key, value in where.items():
            if key == "AND" and isinstance(value, list):
                sub_conditions = []
                for w in value:
                    sql, p, idx = cls.build_where(w, table, idx)
                    if sql:
                        sub_conditions.append(f"({sql})")
                        params.extend(p)
                if sub_conditions:
                    conditions.append(f"({' AND '.join(sub_conditions)})")

            elif key == "OR" and isinstance(value, list):
                sub_conditions = []
                for w in value:
                    sql, p, idx = cls.build_where(w, table, idx)
                    if sql:
                        sub_conditions.append(f"({sql})")
                        params.extend(p)
                if sub_conditions:
                    conditions.append(f"({' OR '.join(sub_conditions)})")

            elif key == "NOT" and isinstance(value, dict):
                sql, p, idx = cls.build_where(value, table, idx)
                if sql:
                    conditions.append(f"NOT ({sql})")
                    params.extend(p)

            elif isinstance(value, dict):
                col = f'"{key}"' if table == "" else f'"{table}"."{key}"'
                mode = value.get("mode", "default")

                for op, val in value.items():
                    if op == "mode":
                        continue
                    elif op == "equals":
                        if mode == "insensitive":
                            conditions.append(f"LOWER({col}) = LOWER({cls.placeholder(idx)})")
                        else:
                            conditions.append(f"{col} = {cls.placeholder(idx)}")
                        params.append(cls._convert_value(val))
                        idx += 1
                    elif op in ("not", "not_"):
                        if mode == "insensitive":
                            conditions.append(f"LOWER({col}) != LOWER({cls.placeholder(idx)})")
                        else:
                            conditions.append(f"{col} != {cls.placeholder(idx)}")
                        params.append(cls._convert_value(val))
                        idx += 1
                    elif op in ("in", "in_"):
                        converted_vals = [cls._convert_value(v) for v in val]
                        placeholders = ", ".join([cls.placeholder(idx + i) for i in range(len(converted_vals))])
                        conditions.append(f"{col} IN ({placeholders})")
                        params.extend(converted_vals)
                        idx += len(converted_vals)
                    elif op == "notIn":
                        converted_vals = [cls._convert_value(v) for v in val]
                        placeholders = ", ".join([cls.placeholder(idx + i) for i in range(len(converted_vals))])
                        conditions.append(f"{col} NOT IN ({placeholders})")
                        params.extend(converted_vals)
                        idx += len(converted_vals)
                    elif op == "lt":
                        conditions.append(f"{col} < {cls.placeholder(idx)}")
                        params.append(cls._convert_value(val))
                        idx += 1
                    elif op == "lte":
                        conditions.append(f"{col} <= {cls.placeholder(idx)}")
                        params.append(cls._convert_value(val))
                        idx += 1
                    elif op == "gt":
                        conditions.append(f"{col} > {cls.placeholder(idx)}")
                        params.append(cls._convert_value(val))
                        idx += 1
                    elif op == "gte":
                        conditions.append(f"{col} >= {cls.placeholder(idx)}")
                        params.append(cls._convert_value(val))
                        idx += 1
                    elif op == "contains":
                        if mode == "insensitive":
                            conditions.append(f"LOWER({col}) LIKE LOWER({cls.placeholder(idx)})")
                        else:
                            conditions.append(f"{col} LIKE {cls.placeholder(idx)}")
                        params.append(f"%{val}%")
                        idx += 1
                    elif op == "startsWith":
                        if mode == "insensitive":
                            conditions.append(f"LOWER({col}) LIKE LOWER({cls.placeholder(idx)})")
                        else:
                            conditions.append(f"{col} LIKE {cls.placeholder(idx)}")
                        params.append(f"{val}%")
                        idx += 1
                    elif op == "endsWith":
                        if mode == "insensitive":
                            conditions.append(f"LOWER({col}) LIKE LOWER({cls.placeholder(idx)})")
                        else:
                            conditions.append(f"{col} LIKE {cls.placeholder(idx)}")
                        params.append(f"%{val}")
                        idx += 1
                    elif op == "isNull":
                        conditions.append(f"{col} IS NULL" if val else f"{col} IS NOT NULL")
            else:
                col = f'"{key}"' if table == "" else f'"{table}"."{key}"'
                conditions.append(f"{col} = {cls.placeholder(idx)}")
                if isinstance(value, bool):
                    if cls.PROVIDER == "sqlite":
                        params.append(1 if value else 0)
                    else:
                        params.append(value)
                elif isinstance(value, datetime):
                    # PostgreSQL (asyncpg) needs naive datetime, SQLite needs string
                    if cls.PROVIDER == "sqlite":
                        params.append(value.isoformat())
                    else:
                        # Strip timezone for asyncpg TIMESTAMP compatibility
                        params.append(value.replace(tzinfo=None) if value.tzinfo else value)
                elif isinstance(value, PyEnum):
                    params.append(value.value)
                else:
                    params.append(value)
                idx += 1

        return " AND ".join(conditions), params, idx

    @classmethod
    def build_order_by(cls, order_by: Dict[str, Any], table: str = "") -> str:
        """Build ORDER BY clause"""
        if not order_by:
            return ""

        parts: List[str] = []
        for field, direction in order_by.items():
            if field.startswith("_"):
                continue
            col = f'"{field}"' if table == "" else f'"{table}"."{field}"'
            if isinstance(direction, dict):
                sort_dir = direction.get("sort", "asc").upper()
                nulls = direction.get("nulls")
                part = f"{col} {sort_dir}"
                if nulls == "first":
                    part += " NULLS FIRST"
                elif nulls == "last":
                    part += " NULLS LAST"
                parts.append(part)
            else:
                parts.append(f"{col} {direction.upper()}")

        return f"ORDER BY {', '.join(parts)}" if parts else ""

    @classmethod
    def build_select(cls, table: str, fields: List[str], select: Optional[SelectDict] = None, omit: Optional[SelectDict] = None) -> Tuple[str, List[str]]:
        """Build SELECT columns, returns (sql_cols, selected_field_names)"""
        selected: List[str] = []
        if select:
            selected = [f for f in fields if select.get(f, False)]
        elif omit:
            selected = [f for f in fields if not omit.get(f, False)]
        else:
            selected = fields[:]

        if not selected:
            return "*", fields

        cols = ", ".join([f'"{f}"' for f in selected])
        return cols, selected

    @classmethod
    def build_distinct(cls, distinct: Optional[List[str]], table: str = "") -> str:
        """Build DISTINCT ON clause (PostgreSQL) or just DISTINCT"""
        if not distinct:
            return ""
        if cls.PROVIDER == "postgresql":
            cols = ", ".join([f'"{d}"' for d in distinct])
            return f"DISTINCT ON ({cols})"
        return "DISTINCT"


def apply_atomic_update(current: Any, field: str, value: Any) -> Any:
    """Apply atomic operations and return new value"""
    if isinstance(value, dict):
        curr = current or 0
        if "set" in value:
            return value["set"]
        elif "increment" in value:
            return curr + value["increment"]
        elif "decrement" in value:
            return curr - value["decrement"]
        elif "multiply" in value:
            return curr * value["multiply"]
        elif "divide" in value:
            return curr / value["divide"] if value["divide"] != 0 else curr
    return value



# User table info
USER_TABLE = "User" 
USER_PK = "id"
USER_FIELDS = ["id", "name", "email", "password", "emailVerified", "image", "createdAt", "updatedAt", "roleId"]
USER_NUMERIC_FIELDS = ["roleId"]
USER_DATETIME_FIELDS = ["emailVerified", "createdAt", "updatedAt"]
USER_ENUM_FIELDS: Dict[str, Any] = {}


# UserRole table info
USERROLE_TABLE = "UserRole" 
USERROLE_PK = "id"
USERROLE_FIELDS = ["id", "name"]
USERROLE_NUMERIC_FIELDS = ["id"]
USERROLE_DATETIME_FIELDS = []
USERROLE_ENUM_FIELDS: Dict[str, Any] = {}


class UserDelegate:
    """Async Direct SQL delegate for User"""

    TABLE = "User"
    PK = "id"
    FIELDS = USER_FIELDS
    NUMERIC_FIELDS = USER_NUMERIC_FIELDS
    DATETIME_FIELDS = USER_DATETIME_FIELDS
    ENUM_FIELDS = USER_ENUM_FIELDS

    def __init__(
        self,
        get_conn: Callable[[], Awaitable[Connection]],
        get_delegate: Callable[[str], Any]
    ) -> None:
        self._get_conn = get_conn
        self._get_delegate = get_delegate

    def _row_to_model(self, row: Any, columns: List[str]) -> User:
        """Convert row to model instance"""
        if isinstance(row, dict):
            data = row
        else:
            data = dict(zip(columns, row))
        # Convert datetime strings back to datetime objects
        if data.get("emailVerified") and isinstance(data["emailVerified"], str):
            try:
                data["emailVerified"] = datetime.fromisoformat(data["emailVerified"])
            except: pass
        if data.get("createdAt") and isinstance(data["createdAt"], str):
            try:
                data["createdAt"] = datetime.fromisoformat(data["createdAt"])
            except: pass
        if data.get("updatedAt") and isinstance(data["updatedAt"], str):
            try:
                data["updatedAt"] = datetime.fromisoformat(data["updatedAt"])
            except: pass


        # Convert enum string values back to enum instances
        for enum_field, enum_class in self.ENUM_FIELDS.items():
            if enum_field in data and data[enum_field] is not None:
                try:
                    data[enum_field] = enum_class(data[enum_field])
                except (ValueError, KeyError):
                    pass  # Keep original value if conversion fails
        return User(**{k: v for k, v in data.items() if k in self.FIELDS})

    def _apply_query_options(
        self,
        record: User,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None,
        include: Optional[UserInclude] = None,
    ) -> User:
        """Store query options on record for to_dict()"""
        record._stored_select = dict(select) if select else None
        record._stored_omit = dict(omit) if omit else None
        record._stored_include = dict(include) if include else None
        return record

    def _generate_defaults(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default values for ID and timestamp fields"""
        if "id" not in data_dict:
            data_dict["id"] = generate_cuid()
        if "createdAt" not in data_dict:
            data_dict["createdAt"] = get_datetime_value(SQLBuilder.PROVIDER)
        if "updatedAt" not in data_dict:
            data_dict["updatedAt"] = get_datetime_value(SQLBuilder.PROVIDER)
        return data_dict

    async def _load_relations(
        self,
        records: List[User],
        include: Optional[UserInclude] = None,
    ) -> None:
        """Load relations for records based on include dict"""
        if not include or not records:
            return

        # Load userRole relation
        inc_userRole = include.get("userRole")
        if inc_userRole:
            delegate = self._get_delegate("UserRole")
            nested_include = None
            nested_where = None
            nested_order = None
            nested_take = None
            nested_skip = None

            if isinstance(inc_userRole, dict):
                nested_include = inc_userRole.get("include")
                nested_where = inc_userRole.get("where")
                nested_order = inc_userRole.get("orderBy")
                nested_take = inc_userRole.get("take")
                nested_skip = inc_userRole.get("skip")

            # Collect FK values
            fk_values = [getattr(r, "roleId") for r in records if getattr(r, "roleId", None) is not None]
            if fk_values:
                base_where: Dict[str, Any] = {"id": {"in_": list(set(fk_values))}}
                if nested_where:
                    base_where = {"AND": [base_where, nested_where]}

                related = await delegate.find_many(where=base_where, include=nested_include)

                # Index by PK
                by_pk: Dict[Any, Any] = {}
                for rel_rec in related:
                    pk_val = getattr(rel_rec, "id")
                    by_pk[pk_val] = rel_rec

                # Assign to records
                for rec in records:
                    fk_val = getattr(rec, "roleId", None)
                    rec.userRole = by_pk.get(fk_val)

    async def find_many(
        self,
        where: Optional[UserWhereInput] = None,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None,
        include: Optional[UserInclude] = None,
        order_by: Optional[UserOrderBy] = None,
        skip: Optional[int] = None,
        take: Optional[int] = None,
        distinct: Optional[List[str]] = None,
        cursor: Optional[UserWhereUniqueInput] = None,
    ) -> List[User]:
        """Find multiple records with include support"""
        conn = await self._get_conn()

        select_dict: Optional[SelectDict] = cast(SelectDict, select) if select else None
        omit_dict: Optional[SelectDict] = cast(SelectDict, omit) if omit else None

        cols_sql, selected_fields = SQLBuilder.build_select(self.TABLE, self.FIELDS, select_dict, omit_dict)

        # Build DISTINCT clause
        distinct_sql = SQLBuilder.build_distinct(distinct)

        if distinct_sql:
            sql = f'SELECT {distinct_sql} {cols_sql} FROM "{self.TABLE}"'
        else:
            sql = f'SELECT {cols_sql} FROM "{self.TABLE}"'

        params: List[Any] = []
        param_idx = 0

        # Handle cursor-based pagination
        cursor_where: Optional[Dict[str, Any]] = None
        if cursor:
            cursor_where = dict(cursor)

        if where or cursor_where:
            combined_where = {}
            if where:
                combined_where.update(dict(where))
            if cursor_where:
                if combined_where:
                    combined_where = {"AND": [combined_where, cursor_where]}
                else:
                    combined_where = cursor_where

            where_sql, where_params, param_idx = SQLBuilder.build_where(combined_where, "", param_idx)
            if where_sql:
                sql += f" WHERE {where_sql}"
                params.extend(where_params)

        if order_by:
            sql += " " + SQLBuilder.build_order_by(dict(order_by))

        if take:
            sql += f" LIMIT {take}"
        if skip:
            sql += f" OFFSET {skip}"

        async with conn.execute(sql, params) as Cursor:
            columns = [desc[0] for desc in Cursor.description] if Cursor.description else selected_fields
            rows = await Cursor.fetchall()
            results = [self._row_to_model(row, columns) for row in rows]

        # Apply query options and load relations
        for rec in results:
            self._apply_query_options(rec, select, omit, include)

        if include:
            await self._load_relations(results, include)

        return results

    async def find_unique(
        self,
        where: UserWhereUniqueInput,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None,
        include: Optional[UserInclude] = None,
    ) -> Optional[User]:
        """Find unique record with include support"""
        conn = await self._get_conn()

        select_dict: Optional[SelectDict] = cast(SelectDict, select) if select else None
        omit_dict: Optional[SelectDict] = cast(SelectDict, omit) if omit else None

        cols_sql, selected_fields = SQLBuilder.build_select(self.TABLE, self.FIELDS, select_dict, omit_dict)
        sql = f'SELECT {cols_sql} FROM "{self.TABLE}"'

        where_sql, params, _ = SQLBuilder.build_where(dict(where))
        if where_sql:
            sql += f" WHERE {where_sql}"
        sql += " LIMIT 1"

        async with conn.execute(sql, params) as Cursor:
            columns = [desc[0] for desc in Cursor.description] if Cursor.description else selected_fields
            row = await Cursor.fetchone()

        if not row:
            return None

        result = self._row_to_model(row, columns)
        self._apply_query_options(result, select, omit, include)

        if include:
            await self._load_relations([result], include)

        return result

    async def find_unique_or_throw(
        self,
        where: UserWhereUniqueInput,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None,
        include: Optional[UserInclude] = None,
    ) -> User:
        """Find unique or raise error"""
        result = await self.find_unique(where, select, omit, include)
        if result is None:
            raise RecordNotFoundError(f"User not found: {where}")
        return result

    async def find_first(
        self,
        where: Optional[UserWhereInput] = None,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None,
        include: Optional[UserInclude] = None,
        order_by: Optional[UserOrderBy] = None,
        skip: Optional[int] = None,
        distinct: Optional[List[str]] = None,
        cursor: Optional[UserWhereUniqueInput] = None,
    ) -> Optional[User]:
        """Find first matching record"""
        results = await self.find_many(
            where=where, select=select, omit=omit, include=include,
            order_by=order_by, skip=skip, take=1, distinct=distinct, cursor=cursor
        )
        return results[0] if results else None

    async def find_first_or_throw(
        self,
        where: Optional[UserWhereInput] = None,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None,
        include: Optional[UserInclude] = None,
        order_by: Optional[UserOrderBy] = None,
        skip: Optional[int] = None,
    ) -> User:
        """Find first or raise error"""
        result = await self.find_first(where, select, omit, include, order_by, skip)
        if result is None:
            raise RecordNotFoundError(f"User not found")
        return result

    async def create(
        self,
        data: UserCreateInput,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None,
        include: Optional[UserInclude] = None,
    ) -> User:
        """Create a new record"""
        conn = await self._get_conn()

        data_dict = dict(data)
        if "id" not in data_dict:
            data_dict["id"] = generate_cuid()
        if "createdAt" not in data_dict:
            data_dict["createdAt"] = get_datetime_value(SQLBuilder.PROVIDER)
        if "updatedAt" not in data_dict:
            data_dict["updatedAt"] = get_datetime_value(SQLBuilder.PROVIDER)

        data_dict = self._prepare_create_data(data_dict)

        fields = [k for k in data_dict.keys() if k in self.FIELDS]
        values = [data_dict[k] for k in fields]
        field_names = ", ".join([f'"{f}"' for f in fields])

        placeholders = ", ".join(["?" for _ in fields])
        sql = f'INSERT INTO "{self.TABLE}" ({field_names}) VALUES ({placeholders})'
        await conn.execute(sql, values)
        await conn.commit()

        pk_value = data_dict.get(self.PK)
        result = await self.find_unique({self.PK: pk_value}, select=select, omit=omit, include=include)  # type: ignore
        if result is None:
            raise RecordNotFoundError(f"Failed to create User")
        return result

    async def create_many(
        self,
        data: List[UserCreateInput],
        skip_duplicates: bool = False,
    ) -> Dict[str, int]:
        """Create multiple records using batch insert"""
        if not data:
            return {"count": 0}

        conn = await self._get_conn()

        prepared_rows: List[Dict[str, Any]] = []
        for item in data:
            row = dict(item)
            row = self._generate_defaults(row)
            row = self._prepare_create_data(row)
            prepared_rows.append(row)

        if not prepared_rows:
            return {"count": 0}

        fields = [k for k in prepared_rows[0].keys() if k in self.FIELDS]
        field_names = ", ".join([f'"{f}"' for f in fields])

        placeholders = ", ".join(["?" for _ in fields])
        conflict = " OR IGNORE" if skip_duplicates else ""
        sql = f'INSERT{conflict} INTO "{self.TABLE}" ({field_names}) VALUES ({placeholders})'

        values_list = [tuple(row.get(f) for f in fields) for row in prepared_rows]

        try:
            await conn.executemany(sql, values_list)
            await conn.commit()
            count = len(values_list)
        except Exception as e:
            if not skip_duplicates:
                raise e
            count = 0

        return {"count": count}

    def _prepare_create_data(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data dict for insert"""
        for key in list(data_dict.keys()):
            if key not in self.FIELDS:
                del data_dict[key]

        for k, v in list(data_dict.items()):
            if isinstance(v, bool):
                if SQLBuilder.PROVIDER == "sqlite":
                    data_dict[k] = 1 if v else 0
                else:
                    data_dict[k] = v
            elif isinstance(v, datetime):
                # PostgreSQL/asyncpg expects datetime objects, SQLite expects strings
                if SQLBuilder.PROVIDER == "sqlite":
                    data_dict[k] = v.isoformat()
                # For postgresql and mysql, keep as datetime object
            elif isinstance(v, str) and k in self.DATETIME_FIELDS:
                # Convert ISO string back to datetime for PostgreSQL (naive)
                if SQLBuilder.PROVIDER != "sqlite":
                    try:
                        dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                        # asyncpg expects naive datetime for TIMESTAMP
                        data_dict[k] = dt.replace(tzinfo=None) if dt.tzinfo else dt
                    except:
                        pass
            elif isinstance(v, PyEnum):
                # Convert enum to its string value for storage
                data_dict[k] = v.value
            elif isinstance(v, dict):
                data_dict[k] = json.dumps(v)

        return data_dict

    async def update(
        self,
        where: UserWhereUniqueInput,
        data: UserUpdateInput,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None,
        include: Optional[UserInclude] = None,
    ) -> Optional[User]:
        """Update a record"""
        conn = await self._get_conn()

        existing = await self.find_unique(where)
        if not existing:
            return None

        data_dict = dict(data)
        data_dict["updatedAt"] = get_datetime_value(SQLBuilder.PROVIDER)

        for key in list(data_dict.keys()):
            if key not in self.FIELDS:
                del data_dict[key]

        for field in self.NUMERIC_FIELDS:
            if field in data_dict and isinstance(data_dict[field], dict):
                current = getattr(existing, field)
                data_dict[field] = apply_atomic_update(current, field, data_dict[field])

        for k, v in list(data_dict.items()):
            if isinstance(v, bool):
                if SQLBuilder.PROVIDER == "sqlite":
                    data_dict[k] = 1 if v else 0
                else:
                    data_dict[k] = v
            elif isinstance(v, datetime):
                if SQLBuilder.PROVIDER == "sqlite":
                    data_dict[k] = v.isoformat()
            elif isinstance(v, str) and k in self.DATETIME_FIELDS:
                if SQLBuilder.PROVIDER != "sqlite":
                    try:
                        dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                        data_dict[k] = dt.replace(tzinfo=None) if dt.tzinfo else dt
                    except:
                        pass
            elif isinstance(v, PyEnum):
                data_dict[k] = v.value
            elif isinstance(v, dict):
                data_dict[k] = json.dumps(v)

        fields = [k for k in data_dict.keys() if k in self.FIELDS and k != self.PK]
        if not fields:
            return existing

        set_clause = ", ".join([f'"{f}" = ?' for f in fields])
        values = [data_dict[f] for f in fields]

        where_sql, where_params, _ = SQLBuilder.build_where(dict(where))
        sql = f'UPDATE "{self.TABLE}" SET {set_clause} WHERE {where_sql}'

        await conn.execute(sql, values + where_params)
        await conn.commit()

        return await self.find_unique(where, select=select, omit=omit, include=include)

    async def update_many(
        self,
        where: UserWhereInput,
        data: UserUpdateInput,
    ) -> Dict[str, int]:
        """Update multiple records"""
        conn = await self._get_conn()

        data_dict = dict(data)
        data_dict["updatedAt"] = get_datetime_value(SQLBuilder.PROVIDER)

        for key in list(data_dict.keys()):
            if key not in self.FIELDS:
                del data_dict[key]

        for k, v in list(data_dict.items()):
            if isinstance(v, bool):
                data_dict[k] = 1 if v else 0
            elif isinstance(v, datetime):
                if SQLBuilder.PROVIDER == "sqlite":
                    data_dict[k] = v.isoformat()
            elif isinstance(v, str) and k in self.DATETIME_FIELDS:
                if SQLBuilder.PROVIDER != "sqlite":
                    try:
                        dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                        data_dict[k] = dt.replace(tzinfo=None) if dt.tzinfo else dt
                    except:
                        pass
            elif isinstance(v, PyEnum):
                data_dict[k] = v.value
            elif isinstance(v, dict) and k not in self.NUMERIC_FIELDS:
                data_dict[k] = json.dumps(v)

        has_atomic = any(isinstance(data_dict.get(f), dict) for f in self.NUMERIC_FIELDS)

        if has_atomic:
            records = await self.find_many(where=where)
            for rec in records:
                await self.update({self.PK: getattr(rec, self.PK)}, data)  # type: ignore
            return {"count": len(records)}

        fields = [k for k in data_dict.keys() if k in self.FIELDS and k != self.PK]

        set_clause = ", ".join([f'"{f}" = ?' for f in fields])
        values = [data_dict[f] for f in fields]

        where_sql, where_params, _ = SQLBuilder.build_where(dict(where))
        sql = f'UPDATE "{self.TABLE}" SET {set_clause}'
        if where_sql:
            sql += f" WHERE {where_sql}"

        cursor = await conn.execute(sql, values + where_params)
        count = cursor.rowcount
        await conn.commit()

        return {"count": count}

    async def delete(
        self,
        where: UserWhereUniqueInput,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None,
        include: Optional[UserInclude] = None,
    ) -> Optional[User]:
        """Delete a record"""
        conn = await self._get_conn()

        existing = await self.find_unique(where, select=select, omit=omit, include=include)
        if not existing:
            return None

        where_sql, params, _ = SQLBuilder.build_where(dict(where))
        sql = f'DELETE FROM "{self.TABLE}" WHERE {where_sql}'

        await conn.execute(sql, params)
        await conn.commit()

        return existing

    async def delete_many(
        self,
        where: Optional[UserWhereInput] = None,
    ) -> Dict[str, int]:
        """Delete multiple records"""
        conn = await self._get_conn()

        sql = f'DELETE FROM "{self.TABLE}"'
        params: List[Any] = []

        if where:
            where_sql, params, _ = SQLBuilder.build_where(dict(where))
            if where_sql:
                sql += f" WHERE {where_sql}"

        cursor = await conn.execute(sql, params)
        count = cursor.rowcount
        await conn.commit()

        return {"count": count}

    async def count(
        self,
        where: Optional[UserWhereInput] = None,
        cursor: Optional[UserWhereUniqueInput] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> int:
        """Count records"""
        conn = await self._get_conn()

        sql = f'SELECT COUNT(*) FROM "{self.TABLE}"'
        params: List[Any] = []

        if where:
            where_sql, params, _ = SQLBuilder.build_where(dict(where))
            if where_sql:
                sql += f" WHERE {where_sql}"

        async with conn.execute(sql, params) as Cursor:
            row = await Cursor.fetchone()
            return row[0] if row else 0

    async def upsert(
        self,
        where: UserWhereUniqueInput,
        create: UserCreateInput,
        update: UserUpdateInput,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None,
        include: Optional[UserInclude] = None,
    ) -> User:
        """Update or create"""
        existing = await self.find_unique(where)
        if existing:
            result = await self.update(where, update, select=select, omit=omit, include=include)
            if result is None:
                raise RecordNotFoundError(f"Failed to update User")
            return result
        return await self.create(create, select=select, omit=omit, include=include)

    async def aggregate(
        self,
        where: Optional[UserWhereInput] = None,
        _count: Optional[Union[bool, Dict[str, bool]]] = None,
        _avg: Optional[Dict[str, bool]] = None,
        _sum: Optional[Dict[str, bool]] = None,
        _min: Optional[Dict[str, bool]] = None,
        _max: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """Aggregate operations"""
        conn = await self._get_conn()
        result: Dict[str, Any] = {}

        where_sql = ""
        params: List[Any] = []
        if where:
            where_sql, params, _ = SQLBuilder.build_where(dict(where))
            where_sql = f" WHERE {where_sql}" if where_sql else ""

        if _count:
            if _count is True or (isinstance(_count, dict) and _count.get("_all")):
                async with conn.execute(f'SELECT COUNT(*) FROM "{self.TABLE}"{where_sql}', params) as cursor:
                    row = await cursor.fetchone()
                    result["_count"] = {"_all": row[0] if row else 0}
            elif isinstance(_count, dict):
                result["_count"] = {}
                for field, include in _count.items():
                    if include and field in self.FIELDS:
                        async with conn.execute(f'SELECT COUNT("{field}") FROM "{self.TABLE}"{where_sql}', params) as cursor:
                            row = await cursor.fetchone()
                            result["_count"][field] = row[0] if row else 0

        for agg_name, agg_func in [("_avg", "AVG"), ("_sum", "SUM"), ("_min", "MIN"), ("_max", "MAX")]:
            agg_dict = {"_avg": _avg, "_sum": _sum, "_min": _min, "_max": _max}[agg_name]
            if agg_dict:
                result[agg_name] = {}
                for field, include in agg_dict.items():
                    if include and field in self.FIELDS:
                        async with conn.execute(f'SELECT {agg_func}("{field}") FROM "{self.TABLE}"{where_sql}', params) as cursor:
                            row = await cursor.fetchone()
                            val = row[0] if row else None
                            result[agg_name][field] = float(val) if val and agg_name == "_avg" else val

        return result



class UserRoleDelegate:
    """Async Direct SQL delegate for UserRole"""

    TABLE = "UserRole"
    PK = "id"
    FIELDS = USERROLE_FIELDS
    NUMERIC_FIELDS = USERROLE_NUMERIC_FIELDS
    DATETIME_FIELDS = USERROLE_DATETIME_FIELDS
    ENUM_FIELDS = USERROLE_ENUM_FIELDS

    def __init__(
        self,
        get_conn: Callable[[], Awaitable[Connection]],
        get_delegate: Callable[[str], Any]
    ) -> None:
        self._get_conn = get_conn
        self._get_delegate = get_delegate

    def _row_to_model(self, row: Any, columns: List[str]) -> UserRole:
        """Convert row to model instance"""
        if isinstance(row, dict):
            data = row
        else:
            data = dict(zip(columns, row))
        # Convert datetime strings back to datetime objects



        # Convert enum string values back to enum instances
        for enum_field, enum_class in self.ENUM_FIELDS.items():
            if enum_field in data and data[enum_field] is not None:
                try:
                    data[enum_field] = enum_class(data[enum_field])
                except (ValueError, KeyError):
                    pass  # Keep original value if conversion fails
        return UserRole(**{k: v for k, v in data.items() if k in self.FIELDS})

    def _apply_query_options(
        self,
        record: UserRole,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None,
        include: Optional[UserRoleInclude] = None,
    ) -> UserRole:
        """Store query options on record for to_dict()"""
        record._stored_select = dict(select) if select else None
        record._stored_omit = dict(omit) if omit else None
        record._stored_include = dict(include) if include else None
        return record

    def _generate_defaults(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default values for ID and timestamp fields"""
        return data_dict

    async def _load_relations(
        self,
        records: List[UserRole],
        include: Optional[UserRoleInclude] = None,
    ) -> None:
        """Load relations for records based on include dict"""
        if not include or not records:
            return

        # Load user relation
        inc_user = include.get("user")
        if inc_user:
            delegate = self._get_delegate("User")
            nested_include = None
            nested_where = None
            nested_order = None
            nested_take = None
            nested_skip = None

            if isinstance(inc_user, dict):
                nested_include = inc_user.get("include")
                nested_where = inc_user.get("where")
                nested_order = inc_user.get("orderBy")
                nested_take = inc_user.get("take")
                nested_skip = inc_user.get("skip")

            # Collect PKs from records
            pk_values = [getattr(r, self.PK) for r in records if getattr(r, self.PK) is not None]
            if pk_values:
                base_where: Dict[str, Any] = {"roleId": {"in_": pk_values}}
                if nested_where:
                    base_where = {"AND": [base_where, nested_where]}

                related = await delegate.find_many(
                    where=base_where,
                    include=nested_include,
                    order_by=nested_order,
                    take=nested_take,
                    skip=nested_skip,
                )

                # Group by FK
                by_fk: Dict[Any, List[Any]] = {}
                for rel_rec in related:
                    fk_val = getattr(rel_rec, "roleId", None)
                    if fk_val not in by_fk:
                        by_fk[fk_val] = []
                    by_fk[fk_val].append(rel_rec)

                # Assign to records
                for rec in records:
                    pk_val = getattr(rec, self.PK)
                    rec.user = by_fk.get(pk_val, [])

    async def find_many(
        self,
        where: Optional[UserRoleWhereInput] = None,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None,
        include: Optional[UserRoleInclude] = None,
        order_by: Optional[UserRoleOrderBy] = None,
        skip: Optional[int] = None,
        take: Optional[int] = None,
        distinct: Optional[List[str]] = None,
        cursor: Optional[UserRoleWhereUniqueInput] = None,
    ) -> List[UserRole]:
        """Find multiple records with include support"""
        conn = await self._get_conn()

        select_dict: Optional[SelectDict] = cast(SelectDict, select) if select else None
        omit_dict: Optional[SelectDict] = cast(SelectDict, omit) if omit else None

        cols_sql, selected_fields = SQLBuilder.build_select(self.TABLE, self.FIELDS, select_dict, omit_dict)

        # Build DISTINCT clause
        distinct_sql = SQLBuilder.build_distinct(distinct)

        if distinct_sql:
            sql = f'SELECT {distinct_sql} {cols_sql} FROM "{self.TABLE}"'
        else:
            sql = f'SELECT {cols_sql} FROM "{self.TABLE}"'

        params: List[Any] = []
        param_idx = 0

        # Handle cursor-based pagination
        cursor_where: Optional[Dict[str, Any]] = None
        if cursor:
            cursor_where = dict(cursor)

        if where or cursor_where:
            combined_where = {}
            if where:
                combined_where.update(dict(where))
            if cursor_where:
                if combined_where:
                    combined_where = {"AND": [combined_where, cursor_where]}
                else:
                    combined_where = cursor_where

            where_sql, where_params, param_idx = SQLBuilder.build_where(combined_where, "", param_idx)
            if where_sql:
                sql += f" WHERE {where_sql}"
                params.extend(where_params)

        if order_by:
            sql += " " + SQLBuilder.build_order_by(dict(order_by))

        if take:
            sql += f" LIMIT {take}"
        if skip:
            sql += f" OFFSET {skip}"

        async with conn.execute(sql, params) as Cursor:
            columns = [desc[0] for desc in Cursor.description] if Cursor.description else selected_fields
            rows = await Cursor.fetchall()
            results = [self._row_to_model(row, columns) for row in rows]

        # Apply query options and load relations
        for rec in results:
            self._apply_query_options(rec, select, omit, include)

        if include:
            await self._load_relations(results, include)

        return results

    async def find_unique(
        self,
        where: UserRoleWhereUniqueInput,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None,
        include: Optional[UserRoleInclude] = None,
    ) -> Optional[UserRole]:
        """Find unique record with include support"""
        conn = await self._get_conn()

        select_dict: Optional[SelectDict] = cast(SelectDict, select) if select else None
        omit_dict: Optional[SelectDict] = cast(SelectDict, omit) if omit else None

        cols_sql, selected_fields = SQLBuilder.build_select(self.TABLE, self.FIELDS, select_dict, omit_dict)
        sql = f'SELECT {cols_sql} FROM "{self.TABLE}"'

        where_sql, params, _ = SQLBuilder.build_where(dict(where))
        if where_sql:
            sql += f" WHERE {where_sql}"
        sql += " LIMIT 1"

        async with conn.execute(sql, params) as Cursor:
            columns = [desc[0] for desc in Cursor.description] if Cursor.description else selected_fields
            row = await Cursor.fetchone()

        if not row:
            return None

        result = self._row_to_model(row, columns)
        self._apply_query_options(result, select, omit, include)

        if include:
            await self._load_relations([result], include)

        return result

    async def find_unique_or_throw(
        self,
        where: UserRoleWhereUniqueInput,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None,
        include: Optional[UserRoleInclude] = None,
    ) -> UserRole:
        """Find unique or raise error"""
        result = await self.find_unique(where, select, omit, include)
        if result is None:
            raise RecordNotFoundError(f"UserRole not found: {where}")
        return result

    async def find_first(
        self,
        where: Optional[UserRoleWhereInput] = None,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None,
        include: Optional[UserRoleInclude] = None,
        order_by: Optional[UserRoleOrderBy] = None,
        skip: Optional[int] = None,
        distinct: Optional[List[str]] = None,
        cursor: Optional[UserRoleWhereUniqueInput] = None,
    ) -> Optional[UserRole]:
        """Find first matching record"""
        results = await self.find_many(
            where=where, select=select, omit=omit, include=include,
            order_by=order_by, skip=skip, take=1, distinct=distinct, cursor=cursor
        )
        return results[0] if results else None

    async def find_first_or_throw(
        self,
        where: Optional[UserRoleWhereInput] = None,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None,
        include: Optional[UserRoleInclude] = None,
        order_by: Optional[UserRoleOrderBy] = None,
        skip: Optional[int] = None,
    ) -> UserRole:
        """Find first or raise error"""
        result = await self.find_first(where, select, omit, include, order_by, skip)
        if result is None:
            raise RecordNotFoundError(f"UserRole not found")
        return result

    async def create(
        self,
        data: UserRoleCreateInput,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None,
        include: Optional[UserRoleInclude] = None,
    ) -> UserRole:
        """Create a new record"""
        conn = await self._get_conn()

        data_dict = dict(data)

        data_dict = self._prepare_create_data(data_dict)

        fields = [k for k in data_dict.keys() if k in self.FIELDS]
        values = [data_dict[k] for k in fields]
        field_names = ", ".join([f'"{f}"' for f in fields])

        placeholders = ", ".join(["?" for _ in fields])
        sql = f'INSERT INTO "{self.TABLE}" ({field_names}) VALUES ({placeholders})'
        await conn.execute(sql, values)
        await conn.commit()

        pk_value = data_dict.get(self.PK)
        result = await self.find_unique({self.PK: pk_value}, select=select, omit=omit, include=include)  # type: ignore
        if result is None:
            raise RecordNotFoundError(f"Failed to create UserRole")
        return result

    async def create_many(
        self,
        data: List[UserRoleCreateInput],
        skip_duplicates: bool = False,
    ) -> Dict[str, int]:
        """Create multiple records using batch insert"""
        if not data:
            return {"count": 0}

        conn = await self._get_conn()

        prepared_rows: List[Dict[str, Any]] = []
        for item in data:
            row = dict(item)
            row = self._generate_defaults(row)
            row = self._prepare_create_data(row)
            prepared_rows.append(row)

        if not prepared_rows:
            return {"count": 0}

        fields = [k for k in prepared_rows[0].keys() if k in self.FIELDS]
        field_names = ", ".join([f'"{f}"' for f in fields])

        placeholders = ", ".join(["?" for _ in fields])
        conflict = " OR IGNORE" if skip_duplicates else ""
        sql = f'INSERT{conflict} INTO "{self.TABLE}" ({field_names}) VALUES ({placeholders})'

        values_list = [tuple(row.get(f) for f in fields) for row in prepared_rows]

        try:
            await conn.executemany(sql, values_list)
            await conn.commit()
            count = len(values_list)
        except Exception as e:
            if not skip_duplicates:
                raise e
            count = 0

        return {"count": count}

    def _prepare_create_data(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data dict for insert"""
        for key in list(data_dict.keys()):
            if key not in self.FIELDS:
                del data_dict[key]

        for k, v in list(data_dict.items()):
            if isinstance(v, bool):
                if SQLBuilder.PROVIDER == "sqlite":
                    data_dict[k] = 1 if v else 0
                else:
                    data_dict[k] = v
            elif isinstance(v, datetime):
                # PostgreSQL/asyncpg expects datetime objects, SQLite expects strings
                if SQLBuilder.PROVIDER == "sqlite":
                    data_dict[k] = v.isoformat()
                # For postgresql and mysql, keep as datetime object
            elif isinstance(v, str) and k in self.DATETIME_FIELDS:
                # Convert ISO string back to datetime for PostgreSQL (naive)
                if SQLBuilder.PROVIDER != "sqlite":
                    try:
                        dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                        # asyncpg expects naive datetime for TIMESTAMP
                        data_dict[k] = dt.replace(tzinfo=None) if dt.tzinfo else dt
                    except:
                        pass
            elif isinstance(v, PyEnum):
                # Convert enum to its string value for storage
                data_dict[k] = v.value
            elif isinstance(v, dict):
                data_dict[k] = json.dumps(v)

        return data_dict

    async def update(
        self,
        where: UserRoleWhereUniqueInput,
        data: UserRoleUpdateInput,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None,
        include: Optional[UserRoleInclude] = None,
    ) -> Optional[UserRole]:
        """Update a record"""
        conn = await self._get_conn()

        existing = await self.find_unique(where)
        if not existing:
            return None

        data_dict = dict(data)

        for key in list(data_dict.keys()):
            if key not in self.FIELDS:
                del data_dict[key]

        for field in self.NUMERIC_FIELDS:
            if field in data_dict and isinstance(data_dict[field], dict):
                current = getattr(existing, field)
                data_dict[field] = apply_atomic_update(current, field, data_dict[field])

        for k, v in list(data_dict.items()):
            if isinstance(v, bool):
                if SQLBuilder.PROVIDER == "sqlite":
                    data_dict[k] = 1 if v else 0
                else:
                    data_dict[k] = v
            elif isinstance(v, datetime):
                if SQLBuilder.PROVIDER == "sqlite":
                    data_dict[k] = v.isoformat()
            elif isinstance(v, str) and k in self.DATETIME_FIELDS:
                if SQLBuilder.PROVIDER != "sqlite":
                    try:
                        dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                        data_dict[k] = dt.replace(tzinfo=None) if dt.tzinfo else dt
                    except:
                        pass
            elif isinstance(v, PyEnum):
                data_dict[k] = v.value
            elif isinstance(v, dict):
                data_dict[k] = json.dumps(v)

        fields = [k for k in data_dict.keys() if k in self.FIELDS and k != self.PK]
        if not fields:
            return existing

        set_clause = ", ".join([f'"{f}" = ?' for f in fields])
        values = [data_dict[f] for f in fields]

        where_sql, where_params, _ = SQLBuilder.build_where(dict(where))
        sql = f'UPDATE "{self.TABLE}" SET {set_clause} WHERE {where_sql}'

        await conn.execute(sql, values + where_params)
        await conn.commit()

        return await self.find_unique(where, select=select, omit=omit, include=include)

    async def update_many(
        self,
        where: UserRoleWhereInput,
        data: UserRoleUpdateInput,
    ) -> Dict[str, int]:
        """Update multiple records"""
        conn = await self._get_conn()

        data_dict = dict(data)

        for key in list(data_dict.keys()):
            if key not in self.FIELDS:
                del data_dict[key]

        for k, v in list(data_dict.items()):
            if isinstance(v, bool):
                data_dict[k] = 1 if v else 0
            elif isinstance(v, datetime):
                if SQLBuilder.PROVIDER == "sqlite":
                    data_dict[k] = v.isoformat()
            elif isinstance(v, str) and k in self.DATETIME_FIELDS:
                if SQLBuilder.PROVIDER != "sqlite":
                    try:
                        dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                        data_dict[k] = dt.replace(tzinfo=None) if dt.tzinfo else dt
                    except:
                        pass
            elif isinstance(v, PyEnum):
                data_dict[k] = v.value
            elif isinstance(v, dict) and k not in self.NUMERIC_FIELDS:
                data_dict[k] = json.dumps(v)

        has_atomic = any(isinstance(data_dict.get(f), dict) for f in self.NUMERIC_FIELDS)

        if has_atomic:
            records = await self.find_many(where=where)
            for rec in records:
                await self.update({self.PK: getattr(rec, self.PK)}, data)  # type: ignore
            return {"count": len(records)}

        fields = [k for k in data_dict.keys() if k in self.FIELDS and k != self.PK]

        set_clause = ", ".join([f'"{f}" = ?' for f in fields])
        values = [data_dict[f] for f in fields]

        where_sql, where_params, _ = SQLBuilder.build_where(dict(where))
        sql = f'UPDATE "{self.TABLE}" SET {set_clause}'
        if where_sql:
            sql += f" WHERE {where_sql}"

        cursor = await conn.execute(sql, values + where_params)
        count = cursor.rowcount
        await conn.commit()

        return {"count": count}

    async def delete(
        self,
        where: UserRoleWhereUniqueInput,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None,
        include: Optional[UserRoleInclude] = None,
    ) -> Optional[UserRole]:
        """Delete a record"""
        conn = await self._get_conn()

        existing = await self.find_unique(where, select=select, omit=omit, include=include)
        if not existing:
            return None

        where_sql, params, _ = SQLBuilder.build_where(dict(where))
        sql = f'DELETE FROM "{self.TABLE}" WHERE {where_sql}'

        await conn.execute(sql, params)
        await conn.commit()

        return existing

    async def delete_many(
        self,
        where: Optional[UserRoleWhereInput] = None,
    ) -> Dict[str, int]:
        """Delete multiple records"""
        conn = await self._get_conn()

        sql = f'DELETE FROM "{self.TABLE}"'
        params: List[Any] = []

        if where:
            where_sql, params, _ = SQLBuilder.build_where(dict(where))
            if where_sql:
                sql += f" WHERE {where_sql}"

        cursor = await conn.execute(sql, params)
        count = cursor.rowcount
        await conn.commit()

        return {"count": count}

    async def count(
        self,
        where: Optional[UserRoleWhereInput] = None,
        cursor: Optional[UserRoleWhereUniqueInput] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> int:
        """Count records"""
        conn = await self._get_conn()

        sql = f'SELECT COUNT(*) FROM "{self.TABLE}"'
        params: List[Any] = []

        if where:
            where_sql, params, _ = SQLBuilder.build_where(dict(where))
            if where_sql:
                sql += f" WHERE {where_sql}"

        async with conn.execute(sql, params) as Cursor:
            row = await Cursor.fetchone()
            return row[0] if row else 0

    async def upsert(
        self,
        where: UserRoleWhereUniqueInput,
        create: UserRoleCreateInput,
        update: UserRoleUpdateInput,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None,
        include: Optional[UserRoleInclude] = None,
    ) -> UserRole:
        """Update or create"""
        existing = await self.find_unique(where)
        if existing:
            result = await self.update(where, update, select=select, omit=omit, include=include)
            if result is None:
                raise RecordNotFoundError(f"Failed to update UserRole")
            return result
        return await self.create(create, select=select, omit=omit, include=include)

    async def aggregate(
        self,
        where: Optional[UserRoleWhereInput] = None,
        _count: Optional[Union[bool, Dict[str, bool]]] = None,
        _avg: Optional[Dict[str, bool]] = None,
        _sum: Optional[Dict[str, bool]] = None,
        _min: Optional[Dict[str, bool]] = None,
        _max: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """Aggregate operations"""
        conn = await self._get_conn()
        result: Dict[str, Any] = {}

        where_sql = ""
        params: List[Any] = []
        if where:
            where_sql, params, _ = SQLBuilder.build_where(dict(where))
            where_sql = f" WHERE {where_sql}" if where_sql else ""

        if _count:
            if _count is True or (isinstance(_count, dict) and _count.get("_all")):
                async with conn.execute(f'SELECT COUNT(*) FROM "{self.TABLE}"{where_sql}', params) as cursor:
                    row = await cursor.fetchone()
                    result["_count"] = {"_all": row[0] if row else 0}
            elif isinstance(_count, dict):
                result["_count"] = {}
                for field, include in _count.items():
                    if include and field in self.FIELDS:
                        async with conn.execute(f'SELECT COUNT("{field}") FROM "{self.TABLE}"{where_sql}', params) as cursor:
                            row = await cursor.fetchone()
                            result["_count"][field] = row[0] if row else 0

        for agg_name, agg_func in [("_avg", "AVG"), ("_sum", "SUM"), ("_min", "MIN"), ("_max", "MAX")]:
            agg_dict = {"_avg": _avg, "_sum": _sum, "_min": _min, "_max": _max}[agg_name]
            if agg_dict:
                result[agg_name] = {}
                for field, include in agg_dict.items():
                    if include and field in self.FIELDS:
                        async with conn.execute(f'SELECT {agg_func}("{field}") FROM "{self.TABLE}"{where_sql}', params) as cursor:
                            row = await cursor.fetchone()
                            val = row[0] if row else None
                            result[agg_name][field] = float(val) if val and agg_name == "_avg" else val

        return result



class PrismaClient:
    """Async Direct SQL Prisma-style client for FastAPI"""

    def __init__(self, pool_size: int = 5, use_pool: bool = True) -> None:
        self._conn: Optional[Connection] = None
        self._pool: Optional[AsyncConnectionPool] = None
        self._pool_size = pool_size
        self._use_pool = use_pool
        self._in_transaction: bool = False
        self._delegates: Dict[str, Any] = {}
        self._stmt_cache = PreparedStatementCache()
        self._connected = False
        self._task_conn: contextvars.ContextVar[Optional[Connection]] = contextvars.ContextVar(
            "prisma_task_conn", default=None
        )
        self._task_conn_task_id: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
            "prisma_task_conn_task_id", default=None
        )
        self._user: Optional[UserDelegate] = None
        self._userrole: Optional[UserRoleDelegate] = None

    async def _get_connection(self) -> Connection:
        if not self._connected:
            await self.connect()

        if not self._use_pool:
            if self._conn is None:
                self._conn = await self._create_connection()
            return self._conn

        task = asyncio.current_task()
        task_id = id(task) if task else None

        cached = self._task_conn.get()
        cached_task_id = self._task_conn_task_id.get()

        if cached is not None and cached_task_id == task_id:
            return cached

        assert self._pool is not None
        conn = await self._pool.get()
        self._task_conn.set(conn)
        self._task_conn_task_id.set(task_id)

        if task is not None:
            def _release(_t: asyncio.Task, _conn: Connection = conn) -> None:
                if self._pool is not None:
                    asyncio.create_task(self._pool.put(_conn))
                self._task_conn.set(None)
                self._task_conn_task_id.set(None)

            task.add_done_callback(_release)

        return conn

    async def _release_connection(self, conn: Connection) -> None:
        """Return connection to pool"""
        if self._use_pool and self._pool and not self._in_transaction:
            await self._pool.put(conn)

    async def _create_connection(self) -> Connection:
        """Create a new database connection"""
        database_url = os.getenv("DATABASE_URL", "file:./prisma/dev.db")
        db_path = database_url.replace("file:", "")
        project_root = Path(__file__).parent.parent.parent.parent
        db_full_path = (project_root / db_path).resolve()
        conn = await aiosqlite.connect(str(db_full_path))
        return conn

    def _get_delegate(self, model_name: str) -> Any:
        """Get delegate by model name for relation loading"""
        if model_name not in self._delegates:
            prop_name = model_name.lower()
            if hasattr(self, prop_name):
                getattr(self, prop_name)
        return self._delegates.get(model_name)

    async def connect(self) -> "PrismaClient":
        """Initialize database connection or pool"""
        if self._connected:
            return self

        if self._use_pool:
            if self._pool is None:
                self._pool = AsyncConnectionPool(self._create_connection, self._pool_size)
        else:
            await self._get_connection()

        self._connected = True
        return self

    async def disconnect(self) -> None:
        """Disconnect from database and close pool"""
        if self._pool:
            await self._pool.close_all()
            self._pool = None
        if self._conn:
            await self._conn.close()
            self._conn = None
        self._stmt_cache.clear()
        self._connected = False

    @property
    def user(self) -> UserDelegate:
        if not self._user:
            self._user = UserDelegate(self._get_connection, self._get_delegate)
            self._delegates["User"] = self._user
        return self._user

    @property
    def userrole(self) -> UserRoleDelegate:
        if not self._userrole:
            self._userrole = UserRoleDelegate(self._get_connection, self._get_delegate)
            self._delegates["UserRole"] = self._userrole
        return self._userrole

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator["PrismaClient", None]:
        """Execute in transaction"""
        conn = await self._get_connection()
        self._in_transaction = True
        try:
            yield self
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            self._in_transaction = False

    async def query_raw(self, query: str, *args: Any) -> List[Dict[str, Any]]:
        """Execute raw SQL query"""
        conn = await self._get_connection()
        async with conn.execute(query, args if args else ()) as cursor:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = await cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    async def execute_raw(self, query: str, *args: Any) -> int:
        """Execute raw SQL command"""
        conn = await self._get_connection()
        cursor = await conn.execute(query, args if args else ())
        count = cursor.rowcount
        await conn.commit()
        return count

    async def __aenter__(self) -> "PrismaClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.disconnect()

    async def batch(self, operations: List[Callable[[], Awaitable[Any]]]) -> List[Any]:
        """Execute multiple operations in a single transaction"""
        results: List[Any] = []
        async with self.transaction():
            for op in operations:
                results.append(await op())
        return results


prisma = PrismaClient(use_pool=True)
