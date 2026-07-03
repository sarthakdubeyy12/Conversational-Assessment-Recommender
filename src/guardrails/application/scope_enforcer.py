"""Scope enforcement logic."""


class ScopeEnforcer:
    """Enforces agent stays in scope."""
    
    def is_in_scope(self, user_message: str) -> bool:
        pass
    
    def get_out_of_scope_topics(self) -> list:
        pass
