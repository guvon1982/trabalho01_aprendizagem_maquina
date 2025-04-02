import os
import pandas as pd
import matplotlib.pyplot as plt


def solicitar_caminho_arquivo():
    while True:
        path = input("Digite o caminho do arquivo: ").strip()

        if not path:
            print("Erro: Você precisa digitar um caminho para o arquivo.")
            continue

        if not os.path.isfile(path):
            print(
                "Erro: Arquivo não encontrado. Verifique o caminho e tente novamente."
            )
            continue

        return path


# Solicitação do caminho do arquivo
df = pd.read_csv(solicitar_caminho_arquivo())

# Contagem de registros e gênero
total_count = df.shape[0]
gender_total = df["Gender"].value_counts()
total_female = gender_total.get("Female", 0)
total_male = gender_total.get("Male", 0)

print(
    f"Existem {total_count} registros no total, "
    f"sendo {total_female} pessoas do sexo feminino e {total_male} do sexo masculino."
)

# Removendo registros com valores nulos na coluna "Parent_Education_Level"
df.dropna(subset=["Parent_Education_Level"], inplace=True)

# Preenchendo valores nulos da coluna "Attendance (%)" com a mediana
mediana_attendance = df["Attendance (%)"].median()
df["Attendance (%)"].fillna(mediana_attendance, inplace=True)

total_attendance = df["Attendance (%)"].sum()
print(f"Total de presença: {total_attendance}")

# Listagem de colunas do dataset
columns = df.columns.to_list()

while True:
    chosen_column = input(
        "Escolha uma das colunas da lista a seguir "
        f"para visualizar a média, mediana, moda e desvio padrão: {columns}\n"
    ).strip()

    if chosen_column not in columns:
        print("Erro: A coluna escolhida não existe no dataset.")
        continue

    if not pd.api.types.is_numeric_dtype(df[chosen_column]):
        print("Erro: A coluna escolhida não contém valores numéricos.")
        continue

    media = df[chosen_column].mean().round(2)
    mediana = df[chosen_column].median()
    moda = df[chosen_column].mode().tolist()
    desvio_padrao = df[chosen_column].std()

    print(
        f"Segue dados da coluna '{chosen_column}':\n"
        f"Média: {media}\nMediana: {mediana}\nModa: {moda}\nDesvio Padrão: {desvio_padrao}"
    )
    break
