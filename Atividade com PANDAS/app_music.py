import streamlit as st
import pandas as pd

### 1. Leia o Arquivo Dados_Artistas.csv e o Transforme em dataframe
df = pd.read_parquet("Dados_Artistas.parquet")

### 2. Coloque um titulo na pagina
st.title("musicas ")

### 3. Coloque subtitulo titulo na pagina
st.subheader("Músicas internacionais")

### 4. Coloque uma logo na sidebar(barra lateral)
with st.sidebar:
      st.image("logo.png")

### 5. Não mexa abaixo, estamos criando uma selectbox, para selecionar o artista
artistas = st.sidebar.selectbox('Selecione o Artista', df['Artist'].unique())
df_artista = df[df['Artist'] == artistas]

### 6. Coloque Mais um subtitulo que mostre o artista que foi selecionado
st.subheader(artistas)

### 7. Não mexa aqui, pois esse é o for que vai percorer o dataframe
st.write('Aqui estão as músicas mais tocadas:')
for index, row in df_artista.iterrows():
        with st.container():
            st.markdown(f"### 🎵 **{row['Track']}**")
            
            col1, col2 = st.columns(2)
            col1.metric("🎵 Spotify Streams", f"{row['Stream']:,.0f}")
            col2.metric("📺 YouTube Views", f"{row['Views']:,.0f}")
            
            st.video(row['Url_youtube'])
            st.markdown("---")
st.link_button('Ouça no Spotify', url=row['Url_spotify'], type='primary')
