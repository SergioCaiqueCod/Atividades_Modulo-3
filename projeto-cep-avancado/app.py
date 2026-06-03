# import streamlit as st
# from ferramentas import buscar_cep,buscar_tempo
# import pandas as pd

# st.sidebar.  image("logo.png")
# st.sidebar.title(" Cep Aladin")
# cep=st.sidebar.text_input('Digite seu CEP sem caracteres especiais:')

# if st.sidebar.button("Buscar"):
#     dados_cep = buscar_cep(cep)# busca na API
#     st.json(dados_cep)#exibe na tela os dados

#     if dados_cep.get("lat"):
#         lat = float(dados_cep.get("lat"))
#         lng = float(dados_cep.get("lng"))
#         dados_clima = buscar_tempo(lat,lng)# busca na API de clima
#         chance_chuva = pd.DataFrame(dados_clima['daily'])
#         st.bar_chart(data=chance_chuva, x="time",y="precipitation_probability_max")

#         st.json(dados_clima) #exibe 
#         st.map(pd.DataFrame({"latitude":[lat],"longitude":[lng]}),zoom=14)

import streamlit as st
import pandas as pd
from ferramentas import buscar_cep, buscar_tempo


# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Clima por CEP",
    page_icon="🌦️",
    layout="wide"
)


# ---------------------------------------------------------
# ESTILO VISUAL OPCIONAL
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
        }

        .card-localizacao {
            padding: 1.2rem;
            border-radius: 18px;
            border: 1px solid rgba(128, 128, 128, 0.25);
            background: rgba(128, 128, 128, 0.08);
            margin-bottom: 1rem;
        }

        .texto-suave {
            color: #888;
            font-size: 0.9rem;
        }

        .alerta-baixo {
            padding: 1rem;
            border-radius: 14px;
            background-color: rgba(46, 204, 113, 0.12);
            border: 1px solid rgba(46, 204, 113, 0.35);
        }

        .alerta-medio {
            padding: 1rem;
            border-radius: 14px;
            background-color: rgba(241, 196, 15, 0.14);
            border: 1px solid rgba(241, 196, 15, 0.40);
        }

        .alerta-alto {
            padding: 1rem;
            border-radius: 14px;
            background-color: rgba(231, 76, 60, 0.14);
            border: 1px solid rgba(231, 76, 60, 0.40);
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# FUNÇÕES AUXILIARES DO DASHBOARD
# ---------------------------------------------------------
def preparar_previsao(dados_clima: dict) -> pd.DataFrame:
    """
    Transforma o bloco daily do JSON de clima em um DataFrame
    pronto para gráfico e tabela.
    """
    daily = dados_clima.get("daily", {})

    df = pd.DataFrame(daily)

    if df.empty:
        return df

    df = df.rename(
        columns={
            "time": "data",
            "precipitation_probability_max": "chance_chuva"
        }
    )

    df["data"] = pd.to_datetime(df["data"])

    dias_semana = {
        0: "Seg",
        1: "Ter",
        2: "Qua",
        3: "Qui",
        4: "Sex",
        5: "Sáb",
        6: "Dom",
    }

    df["dia_semana"] = df["data"].dt.weekday.map(dias_semana)
    df["data_formatada"] = df["dia_semana"] + " " + df["data"].dt.strftime("%d/%m")

    return df


def classificar_chuva(probabilidade: float) -> tuple[str, str]:
    """
    Classifica a chance de chuva para exibir um alerta visual.
    """
    if probabilidade >= 70:
        return "alerta-alto", "🌧️ Alta chance de chuva. Melhor sair preparado."
    elif probabilidade >= 30:
        return "alerta-medio", "🌦️ Chance moderada de chuva. Vale ficar atento."
    else:
        return "alerta-baixo", "☀️ Baixa chance de chuva para hoje."


def renderizar_dashboard(dados_cep: dict, dados_clima: dict):
    """
    Renderiza o dashboard principal.
    """
    lat = float(dados_cep["lat"])
    lng = float(dados_cep["lng"])

    current = dados_clima.get("current", {})
    temperatura = current.get("temperature_2m")
    horario_atualizacao = current.get("time")
    is_day = current.get("is_day")

    previsao = preparar_previsao(dados_clima)

    endereco = dados_cep.get("address", "Endereço não informado")
    bairro = dados_cep.get("district", "Bairro não informado")
    cidade = dados_cep.get("city", "Cidade não informada")
    estado = dados_cep.get("state", "UF")
    cep = dados_cep.get("cep", "")

    st.title("🌦️ Dashboard de Clima por CEP")
    st.caption(f"Previsão para **{endereco} - {bairro}, {cidade}/{estado}**")

    if horario_atualizacao:
        st.caption(f"Última atualização climática: {horario_atualizacao}")

    # -----------------------------------------------------
    # CARDS PRINCIPAIS
    # -----------------------------------------------------
    if not previsao.empty:
        chuva_hoje = previsao.iloc[0]["chance_chuva"]
        maior_chuva = previsao["chance_chuva"].max()
        media_chuva = previsao["chance_chuva"].mean()
    else:
        chuva_hoje = 0
        maior_chuva = 0
        media_chuva = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if temperatura is not None:
            st.metric("Temperatura atual", f"{temperatura:.1f} °C")
        else:
            st.metric("Temperatura atual", "N/D")

    with col2:
        st.metric("Chuva hoje", f"{chuva_hoje:.0f}%")

    with col3:
        st.metric("Maior chance no período", f"{maior_chuva:.0f}%")

    with col4:
        periodo = "Dia" if is_day == 1 else "Noite"
        st.metric("Período atual", periodo)

    classe_alerta, texto_alerta = classificar_chuva(chuva_hoje)

    st.markdown(
        f"""
        <div class="{classe_alerta}">
            <strong>{texto_alerta}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------------------------------
    # GRÁFICO + LOCALIZAÇÃO
    # -----------------------------------------------------
    coluna_grafico, coluna_local = st.columns([2, 1])

    with coluna_grafico:
        st.subheader("📊 Chance de chuva nos próximos dias")

        if not previsao.empty:
            st.bar_chart(
                data=previsao,
                x="data_formatada",
                y="chance_chuva",
                height=340
            )
        else:
            st.warning("Não há dados de previsão disponíveis.")

    with coluna_local:
        st.subheader("📍 Localização")

        st.markdown(
            f"""
            <div class="card-localizacao">
                <strong>{endereco}</strong><br>
                <span class="texto-suave">
                    {bairro} - {cidade}/{estado}<br>
                    CEP: {cep}<br>
                    Latitude: {lat}<br>
                    Longitude: {lng}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        mapa = pd.DataFrame(
            {
                "latitude": [lat],
                "longitude": [lng]
            }
        )

        st.map(mapa, zoom=14)

    st.divider()

    # -----------------------------------------------------
    # TABELA E DADOS DETALHADOS
    # -----------------------------------------------------
    aba1, aba2, aba3 = st.tabs(
        [
            "📅 Previsão em tabela",
            "🏠 Dados do CEP",
            "🧾 JSON bruto"
        ]
    )

    with aba1:
        if not previsao.empty:
            tabela = previsao[["data_formatada", "chance_chuva"]].copy()
            tabela = tabela.rename(
                columns={
                    "data_formatada": "Data",
                    "chance_chuva": "Chance de chuva (%)"
                }
            )

            st.dataframe(
                tabela,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhuma previsão disponível para exibir.")

    with aba2:
        st.json(dados_cep)

    with aba3:
        st.write("Dados climáticos retornados pela API:")
        st.json(dados_clima)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.title("🌎 Consulta")
    st.write("Digite um CEP para consultar a localização e a previsão do clima.")

    cep = st.text_input(
        "CEP",
        placeholder="Ex: 06501115"
    )

    buscar = st.button(
        "Buscar previsão",
        type="primary",
        use_container_width=True
    )


# ---------------------------------------------------------
# FLUXO PRINCIPAL
# ---------------------------------------------------------
if buscar:
    cep_limpo = "".join(filter(str.isdigit, cep))

    if len(cep_limpo) != 8:
        st.warning("Digite um CEP válido com 8 números.")
    else:
        with st.spinner("Buscando dados do CEP..."):
            dados_cep = buscar_cep(cep_limpo)

        if not dados_cep:
            st.error("Não foi possível encontrar dados para esse CEP.")
        elif not dados_cep.get("lat") or not dados_cep.get("lng"):
            st.error("O CEP foi encontrado, mas não possui latitude e longitude.")
            st.json(dados_cep)
        else:
            lat = float(dados_cep.get("lat"))
            lng = float(dados_cep.get("lng"))

            with st.spinner("Buscando previsão do clima..."):
                dados_clima = buscar_tempo(lat, lng)

            if not dados_clima:
                st.error("Não foi possível buscar os dados climáticos.")
            else:
                renderizar_dashboard(dados_cep, dados_clima)

else:
    st.title("🌦️ Dashboard de Clima por CEP")
    st.write(
        "Informe um CEP na barra lateral para visualizar temperatura atual, "
        "chance de chuva, previsão dos próximos dias e localização no mapa."
    )

    st.info("Exemplo de CEP para teste: 06501115")