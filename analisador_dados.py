import pandas as pd
import os
import matplotlib.pyplot as plt

def carregar_dados():
    """
    Carrega dados de um arquivo CSV ou JSON para um DataFrame do Pandas.

    Pergunta ao usuário o caminho do arquivo e tenta carregá-lo.
    Suporta arquivos nos formatos CSV e JSON.

    Returns:
        pandas.DataFrame or None: Um DataFrame contendo os dados carregados,
                                     ou None se ocorrer algum erro.
    """
    while True:
        caminho_arquivo = input("Por favor, digite o caminho do arquivo (CSV ou JSON): ")
        if not os.path.exists(caminho_arquivo):
            print("Erro: O caminho do arquivo especificado não existe.")
            continue
        try:
            if caminho_arquivo.lower().endswith('.csv'):
                df = pd.read_csv(caminho_arquivo)
                print("Arquivo CSV carregado com sucesso!")
                return df
            elif caminho_arquivo.lower().endswith('.json'):
                df = pd.read_json(caminho_arquivo)
                print("Arquivo JSON carregado com sucesso!")
                return df
            else:
                print("Erro: Formato de arquivo não suportado. Por favor, use um arquivo CSV ou JSON.")
                continue
        except pd.errors.EmptyDataError:
            print("Erro: O arquivo está vazio.")
        except pd.errors.ParserError:
            print("Erro: Falha ao analisar o arquivo. Verifique se o formato está correto.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
        return None

def analisar_dados_basico(df):
    """
    Realiza uma análise básica do DataFrame fornecido.

    Exibe a quantidade total de dados, a distribuição por gênero
    e a quantidade de registros sem informação sobre a educação dos pais.

    Args:
        df (pandas.DataFrame): O DataFrame a ser analisado.
    """
    if df is not None:
        total_registros = len(df)
        quantidade_generos = df['Gender'].value_counts()
        registros_sem_educacao_pais = df['Parent_Education_Level'].isnull().sum()

        print("\n--- Análise Básica dos Dados ---")
        print(f"Quantidade total de registros carregados: {total_registros}")
        print("\nDistribuição por gênero:")
        print(quantidade_generos)
        print(f"\nQuantidade de registros sem informação sobre a educação dos pais (Parent_Education_Level): {registros_sem_educacao_pais}")
    else:
        print("Erro: Nenhum dado carregado para analisar.")

def limpar_dados(df):
    """
    Realiza a limpeza dos dados do DataFrame.

    Remove registros com valores nulos na coluna 'Parent_Education_Level'
    e preenche valores nulos na coluna 'Attendance (%)' com a mediana.

    Args:
        df (pandas.DataFrame): O DataFrame a ser limpo.

    Returns:
        pandas.DataFrame: O DataFrame com os dados limpos.
    """
    if df is not None:
        df_limpo = df.dropna(subset=['Parent_Education_Level']).copy()
        print(f"\nRegistros removidos devido à falta de informação na educação dos pais: {len(df) - len(df_limpo)}")

        mediana_attendance = df_limpo['Attendance (%)'].median()
        df_limpo['Attendance (%)'] = df_limpo['Attendance (%)'].fillna(mediana_attendance)
        print(f"Valores nulos na coluna 'Attendance (%)' preenchidos com a mediana: {mediana_attendance:.2f}%")

        soma_attendance = df_limpo['Attendance (%)'].sum()
        print(f"Somatório da coluna 'Attendance (%)': {soma_attendance:.2f}%")

        return df_limpo
    else:
        print("Erro: Nenhum dado carregado para limpar.")
        return None

def consultar_dados_coluna(df):
    """
    Permite ao usuário consultar estatísticas de uma coluna numérica específica do DataFrame
    selecionando por número. Reexibe as opções em caso de erro.

    Lista as colunas numéricas disponíveis com um número correspondente e solicita
    ao usuário o número da coluna para análise. Calcula e exibe as estatísticas.

    Args:
        df (pandas.DataFrame): O DataFrame para consulta.
    """
    if df is not None:
        colunas_numericas = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        if not colunas_numericas:
            print("\nNão há colunas numéricas disponíveis para análise.")
            return

        while True:
            print("\n--- Colunas numéricas disponíveis para análise ---")
            for i, col in enumerate(colunas_numericas):
                print(f"{i + 1}. {col}")
            print("0. Sair")

            opcao = input("\nDigite o número da coluna para análise: ")
            if opcao == '0':
                break
            try:
                indice_coluna = int(opcao) - 1
                if 0 <= indice_coluna < len(colunas_numericas):
                    nome_coluna = colunas_numericas[indice_coluna]
                    print(f"\n--- Estatísticas da coluna '{nome_coluna}' ---")
                    print(f"Média: {df[nome_coluna].mean():.2f}")
                    print(f"Mediana: {df[nome_coluna].median():.2f}")
                    print(f"Moda: {df[nome_coluna].mode().tolist()}")
                    print(f"Desvio Padrão: {df[nome_coluna].std():.2f}")
                else:
                    print("Erro: Opção inválida. Por favor, digite um número da lista ou 0 para sair.")
            except ValueError:
                print("Erro: Por favor, digite um número inteiro.")
    else:
        print("Erro: Nenhum dado carregado para realizar a consulta.")

def gerar_grafico_dispersao(df):
    """
    Gera um gráfico de dispersão entre as horas de sono e a nota final.

    Args:
        df (pandas.DataFrame): O DataFrame contendo os dados.
    """
    if df is not None and 'Sleep_Hours_per_Night' in df.columns and 'Final_Score' in df.columns:
        plt.figure(figsize=(10, 6))
        plt.scatter(df['Sleep_Hours_per_Night'], df['Final_Score'])
        plt.title('Gráfico de Dispersão: Horas de Sono vs. Nota Final')
        plt.xlabel('Horas de Sono por Noite')
        plt.ylabel('Nota Final')
        plt.grid(True)
        plt.show()
    else:
        print("Erro: Colunas 'Sleep_Hours_per_Night' ou 'Final_Score' não encontradas para o gráfico de dispersão.")

def gerar_grafico_barras_idade_media_nota(df):
    """
    Gera um gráfico de barras da idade versus a média das notas intermediárias (midterm_Score).

    Args:
        df (pandas.DataFrame): O DataFrame contendo os dados.
    """
    if df is not None and 'Age' in df.columns and 'Midterm_Score' in df.columns:
        media_notas_por_idade = df.groupby('Age')['Midterm_Score'].mean().sort_index()
        plt.figure(figsize=(10, 6))
        plt.bar(media_notas_por_idade.index, media_notas_por_idade.values)
        plt.title('Gráfico de Barras: Idade vs. Média das Notas Intermediárias')
        plt.xlabel('Idade')
        plt.ylabel('Média da Nota Intermediária')
        plt.xticks(media_notas_por_idade.index)
        plt.grid(axis='y', linestyle='--')
        plt.show()
    else:
        print("Erro: Colunas 'Age' ou 'Midterm_Score' não encontradas para o gráfico de barras.")

def gerar_grafico_pizza_idades(df):
    """
    Gera um gráfico de pizza para a distribuição das idades em grupos.

    Grupos de idade: até 17; 18 a 21; 22 a 24; 25 ou mais.

    Args:
        df (pandas.DataFrame): O DataFrame contendo os dados.
    """
    if df is not None and 'Age' in df.columns:
        bins = [0, 17, 21, 24, float('inf')]
        labels = ['Até 17', '18 a 21', '22 a 24', '25 ou mais']
        df['Grupo_Idade'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
        distribuicao_idades = df['Grupo_Idade'].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(distribuicao_idades, labels=distribuicao_idades.index, autopct='%1.1f%%', startangle=140)
        plt.title('Gráfico de Pizza: Distribuição das Idades')
        plt.axis('equal')
        plt.show()
    else:
        print("Erro: Coluna 'Age' não encontrada para o gráfico de pizza.")

def gerar_graficos(df):
    """
    Apresenta um menu para o usuário escolher qual gráfico gerar.

    Args:
        df (pandas.DataFrame): O DataFrame contendo os dados.
    """
    if df is not None:
        while True:
            print("\n--- Opções de Gráficos ---")
            print("1. Gráfico de Dispersão: Horas de Sono vs. Nota Final")
            print("2. Gráfico de Barras: Idade vs. Média das Notas Intermediárias")
            print("3. Gráfico de Pizza: Distribuição das Idades")
            print("0. Voltar ao menu principal")

            opcao = input("Digite o número do gráfico desejado: ")

            if opcao == '1':
                gerar_grafico_dispersao(df)
            elif opcao == '2':
                gerar_grafico_barras_idade_media_nota(df)
            elif opcao == '3':
                gerar_grafico_pizza_idades(df)
            elif opcao == '0':
                return  # Retorna ao menu principal
            else:
                print("Opção inválida. Por favor, digite um número da lista.")
    else:
        print("Erro: Nenhum dado carregado para gerar gráficos.")

if __name__ == '__main__':
    dados = carregar_dados()
    if dados is not None:
        print("\nPrimeiras linhas dos dados carregados:")
        print(dados.head())
        analisar_dados_basico(dados)  # Exibe a análise básica
        dados_limpos = limpar_dados(dados.copy())
        if dados_limpos is not None:
            print("\nPrimeiras linhas dos dados limpos:")
            print(dados_limpos.head())

            while True:
                print("\n--- Menu Principal ---")
                print("1. Consultar dados por coluna")
                print("2. Gerar gráficos")
                print("0. Encerrar o programa")

                opcao_principal = input("Digite o número da opção desejada: ")

                if opcao_principal == '1':
                    consultar_dados_coluna(dados_limpos)
                elif opcao_principal == '2':
                    gerar_graficos(dados_limpos)
                elif opcao_principal == '0':
                    print("Encerrando o programa.")
                    break
                else:
                    print("Opção inválida. Por favor, digite um número da lista.")