"""Sabor40
##SETUP INICIAL
### BIBLIOTECAS
"""
import pandas as pd
import numpy as np
import unicodedata
import matplotlib.pyplot as plt
import seaborn as sns

"""
Carregamento dos dados
"""

#carregando dados sorveteria
sorvete = pd.read_csv('C:/Users/Erik/Desktop/projeto-fatima/dadossabor40.csv', sep=',')

#Verificando  dataframe sorveteria
sorvete.head()

#Carregando dados clima
clima = pd.read_csv('C:/Users/Erik/Desktop/projeto-fatima/clima-outubro.csv', sep = ',')

#Verificando dataframe clima
clima.head()

#chegando dados
clima.info()
sorvete.info()

"""#Limpeza dos dataframes"""

#Verificando valores nulos
sorvete.isnull().sum()

clima.isnull().sum()

#Mudando valores nulos na coluna para Sem/Informação
clima['preciptype'] = clima['preciptype'].fillna('Sem/Informação')

clima['snowdepth'] = clima['snowdepth'].fillna(0)

clima.isnull().sum()

"""#Padronizando colunas"""

#padronizando colunas, espaços, minusculas, acentos, underline
def padronizar_colunas(df):
    """
    Padroniza nomes de colunas:
    - força tipo string
    - remove acentos
    - deixa minúsculas
    - substitui espaços e caracteres especiais por _
    """
    novas_colunas = []
    for col in df.columns.astype(str):
        # remover acentuação
        col_sem_acentos = ''.join(
            c for c in unicodedata.normalize('NFKD', col)
            if not unicodedata.combining(c)
        )
        # aplicar padronização geral
        col_limpa = (
            col_sem_acentos
            .strip()
            .lower()
            .replace(' ', '_')
            .replace('/', '_')
            .replace('.', '')
            .replace('-', '_')
        )
        novas_colunas.append(col_limpa)
    df.columns = novas_colunas
    return df

clima = padronizar_colunas(clima)
sorvete = padronizar_colunas(sorvete)

sorvete.head()

clima.head()

#verificando nome das colunas
clima.columns

#mapeando para mudança no nome das colunas em clima
rename_mapas = {
    'datetime' : 'data',
    'tempmax' : 'temp_max',
    'tempmin' : 'temp_min',
    'temp' : 'temp_med',
    'humidity' : 'umidade',
    'precip' : 'chuva_mm',
    'precipprob' : 'prob_chuva',
    'cloudcover' : 'nuvens_pct',
    'windspeed' : 'vento_kmh',
    'uvindex' : 'uv',
    'conditions' : 'condicoes',
    'icon' : 'icone',
    }
clima = clima.rename(columns=rename_mapas)

#selecionar colunas de interesse
colunas_interesse = [
    'data',
    'temp_max',
    'temp_min',
    'temp_med',
    'umidade',
    'chuva_mm',
    'prob_chuva',
    'nuvens_pct',
    'vento_kmh',
    'uv',
    'condicoes',
    'icone'
]
clima = clima[[c for c in colunas_interesse if c in clima.columns]].copy()

#converter data
clima['data'] = pd.to_datetime(clima['data'], errors='coerce').dt.date

#mapeando dias
dias_map = {'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
    'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
clima['dia_semana'] = pd.to_datetime(clima['data']).dt.day_name().map(dias_map)

#Criando nova coluna para dizer se choveu como boleean
def flag_chuva(row):
    texto = (row.get('condicoes') or '').lower()
    return (pd.notna(row.get('chuva_mm')) and row['chuva_mm'] > 0) or ('rain' in texto or 'chuva' in texto)

clima['chuveu'] = clima.apply(flag_chuva, axis=1)

#criando coluna com clima
def categorizar_clima(row):
  if row['chuveu']:
    return 'Chuva'
  #considerar ceu limpo ou baixa nebulosidade como sol
  n = row.get('nuvens_pct')
  if pd.notna(n) and n <= 30:
    return 'Sol'

  texto = (row.get('condicoes') or '').lower()
  if any(t in texto for t in ['clear', 'sunny', 'sol']):
    return 'Sol'
  return 'Nublado'

clima['clima_categoria'] = clima.apply(categorizar_clima, axis=1)

clima.head()

sorvete.head()

print(clima['data'].dtype)
print(sorvete['data'].dtype)

# converte e mantém o formato datetime64
clima['data'] = pd.to_datetime(clima['data'], errors='coerce')
sorvete['data'] = pd.to_datetime(sorvete['data'], dayfirst=True, errors='coerce')

# confirma tipos
print(clima['data'].dtype)
print(sorvete['data'].dtype)

#merge
df_final = pd.merge(sorvete, clima, on='data', how='left')

df_final.head()

#Verificar se há datas sem correspondência
df_final[df_final['temp_med'].isna()][['data', 'nome']].head(10)

#Conferir quantos dias tiveram match
print("Total linhas:", len(df_final))
print("Linhas com clima encontrado:", df_final['temp_med'].notna().sum())

#filtrando apenas outubro
df_final = df_final[df_final['data'].dt.month == 10]

df_final['data'].dt.month.unique()

df_final.to_csv("sorveteria_clima_outubro.csv", index=False, encoding="utf-8-sig")

import os
os.getcwd()

"""
Verificação para ter certeza no powerBI
"""

#garante tipos corretos
df_final['data'] = pd.to_datetime(df_final['data'], errors='coerce')
df_final['quantidade'] = pd.to_numeric(df_final['quantidade'], errors='coerce')

#filtrar só OUTUBRO
df_out = df_final[df_final['data'].dt.month == 10].copy()

#TOTAL ENTRADAS = somando positivos
total_entradas = df_out.loc[df_out['quantidade'] > 0, 'quantidade'].sum()

#TOTAL VENDAS = somando negativos
total_vendas = - df_out.loc[df_out['quantidade'] < 0, 'quantidade'].sum()

print("Total Entradas:", total_entradas)
print("Total Vendas:", total_vendas)

#verificando pct vendas
pct_vendas = total_vendas / total_entradas
print(round(pct_vendas * 100, 2))
pct_entrada = total_entradas / total_vendas
print(round(pct_entrada * 100, 2))

#Verificar se a coluna usada no Power BI está presente
df_final[['data', 'clima_categoria', 'quantidade']].head()

#Agrupar total de vendas por categoria de clima
vendas_por_clima = (
    df_final.groupby('clima_categoria')['quantidade']
    .sum()
    .sort_values(ascending=False)
)
print("Total de vendas por clima:")
print(vendas_por_clima)
print()

#Contar quantos dias há em cada categoria climática
dias_por_clima = (
    df_final[['data', 'clima_categoria']]
    .drop_duplicates(subset='data')
    .groupby('clima_categoria')
    .size()
)
print("Quantidade de dias por categoria de clima:")
print(dias_por_clima)

#Corrigir os sinais: transformar vendas negativas em positivas
df_final['vendas_abs'] = df_final['quantidade'].apply(lambda x: -x if x < 0 else 0)

#Agora somar novamente por clima
vendas_corrigidas = (
    df_final.groupby('clima_categoria')['vendas_abs']
    .sum()
    .sort_values(ascending=False)
)
print(vendas_corrigidas)
