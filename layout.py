"""
Layout orchestrator.

Every page calls one of:
  - gestor_page()      → CSS + navbar + auth → returns empresa dict or None
  - colaborador_page() → CSS + auth          → returns (avaliacao, tipo) or (None, "")
  - public_page()      → CSS only            → no auth

Caller pattern:
  empresa = layout.gestor_page()
  if not empresa:
      st.stop()
  layout.page_header("Eyebrow", "Title", "Subtitle")
"""

from __future__ import annotations

import streamlit as st
import db
import style


# ── Primitive helpers ────────────────────────────────────────────────────────

def eyebrow(text: str):
    st.markdown(
        f'<p style="font-size:0.72rem;font-weight:700;letter-spacing:0.14em;'
        f'text-transform:uppercase;color:#3b82f6;margin-bottom:0.3rem">{text}</p>',
        unsafe_allow_html=True,
    )


def page_header(eyebrow_text: str, title: str, subtitle: str = ""):
    eyebrow(eyebrow_text)
    st.title(title)
    if subtitle:
        st.markdown(f'<p class="page-sub">{subtitle}</p>', unsafe_allow_html=True)
    st.divider()


# ── Page orchestrators ───────────────────────────────────────────────────────

def public_page():
    """CSS only — for home and registration pages."""
    style.apply()


def gestor_page() -> dict | None:
    """
    CSS + navbar + auth for all gestor pages.
    Returns empresa dict when authenticated, None when not.
    Caller must do: if not empresa: st.stop()
    """
    style.apply()
    style.navbar()

    token = st.session_state.get("token_empresa", "")

    if not token:
        page_header("Acesso", "Painel de Gestão", "Digite o código da sua empresa para continuar.")
        t = st.text_input("Código da empresa", placeholder="Cole aqui", key="_auth_token")
        if st.button("Entrar", type="primary", use_container_width=True, key="_auth_btn"):
            if t.strip():
                st.session_state["token_empresa"] = t.strip()
                st.rerun()
            else:
                st.error("Digite o código da empresa.")
        return None

    empresa = db.buscar_empresa_por_token(token)
    if not empresa:
        st.error("Código inválido. Verifique e tente novamente.")
        if st.button("Voltar ao início", key="_auth_invalid_btn"):
            st.session_state.pop("token_empresa", None)
            st.switch_page("app.py")
        return None

    st.session_state["empresa_id"] = empresa["id"]
    return empresa


def colaborador_page() -> tuple:
    """
    CSS + auth for the evaluation form.
    Returns (avaliacao, tipo) when authenticated, (None, "") when not.
    Caller must do: if not avaliacao: st.stop()
    """
    style.apply()

    token = st.session_state.get("token_form", "")
    tipo = st.session_state.get("tipo_form", "colaborador")

    if not token:
        page_header("Avaliação", "Preencher avaliação",
                    "Cole o código recebido para acessar sua avaliação.")
        t = st.text_input("Código recebido", placeholder="Cole aqui", key="_colab_token")
        tipo_sel = st.radio(
            "Você é:",
            ["colaborador", "gestor"],
            format_func=lambda x: "Colaborador" if x == "colaborador" else "Gestor",
            key="_colab_tipo",
        )
        if st.button("Continuar", type="primary", use_container_width=True, key="_colab_btn"):
            if t.strip():
                st.session_state["token_form"] = t.strip()
                st.session_state["tipo_form"] = tipo_sel
                st.rerun()
            else:
                st.error("Digite o código recebido.")
        return None, ""

    avaliacao = db.buscar_avaliacao_por_token(token, tipo)
    if not avaliacao:
        st.error("Código inválido ou expirado. Verifique e tente novamente.")
        if st.button("Tentar novamente", key="_colab_retry"):
            st.session_state.pop("token_form", None)
            st.session_state.pop("tipo_form", None)
            st.rerun()
        return None, ""

    return avaliacao, tipo
