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
    # Prioridade 1: Secrets do Streamlit (Cloud ou arquivo local .streamlit/secrets.toml)
    try:
        # No Streamlit, st.secrets funciona como objeto com atributos
        senha = st.secrets.get("SENHA_ADMIN", None)
        if senha:
            return str(senha).strip()
    except:
        try:
            # Tentar acessar diretamente como atributo
            senha = st.secrets.SENHA_ADMIN
            if senha:
                return str(senha).strip()
        except:
            pass
    
    # Prioridade 2: Variável de ambiente
    senha_env = os.environ.get("SENHA_ADMIN")
    if senha_env:
        return str(senha_env).strip()
    
    # Prioridade 3: Senha padrão (fallback)
    return "quemhackearegay666"


def autenticar(senha_digitada: str) -> bool:
    """Verifica se a senha digitada está correta."""
    if not senha_digitada:
        return False
    
    senha_correta = obter_senha()
    if not senha_correta:
        return False
    
    # Normalizar senhas (remover espaços e converter para string)
    senha_digitada_normalizada = str(senha_digitada).strip()
    senha_correta_normalizada = str(senha_correta).strip()
    
    # Comparar senhas
    if senha_digitada_normalizada == senha_correta_normalizada:
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
                if senha:
                    # Tentar autenticar
                    if autenticar(senha):
                        st.success("✅ Autenticado com sucesso!")
                        st.rerun()
                    else:
                        # Mostrar mensagem de erro
                        senha_esperada = obter_senha()
                        st.error("❌ Senha incorreta! Verifique a senha e tente novamente.")
                        # Debug apenas em desenvolvimento (comentar em produção)
                        # st.caption(f"Debug: Senha esperada começa com '{senha_esperada[:3]}...' (apenas para debug)")
                else:
                    st.warning("⚠️ Por favor, digite a senha.")
            
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
                
                # Se autenticado, mostrar opções de deletar
                if autenticado:
                    st.markdown("---")
                    st.subheader("🗑️ Deletar Hunts")
                    
                    # Criar um selectbox com as hunts para deletar
                    opcoes_hunts = []
                    for hunt in hunts:
                        # hunt = (id, respawn, horario_inicio, horario_fim, integrante1, ..., integrante5, data_cadastro)
                        hunt_id = hunt[0]
                        horario_inicio = hunt[2]
                        horario_fim = hunt[3]
                        integrantes = []
                        for i in range(4, 9):
                            if hunt[i] and hunt[i].strip():
                                integrantes.append(hunt[i].strip())
                        integrantes_str = ", ".join(integrantes) if integrantes else "Sem integrantes"
                        label = f"ID {hunt_id}: {horario_inicio} - {horario_fim} ({integrantes_str})"
                        opcoes_hunts.append((hunt_id, label))
                    
                    if opcoes_hunts:
                        hunt_selecionada = st.selectbox(
                            "Selecione a hunt para deletar:",
                            options=opcoes_hunts,
                            format_func=lambda x: x[1],
                            key=f"delete_select_{respawn}"
                        )
                        
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if st.button("🗑️ Deletar", type="secondary", key=f"delete_btn_{respawn}"):
                                hunt_id_para_deletar = hunt_selecionada[0]
                                if database.delete_hunt(hunt_id_para_deletar):
                                    st.success(f"✅ Hunt ID {hunt_id_para_deletar} deletada com sucesso!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro ao deletar hunt ID {hunt_id_para_deletar}")
                        with col2:
                            st.caption("⚠️ Esta ação não pode ser desfeita!")


if __name__ == "__main__":
    main()
