#!/usr/bin/env python
# coding: utf-8

# ## Сегментация пользователей банка
# 
# источник датасета: https://www.kaggle.com
# 
# Описание проекта: В нашем распоряжении датасет, содержащий информацию о клиентах банка, располагающегося во Франции, Испании и Германии. Данные содержат следующую информацию:
# 
# `customer_id` — идентификатор пользователя,
# 
# `credit_score` — баллы кредитного скоринга,
# 
# `country` — страна,
# 
# `gender` — пол,
# 
# `age` — возраст,
# 
# `tenure` — количество объектов в собственности,
# 
# `balance` — баланс на счёте,
# 
# `products_number` — количество продуктов, которыми пользуется клиент,
# 
# `credit_card` — есть ли кредитная карта,
# 
# `active_member` — активный клиент,
# 
# `estimated_salary` — заработная плата клиента,
# 
# `churn` — клиент ушёл или нет (1-ушел, 0 - нет).

# Цель исследования: исследовательский анализ данных для составления портрета пользователя, склонного уходить и рекомендаций для продуктового менеджера по удержанию клиентов. 
# 
# Задачи исследования: 
# 1. Провести исследовательский анализ данных
# 2. Сегментировать пользователей на основе данных в разрезе различных атрибутов и провести сравнительный анализ

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns
import plotly.express as px
import warnings
warnings.filterwarnings('ignore') 


# In[2]:


bank = pd.read_csv('../bank/Bank Customer Churn Prediction.csv')


# In[3]:


bank.head()


# In[4]:


bank.info()


# В датасете 10000 строк, 12 колонок, нет нулевых значений. можно работать спокойно

# In[5]:


bank.nunique()


# Количество пользователей совпадает с кол-вом строк датасета, следовательно все пользователи уникальные.
# У одного не указана зарплата, может быть безработный.

#   

# Проведем EDA-анализ

# In[6]:


bank.describe()


# Проанализируем общие портреты клиентов:
# Возраст пользователей банка варьируется от 18 до 92 лет, но чаще всего от 32 до 44. Средний возраст ~39 лет, медианный - 37 лет. 
# Кредитные рейтинги - от 350 до 850.
# Зарплата клиента 11.6 - 199992.5, при этом средняя = 100090.239881, а 25 квантиль равен 51002.1, это очень интересно, и дальше мы посмотрим на распределение по зарплате на наличие выбросов

#   

# Построим боксплот для отображения выбросов в столбцах с возрастом, балансом на счёте и зарплатой

# In[7]:


for column in ['age', 'balance', 'estimated_salary']:
    plt.figure(figsize=(8, 3))
    sns.boxplot(x=column, data=bank)
    plt.show();


# Боксплот показал, что выбросами (данными, сильно отличающися от общего распределения) являются клиенты старше 62 лет.
# В остальных колонках выбросов не обнаружено.

# In[8]:


# создадим колонку с разделением возраста по категориям
# Т.к. мы выяснили что минимальный возраст клиента - 18 лет, начнем градацию от него.
bank['age_cathegory'] = pd.cut(bank.age, bins=(18,29,50,62, np.inf), 
                           labels=['18-29','30-45','46-62','Старше 62'])
bank


# In[9]:


# Визуализируем соотношение возрастных категорий
fig1,ax1 = plt.subplots()
df = bank.groupby('age_cathegory').agg({'customer_id': 'count'})
ax1.pie(df['customer_id'], labels=df.index, autopct='%1.1f%%')
ax1.set_title(f'Распределение клиентов по возрастным категориям')
plt.show()


# Основными клиентами банков являются люди возрастом от 30 до 45 лет. Что вполне логично, этот класт людей представляет основу рабочего населения с нуждами в банковских продуктов

# In[10]:


bank.drop(['customer_id', 'products_number'], axis=1).groupby('churn').mean()


# Можно отметить следующее:
# средний возраст ушедших клиентов примерно 44-45 лет;
# доля оттока у владельцев кредитных карт и тех, кто ей не пользуется, мало различаются.

# In[19]:


for column in ['age_cathegory','country','gender','credit_card','active_member']:
    plt.figure(figsize=(5,3))
    sns.countplot(data=bank, x=column, hue="churn")
    plt.title(f'Распределение клиентов по признаку {column}')
    plt.show()


# Вычислим некоторые показатели в процентах

# In[12]:


round(bank.groupby('age_cathegory').churn.value_counts(normalize=True)*100, 1)
# отток в % по возрастным категориям


# In[13]:


round(bank.groupby('country').churn.value_counts(normalize=True)*100, 1) 
# отток в % по странам


# In[14]:


round(bank.groupby('gender').churn.value_counts(normalize=True)*100, 1) 
# отток в % по странам


# - Наименьший отток у самой молодой категории (18-29 лет), наибольшей у категории 46-62 года, видимо условия банка для них становятся невыгодными и они уходят из банка.
# - Среди стран наибольший отток клиентов в Германии, а в Испании и Франции примерно одинаково.
# - Уходят из банка больше всего женщины

# In[15]:


sns.set_style("darkgrid")
column_list = ['country', 'gender', 'credit_card', 'tenure', 'products_number', 'churn']

fig, ax = plt.subplots(2, 3)
fig.set_size_inches(15, 6) 
fig.set_dpi(300)
for variable, subplot in zip(column_list, ax.flatten()):
    splot = sns.countplot(bank[variable], ax=subplot)
    for p in splot.patches:
        splot.annotate('{:.0f}'.format(p.get_height()), (p.get_x() + p.get_width()/2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 10), textcoords = 'offset points')
fig.suptitle("Количество клиентов");


# на графиках видим:
# 
# - Больше всего клиентов во Франции, в Германии и Испании примерно одинаково;
# - Мужчин немного больше чем женщин;
# - Владельцев кредитных карт значительно больше чем клиентов, не пользующихся картой;
# - У значительного количества клиентов по несколько объектов в собственности;
# - Большинство клиентов имеют 1,2 продукта банка, клиентов с 3 и 4-мя продуктами очень мало;
# - Отток довольно большой, около 20%.

# In[16]:


bank.drop('customer_id', axis=1).groupby('products_number').mean()


# Видим, что:
# - огромная доля оттока у людей, пользующихся 3-4 продуктами банка (83-100%), но в количественном значении их небольшое количество;
# - Средний возраст выше у этих клиентов больше, чем у остальных;
# 
# Построим распределения по количеству имеющихся банковских продуктов. 

# In[17]:


values = ['country', 'gender', 'tenure', 'credit_card', 'active_member', 'churn']

fig, ax = plt.subplots(2, 3)
fig.set_size_inches(15, 7) 
fig.set_dpi(300)

for variable, subplot in zip(values, ax.flatten()):
    splot = sns.countplot(data=bank, x=variable, hue='products_number', ax=subplot)
    for p in splot.patches:
        splot.annotate('{:.0f}'.format(p.get_height()), (p.get_x() + p.get_width()/2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 10), textcoords = 'offset points')
fig.suptitle("Количество клиентов по количеству имеющихся банковских  продуктов у клиентов");


# - Больше всего 1, 2 продуктами пользуются жители Франции, меньше всего с одним продуктом в Испании, а с 2 продуктами- в Германии. 3 и 4 продуктами везде пользуются мало.
# - 1 - 2 продуктами чаще пользуются мужчины, 3-4 женщины;
# - Пользователей. имеющих продукты и пользующихся кредитными картами, больше чем тем, у кого нет кредитных карт.
# - Активных и неактивных клиентов примерно одинаково.
# - Неушедших клиентов с 4 продуктами нет, а с 3 продуктами очень мало.

# ## Выводы
# 
# На основании проведенного анализа на данном этапе можно составить следующие портреты клиентов, которые уйдут с очень большой вероятностью:
# 
# - женщины;
# - клиенты в возрасте 44-45 лет;
# - проживают в Германии и Испании;
# - имеют большое количество продуктов, возможно это несколько кредитов, закрыв которые клиенты стремятся быстрее уйти из банка, возможно стоит пересмотреть условия для них.
# 
# Портрет более надежного клиента:
# - мужчины;
# - клиенты в возрасте до 44 лет;
# - клиенты регулярно совершающие активности в приложении банка;
# - пользователи двух продуктов банка.
# 
# ### Рекомендации:
# 
# 1. Поддерживать активность клиентов: привлекать клиентов к более активному использованию приложения/продуктов банка.
# 2. Предлагать дополнительные продукты клиентам с одним продуктом.
# 3. Пересмотреть условия услуг для клиентов от 46 лет и выше, провести акции по удержанию пользователей старших лет и женщин.
# 4. Клиенты с большим количеством продуктов склонны к оттоку, стоит разобраться и улучшить их качество.
# 5. Продолжить исследование в разрезе остальных показателей

# In[ ]:




