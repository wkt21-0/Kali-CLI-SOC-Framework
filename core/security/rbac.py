"""
Minimal RBAC manager used by tests and CLI checks.
Loads config/rbac.yaml and exposes simple checks.
"""
from pathlib import Path
import yaml

RBAC_FILE = Path("config/rbac.yaml")


class RBACManager:
    _roles = {}

    @classmethod
    def load_roles(cls, path: Path = RBAC_FILE):
        if not path.exists():
            cls._roles = {}
            return cls._roles
        data = yaml.safe_load(path.read_text()) or {}
        cls._roles = data.get("roles", {})
        return cls._roles

    @classmethod
    def check(cls, role: str, permission: str) -> bool:
        if not cls._roles:
            cls.load_roles()
        role_obj = cls._roles.get(role)
        if not role_obj:
            return False
        allowed = role_obj.get("allowed", [])
        if "all" in allowed:
            return True
        return permission in allowed
