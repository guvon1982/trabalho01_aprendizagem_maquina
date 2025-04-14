import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import json
import webbrowser
import platform

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

    fig3 = None # Inicializa como None para o caso de erro
    ax3 = None
    # Verifica se a coluna 'Age' existe e não está vazia
    if 'Age' in df.columns and not df['Age'].dropna().empty:
        fig3, ax3 = plt.subplots() # Cria a figura/eixo apenas se a coluna for válida
        bins = [0, 18, 22, 25, float('inf')]
        labels = ['Até 17', '18 a 21', '22 a 24', '25 ou mais']

        # Cria a coluna de grupo diretamente no DataFrame (que é uma cópia dentro desta função)
        df['Grupo_Idade'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
        distribuicao_idades = df['Grupo_Idade'].value_counts().sort_index() # Pega a contagem dos GRUPOS e ordena

        # Plota usando os dados agrupados
        distribuicao_idades.plot(kind='pie', labels=distribuicao_idades.index, autopct='%1.1f%%', startangle=140, ax=ax3)
        ax3.set_title('Gráfico de Pizza: Distribuição das Idades (por Grupo)') # Título mais descritivo
        ax3.set_ylabel('') # Remove o label 'Grupo_Idade' do eixo Y que o pandas/matplotlib coloca por padrão
        # ax3.axis('equal') # Garante que a pizza seja circular (opcional, mas recomendado)

    else:
        # Se a coluna 'Age' não existir ou estiver vazia, não gera o gráfico
        print("Aviso: Coluna 'Age' não encontrada ou vazia nos dados limpos. Gráfico de Pizza não será gerado.")
        # Não precisa criar fig3/ax3 se não houver dados

    # Retorna as figuras (fig3 será None se não foi gerado)
    return fig1, fig2, fig3

# Interface Streamlit
st.title("Análise de Dados Educacionais")
# Bloco para validação do nome do usuário
nome_usuario_input = st.text_input("Digite seu nome completo (mínimo 3 letras, apenas letras e espaços):")
nome_valido = False
nome_usuario = "" # Variável que será usada no resto do script se o nome for válido

if nome_usuario_input: # Só processa se algo foi digitado
    nome_usuario_processado = nome_usuario_input.strip() # Remove espaços extras
    # Validação: Mínimo 3 caracteres, apenas letras/espaços, e pelo menos uma letra
    if (len(nome_usuario_processado) >= 3 and
        all(c.isalpha() or c.isspace() for c in nome_usuario_processado) and
        any(c.isalpha() for c in nome_usuario_processado)):
        nome_valido = True
        nome_usuario = nome_usuario_processado # Nome validado está pronto para uso
        # Não logamos a entrada do nome aqui, logamos as ações concretas depois
    else:
        st.warning("Nome inválido. Use apenas letras e espaços (mínimo 3 letras).")
        # nome_valido continua False

if nome_valido:
    # <<< INSIRA ESTA LINHA ABAIXO (opcional, mensagem de boas-vindas) >>>
    # st.success(f"Bem-vindo(a), {nome_usuario}!")

    arquivo = st.file_uploader("Carregue o arquivo CSV ou JSON", type=["csv", "json"])
    if arquivo is not None:
        # <<< INSIRA ESTE LOG ABAIXO >>>
        registrar_acao(nome_usuario, f"Iniciou upload do arquivo: {arquivo.name}")

        try: # Adiciona try-except para o carregamento do arquivo
            if arquivo.name.endswith(".csv"):
                df = pd.read_csv(arquivo)
            else: # Assume JSON se não for CSV
                # Para JSON, é mais seguro ler o conteúdo e depois passar para pandas
                # Isso evita problemas com diferentes estruturas JSON
                stringio = StringIO(arquivo.getvalue().decode("utf-8"))
                df = pd.read_json(stringio) # Recriando StringIO aqui

            # <<< ESTE LOG JÁ EXISTIA, APENAS VERIFIQUE SE ESTÁ AQUI >>>
            registrar_acao(nome_usuario, f"Carregou o arquivo de dados: {arquivo.name}")

            st.subheader("--- Análise Básica dos Dados ---")
            total, generos, sem_educacao = analisar_dados_basico(df)
            st.write(f"Quantidade total de registros carregados: {total}")
            if not generos.empty:
                st.write("Distribuição por gênero (dados brutos):")
                st.write(generos)
            st.write(f"Registros sem info. educação dos pais (dados brutos): {sem_educacao}")

            # <<< INSIRA ESTE LOG ABAIXO >>>
            registrar_acao(nome_usuario, "Iniciou a limpeza dos dados")

            df_limpo, removidos, faltantes, mediana, soma_att, generos_pos = limpar_dados(df.copy()) # Passa cópia para limpar_dados

            # <<< INSIRA ESTE LOG ABAIXO >>>
            registrar_acao(nome_usuario, f"Concluiu a limpeza. Removidos: {removidos}, Nulos preenchidos ('Attendance %'): {faltantes}")

            st.subheader("--- Informações Após Limpeza ---") # Separando a seção de limpeza
            st.write(f"Registros removidos (educação dos pais nula): {removidos}")
            if 'Attendance (%)' in df.columns: # Mostra info de Attendance apenas se a coluna existe
                st.write(f"Valores nulos preenchidos em 'Attendance (%)' (com mediana): {faltantes}")
                if mediana is not None: # Só mostra mediana se foi calculada
                     st.write(f"Mediana usada para preenchimento ('Attendance %'): {mediana:.2f}%")
                st.write(f"Somatório da coluna 'Attendance (%)' (após limpeza): {soma_att:.2f}") # O cálculo da soma foi movido para dentro de limpar_dados
            if not generos_pos.empty:
                 st.write("Distribuição de gênero (após limpeza):")
                 st.write(generos_pos)
            st.write(f"Quantidade total de registros após limpeza: {len(df_limpo)}")


            st.subheader("--- Menu Principal ---")
            opcao = st.selectbox("Escolha uma opção:", ["Consultar dados por coluna", "Gerar gráficos", "Visualizar Logs", "Exportar Dados", "Abrir Documentação"])

            # <<< INSIRA ESTE LOG ABAIXO >>>
            registrar_acao(nome_usuario, f"Selecionou a opção do menu: {opcao}")

            if opcao == "Consultar dados por coluna":
                # Filtra apenas colunas numéricas *existentes* no df_limpo
                colunas_numericas = df_limpo.select_dtypes(include='number').columns.tolist()
                if colunas_numericas:
                    coluna = st.selectbox("Colunas numéricas disponíveis para análise:", colunas_numericas)
                    if coluna: # Verifica se uma coluna foi selecionada
                        # <<< INSIRA ESTE LOG ABAIXO >>>
                        registrar_acao(nome_usuario, f"Consultou estatísticas da coluna: {coluna}")

                        st.subheader(f"--- Estatísticas da coluna '{coluna}' ---")
                        st.write(f"Média: {df_limpo[coluna].mean():.2f}")
                        st.write(f"Mediana: {df_limpo[coluna].median():.2f}")
                        # Tratamento para moda (pode haver mais de uma)
                        moda_valores = df_limpo[coluna].mode().tolist()
                        st.write(f"Moda: {moda_valores}") # Mostra a lista de modas
                        st.write(f"Desvio Padrão: {df_limpo[coluna].std():.2f}")
                else:
                    st.warning("Não há colunas numéricas nos dados limpos para analisar.")


            elif opcao == "Gerar gráficos":
                grafico = st.selectbox("Escolha uma opção de gráfico:", [
                    "Gráfico de Dispersão: Horas de Sono vs. Nota Final",
                    "Gráfico de Barras: Idade vs. Média das Notas Intermediárias",
                    "Gráfico de Pizza: Distribuição das Idades",
                    "Visualizar Todos"
                ])

                # <<< INSIRA ESTE LOG ABAIXO >>>
                registrar_acao(nome_usuario, f"Selecionou para gerar gráfico: {grafico}")

                fig1, fig2, fig3 = gerar_graficos(df_limpo.copy()) # Passa cópia para gerar_graficos

                # Exibe os gráficos que foram gerados com sucesso
                if grafico == "Gráfico de Dispersão: Horas de Sono vs. Nota Final" and fig1:
                    st.pyplot(fig1)
                elif grafico == "Gráfico de Barras: Idade vs. Média das Notas Intermediárias" and fig2:
                    st.pyplot(fig2)
                elif grafico == "Gráfico de Pizza: Distribuição das Idades" and fig3:
                    st.pyplot(fig3)
                elif grafico == "Visualizar Todos":
                    if fig1: st.pyplot(fig1)
                    if fig2: st.pyplot(fig2)
                    if fig3: st.pyplot(fig3)
                    # <<< ESTE LOG JÁ EXISTIA, APENAS VERIFIQUE SE ESTÁ AQUI >>>
                    registrar_acao(nome_usuario, "Visualizou todos os gráficos em conjunto")

                # Botões de Download (apenas para gráficos gerados com sucesso)
                figs_geradas = {'grafico_1_dispersao.png': fig1, 'grafico_2_barras.png': fig2, 'grafico_3_pizza.png': fig3}
                log_download_disponibilizado = False
                for nome_arquivo, fig in figs_geradas.items():
                    if fig: # Só oferece download se a figura existe
                         # Salvar figura em buffer de bytes para download direto
                        from io import BytesIO
                        buf = BytesIO()
                        fig.savefig(buf, format="png")
                        buf.seek(0)
                        st.download_button(label=f"Download {nome_arquivo}",
                                          data=buf,
                                          file_name=nome_arquivo,
                                          mime="image/png")
                        log_download_disponibilizado = True # Marca que pelo menos um botão foi mostrado
                        plt.close(fig) # Fecha a figura após salvar no buffer para liberar memória

                # <<< INSIRA ESTE BLOCO DE CÓDIGO ABAIXO (Log genérico para download de gráficos) >>>
                if log_download_disponibilizado:
                    registrar_acao(nome_usuario, "Disponibilizou botões para download dos gráficos gerados")


            elif opcao == "Visualizar Logs":
                st.subheader("Visualizar Logs")
                # Define limites razoáveis para as datas
                data_minima = datetime.date(2020, 1, 1)
                data_maxima = datetime.date.today()
                # Usa valores padrão mais seguros
                data_inicio_selecionada = st.date_input("Data inicial", value=data_maxima - datetime.timedelta(days=7), min_value=data_minima, max_value=data_maxima)
                data_fim_selecionada = st.date_input("Data final", value=data_maxima, min_value=data_minima, max_value=data_maxima)

                if data_inicio_selecionada and data_fim_selecionada:
                    if data_inicio_selecionada > data_fim_selecionada:
                        st.error("A data inicial não pode ser posterior à data final.")
                    else:
                        # Combina data com horário para abranger o dia todo
                        dt_inicio = datetime.datetime.combine(data_inicio_selecionada, datetime.time.min)
                        dt_fim = datetime.datetime.combine(data_fim_selecionada, datetime.time.max)

                        # <<< INSIRA ESTE LOG ABAIXO >>>
                        registrar_acao(nome_usuario, f"Solicitou visualização de logs entre {data_inicio_selecionada} e {data_fim_selecionada}")

                        logs_filtrados = visualizar_logs(dt_inicio, dt_fim)
                        st.text_area("Logs:", logs_filtrados, height=300) # Usa text_area para melhor visualização

                        # Botão de Download para os logs exibidos
                        st.download_button("Download Logs Exibidos",
                                           data=logs_filtrados.encode('utf-8'), # Codifica para bytes
                                           file_name=f"logs_{data_inicio_selecionada}_a_{data_fim_selecionada}.log",
                                           mime="text/plain")
                        # <<< INSIRA ESTE LOG ABAIXO >>>
                        registrar_acao(nome_usuario, "Disponibilizou botão para download dos logs visualizados")


            elif opcao == "Exportar Dados":
                st.subheader("Exportar Dados Processados") # Título mais claro
                try:
                    # Exportar CSV
                    csv_data = df_limpo.to_csv(index=False).encode('utf-8') # Codifica para bytes
                    st.download_button("Download Dados Limpos (CSV)",
                                       data=csv_data,
                                       file_name="dados_limpos.csv",
                                       mime="text/csv")
                    # <<< INSIRA ESTE LOG ABAIXO >>>
                    registrar_acao(nome_usuario, "Exportou dados limpos para CSV e disponibilizou download")

                    # Exportar Estatísticas JSON
                    stats = {
                        "total_registros_limpos": len(df_limpo),
                        # Converte para dict apenas se a série não estiver vazia
                        "generos_pos_limpeza": generos_pos.to_dict() if not generos_pos.empty else {},
                        # Calcula média apenas se a coluna e dados existirem
                        "media_attendance_pos_limpeza": df_limpo['Attendance (%)'].mean() if 'Attendance (%)' in df_limpo.columns and not df_limpo['Attendance (%)'].isnull().all() else None,
                        "mediana_attendance_usada": mediana # Mediana calculada durante a limpeza
                    }
                    # Converte None para string 'N/A' ou similar para JSON se preferir
                    stats_json = json.dumps(stats, indent=4, ensure_ascii=False).encode('utf-8') # ensure_ascii=False para acentos

                    st.download_button("Download Estatísticas (JSON)",
                                       data=stats_json,
                                       file_name="estatisticas_limpeza.json",
                                       mime="application/json")
                    # <<< INSIRA ESTE LOG ABAIXO >>>
                    registrar_acao(nome_usuario, "Exportou estatísticas para JSON e disponibilizou download")

                    # <<< REMOVA A LINHA st.success(...) ABAIXO, pois os botões já indicam sucesso >>>
                    # st.success("Dados exportados com sucesso!")

                    # <<< REMOVA OS BOTÕES DE DOWNLOAD QUE ESTAVAM AQUI ANTERIORMENTE >>>
                    # (Eles foram movidos para cima, logo após a criação dos dados correspondentes)

                except Exception as e:
                    st.error(f"Erro durante a exportação: {e}")
                    registrar_acao(nome_usuario, f"Falha na exportação de dados: {e}")


            elif opcao == "Abrir Documentação":
                registrar_acao(nome_usuario, "Tentou abrir a documentação")
                caminho_relativo = "_build/index.html" # Caminho corrigido
                caminho_absoluto = os.path.abspath(caminho_relativo)
                caminho_uri = f"file:///{caminho_absoluto.replace(os.sep, '/')}" # Tentativa de formato URI mais robusto

                st.write(f"Tentando abrir URI: {caminho_uri}") # Adicionado para depuração

                if os.path.exists(caminho_absoluto):
                    try:
                        # Tenta abrir diretamente com o handler padrão do sistema
                        webbrowser.open_new_tab(caminho_uri)
                        st.success("Documentação solicitada para abertura no navegador padrão.")
                        # <<< REMOVA ou Comente toda a lógica if/else de sistema/chrome que estava aqui >>>
                        # sistema = platform.system()
                        # if sistema == "Windows":
                        #     ...
                        # else:
                        #    ...

                    except Exception as e:
                        st.error(f"Não foi possível abrir automaticamente a documentação via webbrowser: {e}")
                        st.info(f"Por favor, copie e cole este caminho no seu navegador: {caminho_absoluto}")
                else:
                    st.error(f"Arquivo de documentação não encontrado em: {caminho_absoluto}")
                    st.info("Verifique se a documentação foi gerada corretamente (ex: usando `sphinx-build -b html docs _build` na pasta raiz).")

        # <<< INSIRA ESTE BLOCO try-except PARA CAPTURAR ERROS GERAIS APÓS CARREGAMENTO >>>
        except pd.errors.ParserError as pe:
            st.error(f"Erro ao processar o arquivo: Verifique o formato do {'.csv' if arquivo.name.endswith('.csv') else '.json'}. Detalhe: {pe}")
            registrar_acao(nome_usuario, f"Erro de parsing no arquivo {arquivo.name}: {pe}")
        except KeyError as ke:
             st.error(f"Erro: Coluna esperada não encontrada no arquivo: {ke}. Verifique se o arquivo tem as colunas necessárias (ex: Gender, Parent_Education_Level, Attendance (%), etc.).")
             registrar_acao(nome_usuario, f"Erro de coluna não encontrada (KeyError): {ke}")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado durante o processamento: {e}")
            registrar_acao(nome_usuario, f"Erro inesperado: {e}")


# Adiciona uma mensagem se nenhum nome válido foi inserido ainda
elif nome_usuario_input is not None and not nome_valido and nome_usuario_input != "":
    # Este bloco é alcançado se o usuário digitou algo, mas era inválido.
    # A mensagem de aviso já foi mostrada dentro do bloco de validação.
    pass # Não precisa mostrar mais nada aqui.
else:
    # Este bloco é alcançado na primeira execução, antes do usuário digitar algo.
    st.info("Por favor, digite seu nome para iniciar a análise.")