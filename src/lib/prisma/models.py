"""Auto-generated from Prisma schema - Async Direct SQL without ORM layer"""
import uuid
import json
from enum import Enum as PyEnum
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, TypedDict, Union, Literal, Tuple, Set
from dataclasses import dataclass, field, asdict

try:
    from cuid2 import cuid_wrapper
    _cuid_generator = cuid_wrapper()
    HAS_CUID2 = True
except ImportError:
    _cuid_generator = None
    HAS_CUID2 = False

try:
    from nanoid import generate as nanoid_generate  # type: ignore[import-untyped]
    HAS_NANOID = True
except ImportError:
    nanoid_generate = None
    HAS_NANOID = False

try:
    from ulid import ULID  # type: ignore[import]
    HAS_ULID = True
except ImportError:
    ULID = None
    HAS_ULID = False


def generate_cuid() -> str:
    if HAS_CUID2 and _cuid_generator:
        return _cuid_generator()
    return str(uuid.uuid4())


def generate_uuid() -> str:
    return str(uuid.uuid4())


def generate_nanoid() -> str:
    if HAS_NANOID and nanoid_generate:
        return nanoid_generate()
    return str(uuid.uuid4())


def generate_ulid() -> str:
    if HAS_ULID and ULID:
        return str(ULID())
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_str() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_datetime_value(provider: str) -> Union[str, datetime]:
    """Return UTC now in the correct format for the database provider"""
    now = datetime.now(timezone.utc)
    if provider == "sqlite":
        return now.isoformat()
    # PostgreSQL TIMESTAMP expects naive datetime, TIMESTAMPTZ expects aware
    # asyncpg requires naive datetime for TIMESTAMP columns
    return now.replace(tzinfo=None)


# Type alias for select/omit dicts
SelectDict = Dict[str, bool]
OrderByDict = Dict[str, Any]
IncludeDict = Dict[str, Union[bool, Dict[str, Any]]]


# Atomic operation types
class IntFieldUpdateOperations(TypedDict, total=False):
    set: int
    increment: int
    decrement: int
    multiply: int
    divide: int


class FloatFieldUpdateOperations(TypedDict, total=False):
    set: float
    increment: float
    decrement: float
    multiply: float
    divide: float


class StringFilter(TypedDict, total=False):
    equals: str
    not_: str
    in_: List[str]
    notIn: List[str]
    lt: str
    lte: str
    gt: str
    gte: str
    contains: str
    startsWith: str
    endsWith: str
    mode: Literal["default", "insensitive"]


class IntFilter(TypedDict, total=False):
    equals: int
    not_: int
    in_: List[int]
    notIn: List[int]
    lt: int
    lte: int
    gt: int
    gte: int


class FloatFilter(TypedDict, total=False):
    equals: float
    not_: float
    in_: List[float]
    notIn: List[float]
    lt: float
    lte: float
    gt: float
    gte: float


class BoolFilter(TypedDict, total=False):
    equals: bool
    not_: bool


class DateTimeFilter(TypedDict, total=False):
    equals: datetime
    not_: datetime
    in_: List[datetime]
    notIn: List[datetime]
    lt: datetime
    lte: datetime
    gt: datetime
    gte: datetime


class UserWhereInput(TypedDict, total=False):
    id: Union[str, Dict[str, Any]]
    name: Union[str, Dict[str, Any]]
    email: Union[str, Dict[str, Any]]
    password: Union[str, Dict[str, Any]]
    emailVerified: Union[datetime, Dict[str, Any]]
    image: Union[str, Dict[str, Any]]
    createdAt: Union[datetime, Dict[str, Any]]
    updatedAt: Union[datetime, Dict[str, Any]]
    roleId: Union[int, Dict[str, Any]]
    AND: List["UserWhereInput"]
    OR: List["UserWhereInput"]
    NOT: "UserWhereInput"


class UserWhereUniqueInput(TypedDict, total=False):
    id: str
    email: str


class UserSelect(TypedDict, total=False):
    id: bool
    name: bool
    email: bool
    password: bool
    emailVerified: bool
    image: bool
    createdAt: bool
    updatedAt: bool
    roleId: bool
    userRole: Union[bool, Dict[str, Any]]


class UserOmit(TypedDict, total=False):
    id: bool
    name: bool
    email: bool
    password: bool
    emailVerified: bool
    image: bool
    createdAt: bool
    updatedAt: bool
    roleId: bool


class UserInclude(TypedDict, total=False):
    userRole: Union[bool, Dict[str, Any]]
    _count: Union[bool, Dict[str, bool]]


class UserOrderBy(TypedDict, total=False):
    id: Union[Literal["asc", "desc"], Dict[str, str]]
    name: Union[Literal["asc", "desc"], Dict[str, str]]
    email: Union[Literal["asc", "desc"], Dict[str, str]]
    password: Union[Literal["asc", "desc"], Dict[str, str]]
    emailVerified: Union[Literal["asc", "desc"], Dict[str, str]]
    image: Union[Literal["asc", "desc"], Dict[str, str]]
    createdAt: Union[Literal["asc", "desc"], Dict[str, str]]
    updatedAt: Union[Literal["asc", "desc"], Dict[str, str]]
    roleId: Union[Literal["asc", "desc"], Dict[str, str]]


class UserCreateInput(TypedDict, total=False):
    id: str
    name: str
    email: str
    password: str
    emailVerified: datetime
    image: str
    createdAt: datetime
    updatedAt: datetime
    roleId: int
    userRole: Dict[str, Any]  # Nested create/connect


class UserUpdateInput(TypedDict, total=False):
    name: Optional[str]
    email: Optional[str]
    password: Optional[str]
    emailVerified: Optional[datetime]
    image: Optional[str]
    createdAt: datetime
    updatedAt: datetime
    roleId: Union[int, IntFieldUpdateOperations, None]
    userRole: Dict[str, Any]  # Nested update/connect/disconnect


@dataclass
class User:
    """User model instance"""
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    emailVerified: Optional[datetime] = None
    image: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    roleId: Optional[int] = None
    userRole: Optional["UserRole"] = None

    # Query options stored from find methods
    _stored_select: Optional[Dict[str, Any]] = field(default=None, repr=False)
    _stored_omit: Optional[Dict[str, Any]] = field(default=None, repr=False)
    _stored_include: Optional[Dict[str, Any]] = field(default=None, repr=False)

    def to_dict(
        self,
        include: Optional[UserInclude] = None,
        select: Optional[UserSelect] = None,
        omit: Optional[UserOmit] = None
    ) -> Dict[str, Any]:
        """Convert to dictionary with select/omit/include support"""
        # Use stored options as fallback
        if include is None:
            include = self._stored_include  # type: ignore
        if select is None:
            select = self._stored_select  # type: ignore
        if omit is None:
            omit = self._stored_omit  # type: ignore

        data: Dict[str, Any] = {}
        scalar_fields = ["id", "name", "email", "password", "emailVerified", "image", "createdAt", "updatedAt", "roleId"]

        # Determine which scalar fields to include
        fields_to_include: Set[str] = set()

        if select:
            # Only include explicitly selected scalar fields
            for key in scalar_fields:
                if select.get(key, False):
                    fields_to_include.add(key)
        elif omit:
            # Include all except omitted fields
            for key in scalar_fields:
                if not omit.get(key, False):
                    fields_to_include.add(key)
        else:
            # Include all scalar fields by default
            fields_to_include = set(scalar_fields)

        # Build data dict with only included fields
        for key in fields_to_include:
            val = getattr(self, key)
            if isinstance(val, datetime):
                data[key] = val.isoformat()
            elif isinstance(val, PyEnum):
                data[key] = val.value
            else:
                data[key] = val

        # Handle include for relations
        if include:
            inc_val = include.get("userRole")
            if inc_val:
                nested_opts: Dict[str, Any] = {}
                if isinstance(inc_val, dict):
                    nested_opts = inc_val
                data["userRole"] = (
                    self.userRole.to_dict(
                        include=nested_opts.get("include"),
                        select=nested_opts.get("select"),
                        omit=nested_opts.get("omit")
                    ) if self.userRole else None
                )
            else:  # inc_val is True
                data["userRole"] = self.userRole.to_dict() if self.userRole else None

        # Handle select for relations (when select specifies relation)
        if select:
            sel_val = select.get("userRole")
            if sel_val and "userRole" not in data:
                if isinstance(sel_val, dict):
                    nested_select = sel_val.get("select")
                    data["userRole"] = (
                        self.userRole.to_dict(select=nested_select) if self.userRole else None
                    )
                else:  # sel_val is True
                    data["userRole"] = self.userRole.to_dict() if self.userRole else None

        return data


class UserRoleWhereInput(TypedDict, total=False):
    id: Union[int, Dict[str, Any]]
    name: Union[str, Dict[str, Any]]
    AND: List["UserRoleWhereInput"]
    OR: List["UserRoleWhereInput"]
    NOT: "UserRoleWhereInput"


class UserRoleWhereUniqueInput(TypedDict, total=False):
    id: int
    name: str


class UserRoleSelect(TypedDict, total=False):
    id: bool
    name: bool
    user: Union[bool, Dict[str, Any]]


class UserRoleOmit(TypedDict, total=False):
    id: bool
    name: bool


class UserRoleInclude(TypedDict, total=False):
    user: Union[bool, Dict[str, Any]]
    _count: Union[bool, Dict[str, bool]]


class UserRoleOrderBy(TypedDict, total=False):
    id: Union[Literal["asc", "desc"], Dict[str, str]]
    name: Union[Literal["asc", "desc"], Dict[str, str]]


class UserRoleCreateInput(TypedDict, total=False):
    id: int
    name: str
    user: Dict[str, Any]  # Nested create/connect


class UserRoleUpdateInput(TypedDict, total=False):
    name: str
    user: Dict[str, Any]  # Nested update/connect/disconnect


@dataclass
class UserRole:
    """UserRole model instance"""
    id: Optional[int] = None
    name: Optional[str] = None
    user: List["User"] = field(default_factory=list)

    # Query options stored from find methods
    _stored_select: Optional[Dict[str, Any]] = field(default=None, repr=False)
    _stored_omit: Optional[Dict[str, Any]] = field(default=None, repr=False)
    _stored_include: Optional[Dict[str, Any]] = field(default=None, repr=False)

    def to_dict(
        self,
        include: Optional[UserRoleInclude] = None,
        select: Optional[UserRoleSelect] = None,
        omit: Optional[UserRoleOmit] = None
    ) -> Dict[str, Any]:
        """Convert to dictionary with select/omit/include support"""
        # Use stored options as fallback
        if include is None:
            include = self._stored_include  # type: ignore
        if select is None:
            select = self._stored_select  # type: ignore
        if omit is None:
            omit = self._stored_omit  # type: ignore

        data: Dict[str, Any] = {}
        scalar_fields = ["id", "name"]

        # Determine which scalar fields to include
        fields_to_include: Set[str] = set()

        if select:
            # Only include explicitly selected scalar fields
            for key in scalar_fields:
                if select.get(key, False):
                    fields_to_include.add(key)
        elif omit:
            # Include all except omitted fields
            for key in scalar_fields:
                if not omit.get(key, False):
                    fields_to_include.add(key)
        else:
            # Include all scalar fields by default
            fields_to_include = set(scalar_fields)

        # Build data dict with only included fields
        for key in fields_to_include:
            val = getattr(self, key)
            if isinstance(val, datetime):
                data[key] = val.isoformat()
            elif isinstance(val, PyEnum):
                data[key] = val.value
            else:
                data[key] = val

        # Handle include for relations
        if include:
            inc_val = include.get("user")
            if inc_val:
                nested_opts: Dict[str, Any] = {}
                if isinstance(inc_val, dict):
                    nested_opts = inc_val
                data["user"] = [
                    item.to_dict(
                        include=nested_opts.get("include"),
                        select=nested_opts.get("select"),
                        omit=nested_opts.get("omit")
                    ) for item in self.user
                ]
            else:  # inc_val is True
                data["user"] = [item.to_dict() for item in self.user]

        # Handle select for relations (when select specifies relation)
        if select:
            sel_val = select.get("user")
            if sel_val and "user" not in data:
                if isinstance(sel_val, dict):
                    nested_select = sel_val.get("select")
                    data["user"] = [
                        item.to_dict(select=nested_select) for item in self.user
                    ]
                else:  # sel_val is True
                    data["user"] = [item.to_dict() for item in self.user]

        return data


