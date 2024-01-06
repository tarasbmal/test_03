import pandas as pd
import numpy as np 
import datetime 
from pyxirr import xirr
import streamlit as st
#----------------------------------------------------------------------
#----------------------------------------------------------------------
#-------   Процедура получения данных по облигации с сайта smart-lab.ru
#----------------------------------------------------------------------
#----------------------------------------------------------------------
def get_fi_data(p_isin):
    import requests
    from bs4 import BeautifulSoup
    #---- Инициализируем переменные ----
    fi_name = ""
    fi_mat = ""
    fi_offer = ""
    fi_nominal = ""
    fi_nkd = ""
    fi_price = ""
    coup = ""
    #-----------------------------------
    #https://www.moex.com/ru/issue.aspx?board=TQCB&code=RU000A0ZYEB1&utm_source=www.moex.com/#/bond_4
    url = 'https://smart-lab.ru/q/bonds/' + p_isin
    hdr={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}
    response = requests.get(url=url,stream=True, headers=hdr, verify=False)
    st_code = response.status_code
    if st_code != 200:
        return 0, fi_name, fi_mat, fi_offer, fi_nominal, fi_nkd, fi_price,  ""    #-- облигация не найдена
    tabs = pd.read_html(response.text)
    #--------------------------------
    #-----   Купоны -----------------
    #--------------------------------
    #df = tabs[0]
    #coup = df[["Дата купона","Купон"]]  #-- Оставим только нужные колонки
    #coup.columns = ["cd","amounts"] #-- переименуем столбцы
    #coup["dates"] = datetime.datetime.today()   #-- Новый столбец даты
    #for index,row in coup.iterrows():
    #    coup['dates'][index] = datetime.datetime.strptime(coup['cd'][index], "%d-%m-%Y")
    #coup = coup[["dates","amounts"]]    #-- оставляем только нужные поля
    #---------------------------------------------------------
    #-----------  Поиск параметров облигации ----------------------
    #---------------------------------------------------------
    soup = BeautifulSoup(response.text, "html.parser")  
    divs = soup.find_all("div")
    #---------  Флаги ---------------
    flag_name = 0
    flag_mat = 0 
    flag_offer = 0
    flag_nominal = 0
    flag_nkd = 0
    flag_price = 0
    #--------  Цикл для извлечения параметров ----  
    for div in divs:
        if div.get("class") == ['quotes-simple-table__item']:
            dtext = div.text.strip()
            #-------------------------------------------
            if flag_name == 1:
                flag_name = 0
                fi_name = dtext
                print(fi_name)
            if flag_mat == 1:
                flag_mat = 0
                fi_mat = dtext
            if flag_offer == 1:
                flag_offer = 0
                fi_offer = dtext
            if flag_nominal == 1:
                flag_nominal = 0
                fi_nominal = dtext
            if flag_nkd == 1:
                flag_nkd = 0
                fi_nkd = dtext
                fi_nkd = fi_nkd.split()[0]
            if flag_price == 1:
                flag_price = 0
                fi_price = dtext[0:-1]  #убираем знак %
            #--------------------------------------
            if dtext == "Имя облигации":
                flag_name = 1
            if dtext == "Дата погашения":
                flag_mat = 1
            if "Дата оферты" in dtext:
                flag_offer = 1
            if dtext == "Номинал":
                flag_nominal = 1
            if "НКД" in dtext:
                flag_nkd = 1
            if "Котировка облигации" in dtext:
                flag_price = 1
            #------------------------------------
    return 1, fi_name, fi_mat, fi_offer, fi_nominal, fi_nkd, fi_price, coup    #-- успешное завершение, облигация найдена
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

#----------------------------------------------------
#----------------------------------------------------
#-------  Главный модуль ----------------------------        
#----------------------------------------------------
#----------------------------------------------------
isin = "RU000A103RT2"
isin = st.text_input("ISIN", value=isin)
#-----------------------------------------------------------------------------------------
button1 = st.button("Получить данные по облигации")
if st.session_state.get('button') != True:
    st.session_state['button'] = button1 # Saved the state
if st.session_state['button'] == True:
    #--------  получаем данные по облигации ---
    ret, fi_name, fi_mat, fi_offer, fi_nominal, fi_nkd, fi_price, pl = get_fi_data(isin)
    #st.text("=====================================================================")
    if ret == 0:
        st.text("Не найдены данные по облигации ISIN: " + isin + " !!!")
    else:
        #----------------  Результаты работы -------------
        st.title(fi_name)
        st.text("Дата погашения: " + fi_mat)
        st.text("Дата оферты: " + fi_offer)
        st.text("Номинал: " + fi_nominal)
        st.text("НКД: " + fi_nkd)
        #st.text("=====  Цена =====" + fi_price)
        #st.text("=====  Купоны =====")
        #st.text(pl)
        #st.text(pl.dtypes)
        #------- Вводим параметры расчета -------
        price = float(fi_price)
        price = st.number_input("\bold Цена покупки, %", value=price)
        use_offer = "Погашения"
        if fi_offer != '—':
            use_offer = st.radio("Рассчитывать до даты",["Оферты","Погашения"])            
        #use_nalog = st.radio("Учитывать подоходный налог 13% ?",["Да, учитывать","Нет, не учитывать"])
        use_nalog = st.checkbox('Учитывать подоходный налог 13%', value=True)
        button1 = st.button("Рассчитать доходность")
        if button1:
            #---------   Вычисляем парамеры в нужном формате 
            f_buydate = datetime.datetime.today().date()
            f_buysum = (float(fi_nominal)*price/100+float(fi_nkd))
            if use_offer == 'Оферты':
                f_enddate = datetime.datetime.strptime(fi_offer, "%d-%m-%Y")
            else:
                f_enddate = datetime.datetime.strptime(fi_mat, "%d-%m-%Y")
            f_endsum = float(fi_nominal)    
            #---------   Добавляем налог с купонов ---
            if use_nalog:
                for index,row in pl.iterrows():
                        pl.loc[len(pl.index)] = [pl['dates'][index],round(pl['amounts'][index]*(-0.13),2)]
                #--- если купили дешевле, то еще в конце срока
                if f_buysum < f_endsum:
                    pl.loc[len(pl.index)] = [f_enddate,round((f_endsum-f_buysum)*(-0.13),2)]                              
            #---------   Добавляем покупку  -----------
            pl.loc[len(pl.index)] = [f_buydate, f_buysum*(-1)]
            #---------   Добавляем погашение -----
            pl.loc[len(pl.index)] = [f_enddate,f_endsum]
            #-------  Запуск расчета ------
            rrr = xirr(pl)
            st.title("Доходность: " + str(round(rrr*100,2)) + " %")
            st.text("Подробности расчета")
            #st.text(pl.sort_values(by=['dates']))
            st.text(pl)
    #st.text("=====================================================================")


