from typing import Optional

import streamlit as st
from streamlit_cookies_controller import CookieController
from supabase_auth._sync.storage import SyncMemoryStorage, SyncSupportedStorage


class PkceCookieStorage(SyncSupportedStorage):
    def __init__(self) -> None:
        self.memory_fallback = SyncMemoryStorage()
        try:
            if "pkce_cookie_controller" not in st.session_state:
                st.session_state["pkce_cookie_controller"] = {}
            self.controller = CookieController(key="pkce_cookie_controller")
        except Exception:
            self.controller = None

    def _is_pkce_key(self, key: str) -> bool:
        return "code-verifier" in key or key.startswith("sb-pkce")

    def get_item(self, key: str) -> Optional[str]:
        if not self._is_pkce_key(key):
            return self.memory_fallback.get_item(key)
        if not self.controller:
            return self.memory_fallback.get_item(key)
        try:
            val = self.controller.getAll().get(key) or self.controller.get(key)
            if val is not None:
                return str(val)
            return self.memory_fallback.get_item(key)
        except Exception:
            return self.memory_fallback.get_item(key)

    def set_item(self, key: str, value: str) -> None:
        if not self._is_pkce_key(key):
            self.memory_fallback.set_item(key, value)
            return
        self.memory_fallback.set_item(key, value)
        if self.controller:
            try:
                self.controller.set(
                    key,
                    value,
                    path="/",
                    same_site="lax",
                    secure=True,
                    max_age=604800,
                )
            except Exception:
                pass

    def remove_item(self, key: str) -> None:
        if not self._is_pkce_key(key):
            self.memory_fallback.remove_item(key)
            return
        self.memory_fallback.remove_item(key)
        if self.controller:
            try:
                self.controller.remove(key)
            except Exception:
                pass
