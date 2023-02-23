#!/usr/bin/env python
# coding: utf-8

# # Visualização de Dados e Informações - Prática #01
# 
# - Daniel Vieira Batista
# - RA: 11106614

# - Dependências:

# In[3]:


import pandas as pd
import numpy as np
import seaborn as sb
import plotly as ply
from matplotlib import pyplot as plt


# - Leitura dos dados

# In[6]:


df_vendas = pd.read_csv("VIS_Pr_01_Vendas.csv", sep=",", decimal=".", encoding="latin-1")


# In[9]:


df_vendas.head(2)


# In[34]:


df_vendas.shape


# In[10]:


df_vendas.head(3).T


# In[13]:


df_vendas.info()


# ------------------

# ### Q1
# 
# Q1. (2,0) Segundo seu chefe, o pessoal de Vendas adora Excel. Assim, eles gostariam de receber um CSV para
# contrastar Sales X Profit segmentado por Region, destacando qual a media de Discount aplicado.

# - Quais são as regiões possíveis e suas volumetrias?

# In[16]:


df_vendas.Region.value_counts(dropna=False, normalize=False)


# - Criando a função que fará a agregação:

# In[45]:


def agg_func(g):
    
    dictResult = {}
    
    dictResult['sales_total'] = g["Sales"].sum()
    dictResult['quantity_total'] = g["Quantity"].sum()
    dictResult['discount_mean'] = g["Discount"].mean()
    dictResult['discount_median'] = g["Discount"].median()
    dictResult['discount_std'] = g["Discount"].std()
    dictResult['discount_max'] = g["Discount"].max()
    dictResult['discount_min'] = g["Discount"].min()
    
    return pd.Series(dictResult)


# In[46]:


get_ipython().run_cell_magic('time', '', 'df_agg = df_vendas.groupby(by=["Region"], as_index=False, axis=0, dropna=False, observed=False, sort=True).apply(agg_func)')


# - <b>Resposta:</b>

# In[47]:


df_agg


# In[88]:


# O resultado com os dados ficará disponível com o nome "dados_vendas.csv"
df_agg.to_csv("dados_vendas.csv", sep=";", decimal=".")


# ------------------

# ### Q2
# 
# Q2. (4,0) Ja para o pessoal de marketing de produto, seu chefe indicou que eles gostariam de uma visão de Profit acumulado por ano (Order Date) para cada um das sub-categorias de produto (Sub-Category). Marketing adora um gráfico de barras! Voce pode usar a bilioteca matplotlib ou seaborn.
Profit, Order Date, Sub-Category
# - Quantos anos distintos temos?

# In[48]:


# Vamos converter para data para ficar mais fácil de trabalhar
df_vendas['Order Date'] = pd.to_datetime(df_vendas['Order Date'], format="%m/%d/%Y", errors="coerce")


# In[49]:


# Criando as variáveis de dia, mês e ano
df_vendas['day'] = df_vendas['Order Date'].apply(lambda e: e.day)
df_vendas['month'] = df_vendas['Order Date'].apply(lambda e: e.month)
df_vendas['year'] = df_vendas['Order Date'].apply(lambda e: e.year)


# In[50]:


df_vendas['year'].value_counts()


# - Os dados de profit fazem sentido:

# In[80]:


df_vendas.Profit.describe()


# - Quantas subcategorias temos?
#     - Temos mais categorias do que anos distintos, isso influencia no nosso plot;

# In[51]:


df_vendas['Sub-Category'].value_counts(dropna=False, normalize=False)


#          

# - Gerando função de agregação:

# In[64]:


def agg_func_2(g):
    
    dictResult = {}
    
    g = g.sort_values(by=['year'], ascending=True)
    dictResult['year'] = int(g["year"].iat[0])
    
    dictResult['profit_sum'] = g["Profit"].sum()
    
    return pd.Series(dictResult)


# In[65]:


get_ipython().run_cell_magic('time', '', 'df_agg2 = df_vendas.groupby(by=["Sub-Category", "year"], as_index=False, axis=0,\n                            dropna=False, observed=False, sort=True, group_keys=False).apply(agg_func_2)\n\ndf_agg2.year = df_agg2.year.astype(int)\n\ndf_agg2.head()')


# In[72]:


def agg_func_3(g):
    
    dictResult = {}
    
    dictResult['sub_category'] = g["Sub-Category"]
    dictResult['year'] = g["year"]
    dictResult['profit_sum'] = g["profit_sum"]
    dictResult['profit_cumsum'] = g["profit_sum"].cumsum()
    
    return pd.DataFrame(dictResult)

df_agg3 = df_agg2.groupby(by=["Sub-Category"], as_index=False, axis=0,
                            dropna=False, observed=False, sort=True).apply(agg_func_3)


# In[74]:


df_agg3.head(5)


# - Plot resposta:

# In[87]:


sb.catplot(data=df_agg3, 
           col="sub_category", 
           x="year", 
           y="profit_cumsum", 
           height=5, 
           kind="bar",
           orient="v",
           legend=True,
           sharey=False,
           sharex=False,
           margin_titles=True,
           col_wrap=3)


# In[89]:


# O resultado com os dados ficará disponível com o nome "dados_vendas.csv"
df_agg3.to_csv("dados_marketing.csv", sep=";", decimal=".")


# ------------------

# ### Q3
# 
# Q3. (4,0) Por fim, o pessoal do financeiro gostariam de receber um CSV com a quantidade de consumidores por
# classe de performance das vendas e Segment do consumidor.

# In[90]:


df_vendas.head(3)


# In[91]:


df_vendas.head(3).T


# - Temos muitos consumidores que fizeram mais de um consumo:

# In[92]:


df_vendas["Customer ID"].value_counts()


# - Tipos de segmento e suas volumetrias:

# In[102]:


df_vendas["Segment"].value_counts()


#         

# - Classe de Performance:

# In[93]:


def class_perf(row):
    r = row["Profit"]/(row["Sales"]-row["Discount"])
    return r


# In[96]:


df_vendas["class_perf"] = df_vendas.apply(class_perf, axis=1)


# In[97]:


df_vendas["class_perf"].describe()


# In[98]:


df_vendas[["Profit","Sales","Discount","class_perf"]].head()


# In[101]:


def class_perf_label(v):
    
    if v <= 0.1:
        return "E"
    elif v <= 0.15:
        return "D"
    elif v <= 0.2:
        return "C"
    elif v <= 0.25:
        return "B"
    elif v > 0.25:
        return "A"
    else:
        return "F"
    
df_vendas["class_perf_label"] = df_vendas.class_perf.apply(class_perf_label)


#         

# - Pivotando com agregação:

# In[104]:


df_result = df_vendas.pivot_table(values="Customer ID",index=["class_perf_label"], columns=["Segment"], aggfunc="count")


# In[112]:


df_result


# In[115]:


df_result.sum()


# In[114]:


df_result.sum().sum()


# In[117]:


df_vendas.shape


# - Resultado:

# In[119]:


# O resultado com os dados ficará disponível com o nome "dados_vendas.csv"
df_result.to_csv("dados_financeiro.csv", sep=";", decimal=".")


#         
