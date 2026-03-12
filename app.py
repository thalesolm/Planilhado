import streamlit as st
from datetime import time
import os

import database
import validators
import viz

# Índices dos dias: 0=Dom, 1=Seg, 2=Ter, 3=Qua, 4=Qui, 5=Sex, 6=Sab
DIAS_IDS = list(range(7))
DIAS_NOMES = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]


def _obter_dias_selecionados(key_prefix: str) -> str:
    """Lê os checkboxes de dias e retorna string no formato '0,1,2,3,4,5,6'."""
    selecionados = []
    for i in DIAS_IDS:
        if st.session_state.get(key_prefix + f"_dias_{i}", False):
            selecionados.append(str(i))
    return ",".join(selecionados) if selecionados else None


def widget_dias_semana(key_prefix: str) -> str:
    """
    Renderiza atalhos (Semana toda, Seg-Sex, Sab-Dom) e checkboxes por dia.
    key_prefix diferencia formulário de requisição ('req_') do de hunt ('hunt_').
    Retorna a string para salvar no banco (ex: '1,2,3,4,5') ou None.
    """
    # Inicializar com Seg-Sex na primeira vez
    if not any(key_prefix + f"_dias_{i}" in st.session_state for i in DIAS_IDS):
        for i in DIAS_IDS:
            st.session_state[key_prefix + f"_dias_{i}"] = (i in [1, 2, 3, 4, 5])

    st.markdown("#### 📅 Dias da semana 📅")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Semana toda", key=key_prefix + "_btn_semana", use_container_width=True):
            for i in DIAS_IDS:
                st.session_state[key_prefix + f"_dias_{i}"] = True
            st.rerun()
    with col2:
        if st.button("Seg - Sex", key=key_prefix + "_btn_segsex", use_container_width=True):
            for i in DIAS_IDS:
                st.session_state[key_prefix + f"_dias_{i}"] = i in [1, 2, 3, 4, 5]
            st.rerun()
    with col3:
        if st.button("Sab - Dom", key=key_prefix + "_btn_sabdom", use_container_width=True):
            for i in DIAS_IDS:
                st.session_state[key_prefix + f"_dias_{i}"] = i in [0, 6]
            st.rerun()

    cols = st.columns(7)
    for i, nome in enumerate(DIAS_NOMES):
        with cols[i]:
            st.checkbox(
                nome[:3],
                key=key_prefix + f"_dias_{i}",
                help=nome,
            )

    return _obter_dias_selecionados(key_prefix)

# Configuração da página
st.set_page_config(
    page_title="Planilhado de Hunts - Carreta Encore",
    page_icon="💀",
    layout="wide"
)


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


def mostrar_requisicao_interface():
    """Interface para usuários fazerem requisições de horários."""
    st.markdown("### 🔥📝 Solicitar Horário 📝🔥")
    st.info("💀 Preencha os dados abaixo para solicitar um horário. O administrador irá revisar sua solicitação. 💀")
    
    # Botão para voltar
    if st.button("← Voltar", key="voltar_requisicao"):
        st.session_state['mostrar_requisicao'] = False
        st.rerun()
    
    st.markdown("---")
    
    # Buscar respawns existentes
    respawns_existentes = database.get_respawns()
    
    # Campo Respawn com autocomplete
    opcoes_respawn = ["Novo respawn"] + respawns_existentes
    respawn_selecionado = st.selectbox(
        "Respawn",
        options=opcoes_respawn,
        key="req_respawn_select"
    )
    
    if respawn_selecionado == "Novo respawn":
        respawn = st.text_input(
            "Digite o nome do novo respawn",
            key="req_respawn_new",
            placeholder="Ex: Livraria de Energy"
        )
    else:
        respawn = respawn_selecionado
    
    # Timebox
    st.markdown("#### 🔥⏰ Horários ⏰🔥")
    horario_inicio = st.time_input(
        "Horário Inicial",
        value=time(15, 0),
        key="req_horario_inicio"
    )
    horario_fim = st.time_input(
        "Horário Final",
        value=time(18, 0),
        key="req_horario_fim"
    )

    widget_dias_semana("req_")
    
    # Integrantes
    st.markdown("#### 💀👥 Integrantes da Party 👥💀")
    integrante1 = st.text_input("Integrante 1", key="req_int1")
    integrante2 = st.text_input("Integrante 2", key="req_int2")
    integrante3 = st.text_input("Integrante 3", key="req_int3")
    integrante4 = st.text_input("Integrante 4", key="req_int4")
    integrante5 = st.text_input("Integrante 5", key="req_int5")
    
    # Botão Submeter
    if st.button("🔥💀 Submeter Requisição 💀🔥", type="primary", use_container_width=True):
        # Validar campos obrigatórios
        if not respawn or not respawn.strip():
            st.error("💀⚠️ Por favor, preencha o campo Respawn. ⚠️💀")
            return
        
        # Converter horários para string HH:MM
        horario_inicio_str = horario_inicio.strftime("%H:%M")
        horario_fim_str = horario_fim.strftime("%H:%M")
        
        # Validar horários
        valido, mensagem_erro = validators.validar_horarios(
            horario_inicio_str, horario_fim_str
        )
        if not valido:
            st.error(f"💀⚠️ {mensagem_erro} ⚠️💀")
            return
        
        # Overlap permitido: não verificamos mais conflito de horário.

        # Salvar requisição
        dias_semana_str = _obter_dias_selecionados("req_")
        try:
            database.insert_requisicao(
                respawn=respawn.strip(),
                horario_inicio=horario_inicio_str,
                horario_fim=horario_fim_str,
                integrante1=integrante1.strip() if integrante1 else None,
                integrante2=integrante2.strip() if integrante2 else None,
                integrante3=integrante3.strip() if integrante3 else None,
                integrante4=integrante4.strip() if integrante4 else None,
                integrante5=integrante5.strip() if integrante5 else None,
                dias_semana=dias_semana_str
            )
            st.success("💀🔥✅ Requisição enviada com sucesso! Aguarde aprovação do administrador. ✅🔥💀")
            st.session_state['mostrar_requisicao'] = False
            st.rerun()
        except Exception as e:
            st.error(f"💀❌ Erro ao enviar requisição: {str(e)} ❌💀")


def mostrar_aprovacao_requisicoes():
    """Interface para admin aprovar/rejeitar requisições."""
    requisicoes = database.get_all_requisicoes()
    count_pendentes = len(requisicoes)
    
    # Badge com contador de requisições pendentes
    if count_pendentes > 0:
        st.markdown(f"""
        <div style='background-color: #FF4B4B; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center;'>
            <h3>💀🔥 {count_pendentes} Requisição(ões) Pendente(s) 🔥💀</h3>
        </div>
        """, unsafe_allow_html=True)
    
    if not requisicoes:
        st.info("💀✅ Nenhuma requisição pendente no momento. ✅💀")
        st.markdown("---")
        return
    
    st.markdown("### 💀⚖️ Requisições Pendentes ⚖️💀")
    
    for req in requisicoes:
        # req = (id, respawn, horario_inicio, horario_fim, integrante1, ..., integrante5, data_requisicao)
        req_id = req[0]
        respawn = req[1]
        horario_inicio = req[2]
        horario_fim = req[3]
        
        integrantes = []
        for i in range(4, 9):
            if req[i] and req[i].strip():
                integrantes.append(req[i].strip())
        integrantes_str = ", ".join(integrantes) if integrantes else "Sem integrantes"
        
        with st.expander(f"💀 {respawn} - {horario_inicio} às {horario_fim} ({integrantes_str})", expanded=True):
            col1, col2 = st.columns(2)
            
            st.write(f"**Respawn:** {respawn}")
            st.write(f"**Horário:** {horario_inicio} - {horario_fim}")
            st.write(f"**Dias:** {viz.formatar_dias_semana(req[9] if len(req) > 9 else None)}")
            st.write(f"**Integrantes:** {integrantes_str}")
            st.write(f"**Data da Requisição:** {req[10] if len(req) > 10 else req[9]}")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button(f"✅ Aceitar", key=f"accept_{req_id}", type="primary", use_container_width=True):
                    # Overlap permitido: aceitar sem verificar conflito.
                    # req: id, respawn, h_inicio, h_fim, i1..i5, dias_semana, data_requisicao
                    dias_semana_req = req[9] if len(req) > 9 else None
                    # Mover para hunts
                    database.insert_hunt(
                        respawn=respawn,
                        horario_inicio=horario_inicio,
                        horario_fim=horario_fim,
                        integrante1=req[4] if len(req) > 4 else None,
                        integrante2=req[5] if len(req) > 5 else None,
                        integrante3=req[6] if len(req) > 6 else None,
                        integrante4=req[7] if len(req) > 7 else None,
                        integrante5=req[8] if len(req) > 8 else None,
                        dias_semana=dias_semana_req
                    )
                    # Deletar requisição
                    database.delete_requisicao(req_id)
                    st.success(f"💀🔥✅ Requisição ID {req_id} aceita e adicionada ao planilhado! ✅🔥💀")
                    st.rerun()
            
            with col2:
                if st.button(f"❌ Rejeitar", key=f"reject_{req_id}", type="secondary", use_container_width=True):
                    database.delete_requisicao(req_id)
                    st.success(f"💀❌ Requisição ID {req_id} rejeitada e removida. ❌💀")
                    st.rerun()
            
            with col3:
                st.caption("Overlaps de horário são permitidos.")
        
        st.markdown("---")


def main():
    # Inicializar banco de dados (dentro do contexto Streamlit para garantir que secrets estejam disponíveis)
    try:
        database.init_db()
        status = database.get_connection_status()
    except Exception as e:
        st.error(f"💀 Erro ao conectar no banco de dados: {str(e)}")
        st.info("Verifique se DATABASE_URL está configurada nos Secrets (Streamlit Cloud) ou use SQLite local.")
        st.stop()

    # Indicador de banco (confirma que a conexão foi executada)
    with st.sidebar:
        st.caption(f"🗄️ Banco: {status}")
        if database.postgres_failed():
            st.warning(
                "PostgreSQL falhou; usando SQLite (dados podem sumir quando o app dormir)."
            )
            err = database.get_postgres_error_message()
            if err:
                with st.expander("Ver detalhe do erro da conexão", expanded=False):
                    st.code(err, language=None)
                st.caption("Confira: senha no Secrets = senha do banco no Supabase; uso do pooler (porta 6543).")

    # Título com ícones malvadões
    st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='color: #FF4B4B; font-size: 2.5em; margin-bottom: 10px; white-space: nowrap;'>
            💀💀💀 Planilhado de Hunts - Carreta Encore 💀💀💀
        </h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Verificar autenticação
    autenticado = verificar_autenticacao()
    
    # Sidebar
    with st.sidebar:
        if not autenticado:
            # Formulário de autenticação
            st.markdown("### 💀🔐 Acesso de Edição 🔐💀")
            st.info("🔥 Qualquer pessoa pode visualizar o planilhado, mas apenas usuários autorizados podem editar. 🔥")
            
            senha = st.text_input(
                "Senha de Administrador",
                type="password",
                key="senha_input",
                placeholder="Digite a senha para editar"
            )
            
            if st.button("💀🔓 Entrar 🔓💀", type="primary", use_container_width=True):
                if senha:
                    # Tentar autenticar
                    if autenticar(senha):
                        st.success("💀🔥✅ Autenticado com sucesso! ✅🔥💀")
                        st.rerun()
                    else:
                        # Mostrar mensagem de erro
                        senha_esperada = obter_senha()
                        st.error("💀❌ Senha incorreta! Verifique a senha e tente novamente. ❌💀")
                        # Debug apenas em desenvolvimento (comentar em produção)
                        # st.caption(f"Debug: Senha esperada começa com '{senha_esperada[:3]}...' (apenas para debug)")
                else:
                    st.warning("🔥⚠️ Por favor, digite a senha. ⚠️🔥")
            
            st.markdown("---")
            
            # Botão para fazer requisição
            st.markdown("### 🔥📝 Fazer Requisição 📝🔥")
            st.info("💀 Solicite um horário para ser aprovado pelo administrador. 💀")
            
            if st.button("💀📋 Solicitar Horário 📋💀", use_container_width=True, key="btn_requisicao"):
                st.session_state['mostrar_requisicao'] = True
                st.rerun()
            
            st.markdown("---")
            st.caption("Para visualizar, role a página para baixo 👇")
        else:
            # Formulário de cadastro (apenas se autenticado)
            st.markdown("### 🔪➕ Nova Hunt ➕🔪")
            
            # Contador de requisições pendentes
            count_requisicoes = database.count_requisicoes_pendentes()
            if count_requisicoes > 0:
                st.markdown(f"""
                <div style='background-color: #FF4B4B; color: white; padding: 8px; border-radius: 5px; margin-bottom: 10px; text-align: center; font-weight: bold;'>
                    💀🔥 {count_requisicoes} Requisição(ões) Pendente(s) 🔥💀
                </div>
                """, unsafe_allow_html=True)
            
            # Botão de logout
            if st.button("💀🚪 Sair 🚪💀", use_container_width=True):
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
            st.markdown("#### 🔥⏰ Horários ⏰🔥")
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

            widget_dias_semana("hunt_")

            # Integrantes
            st.markdown("#### 💀👥 Integrantes da Party 👥💀")
            integrante1 = st.text_input("Integrante 1", key="int1")
            integrante2 = st.text_input("Integrante 2", key="int2")
            integrante3 = st.text_input("Integrante 3", key="int3")
            integrante4 = st.text_input("Integrante 4", key="int4")
            integrante5 = st.text_input("Integrante 5", key="int5")
            
            # Botão Salvar
            if st.button("🔥💀 Salvar Hunt 💀🔥", type="primary", use_container_width=True):
                # Validar campos obrigatórios
                if not respawn or not respawn.strip():
                    st.error("💀⚠️ Por favor, preencha o campo Respawn. ⚠️💀")
                    return
                
                # Converter horários para string HH:MM
                horario_inicio_str = horario_inicio.strftime("%H:%M")
                horario_fim_str = horario_fim.strftime("%H:%M")
                
                # Validar horários
                valido, mensagem_erro = validators.validar_horarios(
                    horario_inicio_str, horario_fim_str
                )
                if not valido:
                    st.error(f"💀⚠️ {mensagem_erro} ⚠️💀")
                    return
                
                # Overlap permitido: não verificamos mais conflito de horário.

                # Salvar no banco
                dias_semana_str = _obter_dias_selecionados("hunt_")
                try:
                    database.insert_hunt(
                        respawn=respawn.strip(),
                        horario_inicio=horario_inicio_str,
                        horario_fim=horario_fim_str,
                        integrante1=integrante1.strip() if integrante1 else None,
                        integrante2=integrante2.strip() if integrante2 else None,
                        integrante3=integrante3.strip() if integrante3 else None,
                        integrante4=integrante4.strip() if integrante4 else None,
                        integrante5=integrante5.strip() if integrante5 else None,
                        dias_semana=dias_semana_str
                    )
                    st.success("💀🔥✅ Hunt salva com sucesso! ✅🔥💀")
                    st.rerun()
                except Exception as e:
                    st.error(f"💀❌ Erro ao salvar: {str(e)} ❌💀")
    
    # Verificar se deve mostrar interface de requisição
    if not autenticado and st.session_state.get('mostrar_requisicao', False):
        mostrar_requisicao_interface()
        return
    
    # Se autenticado, mostrar tela de aprovação de requisições
    if autenticado:
        mostrar_aprovacao_requisicoes()
    
    # Área principal - Visualização
    st.markdown("""
    <div style='text-align: center; margin: 20px 0;'>
        <h2>🐍📊 Visualização do Planilhado 📊🐍</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Buscar todas as hunts
    todas_hunts = database.get_all_hunts()
    
    if not todas_hunts:
        st.info("💀📝 Nenhuma hunt cadastrada ainda. Use o formulário na barra lateral para adicionar uma nova hunt. 📝💀")
    else:
        # Agrupar por respawn
        hunts_por_respawn = viz.agrupar_hunts_por_respawn(todas_hunts)
        
        # Ordenar respawns alfabeticamente
        respawns_ordenados = sorted(hunts_por_respawn.keys())
        
        # Exibir quadro para cada respawn
        for respawn in respawns_ordenados:
            hunts = hunts_por_respawn[respawn]
            df = viz.gerar_quadro_respawn(respawn, hunts)
            
            # Usar expander para cada respawn
            with st.expander(f"💀🔥 **{respawn}** 🔥💀 ({len(hunts)} hunt{'s' if len(hunts) > 1 else ''})", expanded=True):
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Se autenticado, mostrar opções de deletar
                if autenticado:
                    st.markdown("---")
                    st.markdown("### 🔪🗑️ Deletar Hunts 🗑️🔪")
                    
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
                            if st.button("💀🗑️ Deletar 🗑️💀", type="secondary", key=f"delete_btn_{respawn}"):
                                hunt_id_para_deletar = hunt_selecionada[0]
                                if database.delete_hunt(hunt_id_para_deletar):
                                    st.success(f"💀🔥✅ Hunt ID {hunt_id_para_deletar} deletada com sucesso! ✅🔥💀")
                                    st.rerun()
                                else:
                                    st.error(f"💀❌ Erro ao deletar hunt ID {hunt_id_para_deletar} ❌💀")
                        with col2:
                            st.caption("🔥⚠️ Esta ação não pode ser desfeita! ⚠️🔥")


if __name__ == "__main__":
    main()
