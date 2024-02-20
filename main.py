#---------------------------------------------------------------------------------------
#----   Цены Bid и Offer по одной ценной бумаге (по любому режиму торгов) 
#----   Код ценной бумаги на бирже (не ISIN !!!)
#---------------------------------------------------------------------------------------
def micex_get_sec_price(p_code):
	import pandas as pd
	#-----   Выгружаем данные с сайта биржи в формате JSON -----
	url = f'https://iss.moex.com/iss/engines/stock/markets/bonds/securities/{p_code}.json?iss.only=marketdata'
	data = pd.read_json(url)
	#---- преобразуем данные в нормальный фрейм -----
	data = pd.DataFrame(data=data.iloc[1, 0], columns=data.iloc[0, 0])
	#-----  Фильтруем только нужные секции   ----
	res = data[( data["BOARDID"] == 'TQOB') | (data["BOARDID"] == 'TQCB') | (data["BOARDID"] == 'TQOD') | (data["BOARDID"] == 'TQIR') | (data["BOARDID"] == 'TQOY')]
	#----  Выгрузка данных (для тестрования)
	res.to_csv("price.csv", sep=';')
	if len(res.index)>0:
		#-- BID
		bid = res['BID'].iloc[0]
		#-- OFFER
		offer = res['OFFER'].iloc[0]
		ret = bid, offer
	else:
		ret = 0,0
	return ret

#=======================================================================================
#=======================================================================================
#======    Главная процедура    ========================================================
#=======================================================================================
#=======================================================================================
#---------  Параметры   -----
#fi = 'SU26237RMFS6'	# ОФЗ
#fi = 'RU000A103WB0'	# Славянск
#fi = 'RU000A105KU0'     # Замещающие
#fi = 'RU000A104Z71'
sec_bid, sec_offer=micex_get_sec_price('RU000A105KU0')
#sec_bid, sec_offer=micex_get_sec_price('4554')
if sec_bid  == 0 or sec_offer == 0:
	print('Цен нет !')
else:
	print("sec_bid:   " + str(sec_bid))
	print("sec_offer: " + str(sec_offer))


