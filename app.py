import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import json
from io import StringIO

# Funcoes auxiliares
def registrar_acao(nome_usuario, acao):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_mensagem = f"[{timestamp}] Usuário: {nome_usuario} - Ação: {acao}\n"
    with open("registro_acoes.log", "a") as arquivo_log:
        arquivo_log.write(log_mensagem)

def visualizar_logs(data_inicio=None, data_fim=None):
    try:
        with open("registro_acoes.log", "r") as log:
            linhas = log.readlines()
            linhas.reverse()  # ordem decrescente
            if data_inicio and data_fim:
                filtradas = []
                for linha in linhas:
                    timestamp_str = linha.split("]")[0][1:]
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    if data_inicio <= timestamp <= data_fim:
                        filtradas.append(linha)
                return "".join(filtradas)
            return "".join(linhas)
    except FileNotFoundError:
        return "Arquivo de log não encontrado."

def analisar_dados_basico(df):
    total = len(df)
    generos = df['Gender'].value_counts()
    sem_educacao = df['Parent_Education_Level'].isnull().sum()
    return total, generos, sem_educacao

def limpar_dados(df):
    df_limpo = df.dropna(subset=['Parent_Education_Level']).copy()
    removidos = len(df) - len(df_limpo)
    mediana = df_limpo['Attendance (%)'].median()
    faltantes = df_limpo['Attendance (%)'].isnull().sum()
    df_limpo['Attendance (%)'] = df_limpo['Attendance (%)'].fillna(mediana)
    soma_attendance = df_limpo['Attendance (%)'].sum()
    generos_pos = df_limpo['Gender'].value_counts()
    return df_limpo, removidos, faltantes, mediana, soma_attendance, generos_pos

def gerar_graficos(df):
    fig1, ax1 = plt.subplots()
    sns.scatterplot(data=df, x='Sleep_Hours_per_Night', y='Final_Score', ax=ax1)
    ax1.set_title('Horas de Sono vs. Nota Final')

    fig2, ax2 = plt.subplots()
    df.groupby('Age')['Midterm_Score'].mean().plot(kind='bar', ax=ax2)
    ax2.set_title('Idade vs. Média das Notas Intermediárias')
    ax2.set_xlabel('Idade')
    ax2.set_ylabel('Média da Nota')

    fig3, ax3 = plt.subplots()
    df['Age'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax3)
    ax3.set_title('Distribuição das Idades')
    ax3.set_ylabel('')

    return fig1, fig2, fig3

# Interface Streamlit
st.title("Análise de Dados Educacionais")
nome_usuario = st.text_input("Digite seu nome completo:")

if nome_usuario:
    arquivo = st.file_uploader("Carregue o arquivo CSV ou JSON", type=["csv", "json"])
    if arquivo is not None:
        if arquivo.name.endswith(".csv"):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_json(arquivo)

        registrar_acao(nome_usuario, "Carregou o arquivo de dados")

        st.subheader("--- Análise Básica dos Dados ---")
        total, generos, sem_educacao = analisar_dados_basico(df)
        st.write(f"Quantidade total de registros carregados: {total}")
        st.write("Distribuição por gênero:")
        st.write(generos)
        st.write(f"Quantidade de registros sem informação sobre a educação dos pais: {sem_educacao}")

        df_limpo, removidos, faltantes, mediana, soma_att, generos_pos = limpar_dados(df)
        st.write(f"Registros removidos devido à falta de informação na educação dos pais: {removidos}")
        st.write(f"Valores nulos preenchidos na coluna 'Attendance (%)' com a mediana: {mediana:.2f}%")
        st.write(f"Somatório da coluna 'Attendance (%)': {soma_att:.2f}%")
        st.write(f"Quantidade total de registros carregados após limpeza dos dados: {len(df_limpo)}")
        st.write("--- Distribuição de gênero após a limpeza dos dados ---")
        st.write(generos_pos)

        st.subheader("--- Menu Principal ---")
        opcao = st.selectbox("Escolha uma opção:", ["Consultar dados por coluna", "Gerar gráficos", "Visualizar Logs", "Exportar Dados", "Abrir Documentação"])

        if opcao == "Consultar dados por coluna":
            colunas = df_limpo.select_dtypes(include='number').columns.tolist()
            coluna = st.selectbox("Colunas numéricas disponíveis para análise:", colunas)
            if coluna:
                st.subheader(f"--- Estatísticas da coluna '{coluna}' ---")
                st.write("Média:", df_limpo[coluna].mean())
                st.write("Mediana:", df_limpo[coluna].median())
                moda_valores = df_limpo[coluna].mode().tolist()
                if len(moda_valores) == 1:
                    st.write("Moda:", moda_valores[0])
                else:
                    st.write("Moda:", moda_valores)
                st.write("Desvio Padrão:", df_limpo[coluna].std())

        elif opcao == "Gerar gráficos":
            grafico = st.selectbox("Escolha uma opção de gráfico:", [
                "Gráfico de Dispersão: Horas de Sono vs. Nota Final",
                "Gráfico de Barras: Idade vs. Média das Notas Intermediárias",
                "Gráfico de Pizza: Distribuição das Idades",
                "Visualizar Todos"
            ])

            fig1, fig2, fig3 = gerar_graficos(df_limpo)
            if grafico == "Gráfico de Dispersão: Horas de Sono vs. Nota Final":
                st.pyplot(fig1)
            elif grafico == "Gráfico de Barras: Idade vs. Média das Notas Intermediárias":
                st.pyplot(fig2)
            elif grafico == "Gráfico de Pizza: Distribuição das Idades":
                st.pyplot(fig3)
            elif grafico == "Visualizar Todos":
                st.pyplot(fig1)
                st.pyplot(fig2)
                st.pyplot(fig3)
                registrar_acao(nome_usuario, "Visualizou todos os gráficos em conjunto")

            for i, fig in enumerate([fig1, fig2, fig3], start=1):
                buf = StringIO()
                fig.savefig(f"grafico_{i}.png")
                with open(f"grafico_{i}.png", "rb") as f:
                    st.download_button(label=f"Download Gráfico {i}", data=f, file_name=f"grafico_{i}.png")

        elif opcao == "Visualizar Logs":
            st.subheader("Visualizar Logs")
            data_inicio = st.date_input("Data inicial", value=datetime.date.today())
            data_fim = st.date_input("Data final", value=datetime.date.today())
            if data_inicio and data_fim:
                logs_filtrados = visualizar_logs(datetime.datetime.combine(data_inicio, datetime.time.min),
                                                 datetime.datetime.combine(data_fim, datetime.time.max))
                st.text(logs_filtrados)
                st.download_button("Download Logs", data=logs_filtrados, file_name="log.txt")

        elif opcao == "Exportar Dados":
            df_limpo.to_csv("dados_limpos.csv", index=False)
            stats = {
                "total": len(df_limpo),
                "generos": df_limpo["Gender"].value_counts().to_dict(),
                "media_attendance": df_limpo["Attendance (%)"].mean()
            }
            with open("estatisticas.json", "w") as f:
                json.dump(stats, f, indent=4)
            st.success("Dados exportados com sucesso!")
            with open("dados_limpos.csv", "rb") as f:
                st.download_button("Download CSV", data=f, file_name="dados_limpos.csv")
            with open("estatisticas.json", "rb") as f:
                st.download_button("Download Estatísticas", data=f, file_name="estatisticas.json")

        elif opcao == "Abrir Documentação":
            import webbrowser
            import platform
            caminho = os.path.abspath("_build/index.html")
            registrar_acao(nome_usuario, "Abriu a documentação")
            sistema = platform.system()
            try:
                if sistema == "Windows":
                    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
                    if os.path.exists(chrome_path):
                        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
                        webbrowser.get('chrome').open_new_tab(caminho)
                        st.success("Documentação aberta no Chrome.")
                    else:
                        st.warning(f"Chrome não encontrado no caminho padrão. Abra manualmente: {caminho}")
                else:
                    webbrowser.open_new_tab(caminho)
                    st.success("Documentação aberta no navegador padrão.")
            except Exception as e:
                st.error("Não foi possível abrir automaticamente. Abra manualmente:")
                st.text(caminho)