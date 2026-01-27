import streamlit as st
from datetime import time
import database
import validators
import visualizations
import os

# Configuração da página
st.set_page_config(
    page_title="Planilhado",
    page_icon="📋",
    layout="wide"
)

# Inicializar banco de dados
database.init_db()


def verificar_autenticacao():
    """Verifica se o usuário está autenticado. Retorna True se autenticado."""
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    return st.session_state.autenticado


def obter_senha():
    """Obtém a senha de autenticação dos secrets ou variável de ambiente."""
    # Tentar obter do secrets do Streamlit (arquivo .streamlit/secrets.toml ou Cloud)
    try:
        if hasattr(st, 'secrets'):
            # Tentar acessar como dicionário
            if isinstance(st.secrets, dict) and 'SENHA_ADMIN' in st.secrets:
                return st.secrets['SENHA_ADMIN']
            # Tentar acessar como atributo
            elif hasattr(st.secrets, 'SENHA_ADMIN'):
                return st.secrets.SENHA_ADMIN
    except Exception as e:
        # Se houver erro, continuar para outros métodos
        pass
    
    # Fallback para variável de ambiente (desenvolvimento local)
    senha_env = os.environ.get("SENHA_ADMIN")
    if senha_env:
        return senha_env
    
    # Senha padrão para desenvolvimento (apenas se nenhuma outra estiver configurada)
    return "admin123"


def autenticar(senha_digitada: str) -> bool:
    """Verifica se a senha digitada está correta."""
    if not senha_digitada:
        return False
    
    senha_correta = obter_senha()
    if not senha_correta:
        return False
    
    # Comparar senhas (removendo espaços em branco)
    if senha_digitada.strip() == str(senha_correta).strip():
        st.session_state.autenticado = True
        return True
    return False


def main():
    st.title("📋 Planilhado de Hunts")
    st.markdown("---")
    
    # Verificar autenticação
    autenticado = verificar_autenticacao()
    
    # Sidebar
    with st.sidebar:
        if not autenticado:
            # Formulário de autenticação
            st.header("🔐 Acesso de Edição")
            st.info("💡 Qualquer pessoa pode visualizar o planilhado, mas apenas usuários autorizados podem editar.")
            
            senha = st.text_input(
                "Senha de Administrador",
                type="password",
                key="senha_input",
                placeholder="Digite a senha para editar"
            )
            
            if st.button("🔓 Entrar", type="primary", use_container_width=True):
                if autenticar(senha):
                    st.success("✅ Autenticado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
            
            st.markdown("---")
            st.caption("Para visualizar, role a página para baixo 👇")
        else:
            # Formulário de cadastro (apenas se autenticado)
            st.header("➕ Nova Hunt")
            
            # Botão de logout
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.autenticado = False
                st.rerun()
            
            st.markdown("---")
            
            # Buscar respawns existentes
            respawns_existentes = database.get_respawns()
            
            # Campo Respawn com autocomplete
            opcoes_respawn = ["Novo respawn"] + respawns_existentes
            respawn_selecionado = st.selectbox(
                "Respawn",
                options=opcoes_respawn,
                key="respawn_select"
            )
            
            if respawn_selecionado == "Novo respawn":
                respawn = st.text_input(
                    "Digite o nome do novo respawn",
                    key="respawn_new",
                    placeholder="Ex: Livraria de Energy"
                )
            else:
                respawn = respawn_selecionado
            
            # Timebox
            st.subheader("Horários")
            horario_inicio = st.time_input(
                "Horário Inicial",
                value=time(15, 0),
                key="horario_inicio"
            )
            horario_fim = st.time_input(
                "Horário Final",
                value=time(18, 0),
                key="horario_fim"
            )
            
            # Integrantes
            st.subheader("Integrantes da Party")
            integrante1 = st.text_input("Integrante 1", key="int1")
            integrante2 = st.text_input("Integrante 2", key="int2")
            integrante3 = st.text_input("Integrante 3", key="int3")
            integrante4 = st.text_input("Integrante 4", key="int4")
            integrante5 = st.text_input("Integrante 5", key="int5")
            
            # Botão Salvar
            if st.button("💾 Salvar Hunt", type="primary", use_container_width=True):
                # Validar campos obrigatórios
                if not respawn or not respawn.strip():
                    st.error("⚠️ Por favor, preencha o campo Respawn.")
                    return
                
                # Converter horários para string HH:MM
                horario_inicio_str = horario_inicio.strftime("%H:%M")
                horario_fim_str = horario_fim.strftime("%H:%M")
                
                # Validar horários
                valido, mensagem_erro = validators.validar_horarios(
                    horario_inicio_str, horario_fim_str
                )
                if not valido:
                    st.error(f"⚠️ {mensagem_erro}")
                    return
                
                # Verificar overlaps
                tem_overlap, mensagem_overlap = validators.verificar_overlap(
                    respawn.strip(), horario_inicio_str, horario_fim_str
                )
                if tem_overlap:
                    st.error(f"⚠️ {mensagem_overlap}")
                    return
                
                # Salvar no banco
                try:
                    database.insert_hunt(
                        respawn=respawn.strip(),
                        horario_inicio=horario_inicio_str,
                        horario_fim=horario_fim_str,
                        integrante1=integrante1.strip() if integrante1 else None,
                        integrante2=integrante2.strip() if integrante2 else None,
                        integrante3=integrante3.strip() if integrante3 else None,
                        integrante4=integrante4.strip() if integrante4 else None,
                        integrante5=integrante5.strip() if integrante5 else None
                    )
                    st.success("✅ Hunt salva com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {str(e)}")
    
    # Área principal - Visualização
    st.header("📊 Visualização do Planilhado")
    
    # Buscar todas as hunts
    todas_hunts = database.get_all_hunts()
    
    if not todas_hunts:
        st.info("📝 Nenhuma hunt cadastrada ainda. Use o formulário na barra lateral para adicionar uma nova hunt.")
    else:
        # Agrupar por respawn
        hunts_por_respawn = visualizations.agrupar_hunts_por_respawn(todas_hunts)
        
        # Ordenar respawns alfabeticamente
        respawns_ordenados = sorted(hunts_por_respawn.keys())
        
        # Exibir quadro para cada respawn
        for respawn in respawns_ordenados:
            hunts = hunts_por_respawn[respawn]
            df = visualizations.gerar_quadro_respawn(respawn, hunts)
            
            # Usar expander para cada respawn
            with st.expander(f"🎯 **{respawn}** ({len(hunts)} hunt{'s' if len(hunts) > 1 else ''})", expanded=True):
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )


if __name__ == "__main__":
    main()
