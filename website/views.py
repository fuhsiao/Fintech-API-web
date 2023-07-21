import re
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Mapping_code, Invest_plan, Portfolios, Stocks, News
from . import db
import requests
import json
from random import randrange
from datetime import datetime, timedelta
from datetime import date as Datetime_date
from bs4 import BeautifulSoup
import time
import jieba
from sqlalchemy import and_, or_


views = Blueprint('views',__name__)


# ===================== Frontend page =====================

# 最新消息
@views.route('/index',methods= ['GET','POST'])
@login_required
def Index():
    now = datetime.now()
    timestamp = int(datetime.timestamp(now))
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"}
    res = requests.get('https://www.twse.com.tw/fund/BFI82U?response=json&dayDate=&weekDate=&monthDate=&type=day&_='+str(timestamp),headers=headers)
    # soup = BeautifulSoup(res.text,"html.parser")
    json_object = res.json()
    time.sleep(1)
    res2 = requests.get('https://www.twse.com.tw/exchangeReport/MI_MARGN?response=json&date=&selectType=&_='+str(timestamp),headers=headers)
    # soup2 = BeautifulSoup(res2.text,"html.parser")
    json_object2 = res2.json()
    

    return render_template("index.html", user = current_user, data = json_object, data2 = json_object2)


# 個股搜尋
@views.route('/stock',methods= ['GET','POST'])
@login_required
def Stock():
    stock_info = ""
    news_json = {"title":[],"link":[]}
    senti_object = {"sneutral":0,"spos":0,"sneg":0}
    if request.method == 'POST':
        stock_id = request.form.get('stock_id')
        meta = api_meta(stock_id)
        if meta !=0:
            stock_info = {  "nameZhTw":meta['meta']['nameZhTw'], 
                            "industryZhTw":meta['meta']['industryZhTw'],
                            "stock_id":meta['info']['symbolId'],
                            "stock_date":meta['info']['date'],
                            "priceHighLimit":meta['meta']['priceHighLimit'],
                            "priceLowLimit":meta['meta']['priceLowLimit']}
            
            res = requests.get('https://tw.stock.yahoo.com/quote/'+ str(stock_id)+'/news')
            
            # 爬個股新聞
            soup = BeautifulSoup(res.text,"html.parser")
            newsBox = soup.find_all('u', class_="StretchedBox")
            news = [x.find_parent("a") for x in newsBox]
            news_json = {"title":[],"link":[]}
            for i in news:
                news_json["title"].append(i.text)
                news_json["link"].append(i['href'])
            
            link = news_json["link"]
            result = News.query.filter_by(stockid=stock_id).all()

            rl = [x.url for x in result]

            for l in link:
                if l not in rl:
                    newsdate , content = get_news(l)
                    sentiScore = get_sentiScore(content)
                    news = News(url=l,date=datetime(int(newsdate[0]),int(newsdate[1]),int(newsdate[2]),0,0,0,0), senti= sentiScore,stockid = stock_id)
                    db.session.add(news)
                    db.session.commit()
            
            filterdate = Datetime_date.today() - timedelta(7)
            result2 = News.query.filter(and_(News.date >= filterdate,News.stockid ==stock_id)).all()
            sneutral = [ x.senti for x in result2 if x.senti == 0]
            spos = [ x.senti for x in result2 if x.senti == 1]
            sneg = [ x.senti for x in result2 if x.senti == -1]

            senti_object["sneutral"]=len(sneutral)
            senti_object["spos"]=len(spos)
            senti_object["sneg"]=len(sneg)
            


    return render_template("stock.html", user = current_user, stock_info = stock_info, news = news_json,senti= senti_object, zip =zip)

# 投資取向
@views.route('/target', methods=['GET','POST'])
@login_required
def Target():
    opCode = Mapping_code.query.filter(Mapping_code.category.in_(['op1','op2','op3'])).all()
    options = list(map(lambda Mapping_code:Mapping_code.serialize(),opCode))
    current_user.investplan = mapping_investplanText(current_user.investplan, options)
    user_plans = list(map(lambda Invest_plan:Invest_plan.serialize(Invest_plan.id),current_user.investplan))
    return render_template('target.html', user = current_user , options = options, user_plans = user_plans )    

# 投資組合
@views.route('/portfolio', defaults={'index':0})
@views.route('/portfolio/<index>')
@login_required
def Portfolio(index):
    user_portfolios = list(map(lambda Portfolios:Portfolios.serialize(Portfolios.id),current_user.portfolios))
    portfolio_index = user_portfolios[int(index)]['id']
    this_portfolio = Portfolios.query.filter_by(id=portfolio_index).first()
    
    current_portfolio = list(map(lambda Stocks:Stocks.serialize(),this_portfolio.selected_stocks))

    return render_template('portfolio.html', user = current_user, user_portfolios = user_portfolios, portfolio = current_portfolio, portfolio_index = index)

# 選股-個人推薦
@views.route('/picker-oneself')
@login_required
def Picker1():
    user_plans = list(map(lambda Invest_plan:Invest_plan.serialize(Invest_plan.id),current_user.investplan))
    user_portfolios = list(map(lambda Portfolios:Portfolios.serialize(Portfolios.id),current_user.portfolios))
    return render_template('picker-oneself.html', user = current_user,  user_plans = user_plans, portfolio = user_portfolios)

# 選股-自訂條件
# @views.route('/picker-cond')
# @login_required
# def Picker2():
#     return render_template('picker-cond.html', user = current_user)

# 風險評估
# @views.route('/risk-assessment')
# @login_required
# def Risk_assess():
#     return render_template('risk-assessment.html', user = current_user)

# 個人資料
@views.route('/account')
@login_required
def Set_account():
    return render_template('account.html', user = current_user)


# ===================== CRUD methods =====================

# 新增計畫 (Target)
@views.route('/add_newPlan', methods=['POST'])
@login_required
def add_newPlan():
    if request.method == 'POST':
        new_planName = request.form.get('new_planName')
        monthlyInvest = request.form.get('monthlyInvest')
        planTime = request.form.get('planTime')
        planRisk = request.form.get('planRisk')
        new_plan = Invest_plan(plan_name=new_planName, plan_monthly_invest=monthlyInvest, plan_time=planTime, plan_risk=planRisk, user_id=current_user.id)
        db.session.add(new_plan)
        db.session.commit()
        return redirect(url_for('views.Target'))
    return jsonify({})

# 刪除計畫 (Target)
@views.route('/delete_plan', methods=['POST'])
@login_required
def delete_Plan():
    plan_id = request.form.get('plan_id')
    plan = Invest_plan.query.get(plan_id)
    if plan.user_id == current_user.id:
        db.session.delete(plan)
        db.session.commit()
    return redirect(url_for('views.Target'))

# 新增投資組合 (Portfolio)
@views.route('/add_portfolio', methods=['POST'])
@login_required
def add_portfolio():
    if request.method == 'POST':
        portfolio_name = request.form.get('portfolio_name')
        new_portfolio = Portfolios(name=portfolio_name, user_id=current_user.id)
        db.session.add(new_portfolio)
        db.session.commit()
    return redirect(url_for('views.Portfolio'))

# 修改組合名稱 (Portfolio)
@views.route('/edit_portfolio_name', methods=['POST'])
@login_required
def edit_portfolio_name():
    if request.method == 'POST':
        portfolio_id = request.form.get('portfolio_id')
        portfolio_index = request.form.get('index')
        portfolio_newName = request.form.get('portfolio_newName')
        portfolio = Portfolios.query.get(portfolio_id)
        if portfolio.user_id == current_user.id:
            portfolio.name = portfolio_newName
            db.session.commit()
    return redirect(url_for('views.Portfolio', index=portfolio_index))
    
# 刪除投資組合 (Portfolio)
@views.route('/delete_portfolio', methods=['POST'])
@login_required
def delete_portfolio():
    if request.method == 'POST':
        portfolio_id = request.form.get('portfolio_id')
        portfolio = Portfolios.query.get(portfolio_id)
        if portfolio.user_id == current_user.id:
            db.session.delete(portfolio)
            db.session.commit()
    return redirect(url_for('views.Portfolio'))

# 新增股票 (Portfolio)
@views.route('/add_stock_by_id', methods=['POST'])
@login_required
def add_stock_by_id():
    if request.method == 'POST':
        stock_id = request.form.get('stock_id')
        stock = Stocks.query.get(stock_id)
        portfolio_index = request.form.get('index')
        portfolio_id = request.form.get('portfolio_id')
        this_portfolio = Portfolios.query.get(portfolio_id)
        if stock and (stock not in this_portfolio.selected_stocks): 
            this_portfolio.selected_stocks.append(stock)
            db.session.commit()
    return redirect(url_for('views.Portfolio',index=portfolio_index))

# 刪除股票 (Portfolio)
@views.route('/delete_stock',methods=['POST'])
@login_required
def delete_stock():
    if request.method == 'POST':    
        stock_id = request.form.get('stock_id')
        stock = Stocks.query.get(stock_id)
        portfolio_index = request.form.get('index')
        portfolio_id = request.form.get('portfolio_id')   
        this_portfolio = Portfolios.query.get(portfolio_id)
        if this_portfolio.user_id == current_user.id:
            this_portfolio.selected_stocks.remove(stock)
            db.session.commit()
    return redirect(url_for('views.Portfolio',index=portfolio_index))

# 投資組合 分頁路由 (Portfolio)
@views.route('/portfolio_index_router', methods=['POST'])
@login_required
def portfolio_index_router():
    portfolio_index = request.form['index']
    return redirect(url_for('views.Portfolio',index=portfolio_index))


# ===================== other methods =====================

# 取得 選項名稱 (by id)
def mapping_codeValue(id, options):
    for i in options:
        if id == i['id']:
            return i['name']
    return ""

# 取得 投資計畫 表格欄的對應名稱
def mapping_investplanText(plans, options):
    for i in plans:
        i.monInvest_text = mapping_codeValue(i.plan_monthly_invest, options)
        i.planTime_text = mapping_codeValue(i.plan_time, options)
        i.planRisk_text = mapping_codeValue(i.plan_risk, options)
    return plans


# ===================== getData from API =====================

# 取得組合內股票的 成交價、漲跌、漲跌幅 (Portfolio)
@views.route('/get_price_quotechange',methods=['POST'])
def get_Price_quoteChange():
    stock = json.loads(dict(request.form)['portfolio_stock'])
    for i in stock:
        a1 = api_dealts(i['stock_id'])
        a2 = api_quote(i['stock_id'])
        # set price、change、changePercent
        i['price'] = a1['price']
        i['change'] = a2['change']
        i['changePercent'] = a2['changePercent']
        # i['price'] = randrange(100)
        # i['change'] = randrange(10)
        # i['changePercent'] = randrange(100)
    return jsonify({'data':stock})

@views.route('/get_best_bid_ask',methods = ['POST'])
def get_Best_Bid_Ask():
    stock_id = json.loads(dict(request.form)['stock_id'])
    a1 = api_quote(stock_id)['order']
    bids = a1['bids']
    asks = a1['asks']
    result = []
    for i in range(5):
        result.append( {"bid_unit":bids[i]["volume"],
                        "bid_price":bids[i]["price"],
                        "ask_price":asks[i]["price"],
                        "ask_unit":asks[i]["volume"]})
    return jsonify({'data':result})

@views.route('/get_close_price',methods = ['POST'])
def get_Close_Price():
    stock_id = json.loads(dict(request.form)['stock_id'])
    a1 = api_chart(stock_id)
    return jsonify(a1)

# ===================== API - Digital Sandbox =====================

# api token
jwt ="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyMDI0IiwiaWF0IjoxNjU0NjU4MTY1LCJpc3MiOiIydUtBOE8xYU1iUUs2ZFpCT0M0UGpWRnJlOW9NWjM3byJ9.HFYDRUDYXM7kCqRa0iFUJzyNzCsmNHgLrHqHhQc9ybk"

# 最近一筆成交資料 - 價格、張數
def api_dealts(symbolId):
    url = "https://api.fintechspace.com.tw/realtime/v0.3/intraday/dealts"
    params = {
        "symbolId": symbolId,
        "apiToken": '4af7c90c0eac7cd5ee3d289f00045bbb',
        "oddLot": 'false',
        "limit": 1,
        "offset": 0,
        "jwt": jwt
    }
    response = requests.request("GET", url, params = params)
    return json.loads(response.text)['data']['dealts'][0]

# 盤中最佳五檔、統計資訊(OHLC)、漲跌(幅)
def api_quote(symbolId):
    url = "https://api.fintechspace.com.tw/realtime/v0.3/intraday/quote"
    params = {
        "symbolId": symbolId,
        "apiToken": '4af7c90c0eac7cd5ee3d289f00045bbb',
        "oddLot": 'false',
        "jwt": jwt
    }
    response = requests.request("GET", url, params = params)
    return json.loads(response.text)['data']['quote']

# 提供 股票基本資訊
def api_meta(symbolId):
    url = "https://api.fintechspace.com.tw/realtime/v0.3/intraday/meta"
    params = {
        "symbolId": symbolId,
        "apiToken": '4af7c90c0eac7cd5ee3d289f00045bbb',
        "oddLot": 'false',
        "jwt": jwt
    }
    response = requests.request("GET", url, params = params)
    if response.status_code!=200:
        return 0
    return json.loads(response.text)['data']

# 取得股票收盤價 圖資料
def api_chart(symbolId):
    url = "https://api.fintechspace.com.tw/realtime/v0.3/intraday/chart"
    params = {
        "symbolId": symbolId,
        "apiToken": '4af7c90c0eac7cd5ee3d289f00045bbb',
        "oddLot": 'false',
        "jwt": jwt
    }
    response = requests.request("GET", url, params = params)
    return json.loads(response.text)['data']['chart']['c']


def get_news(url):

    res = requests.get(url)
    soup = BeautifulSoup(res.text,"html.parser")

    time = soup.find("div",class_="caas-attr-time-style").find("time").text
    date = re.findall(r'\d+',time.split()[0])


    p = soup.find("div",class_="caas-body").find_all("p",text=True, recursive=False)

    content = ' '.join([i.text for i in p])

    return date ,content


def get_sentiScore(text):

    with open('website/dict/NTUSD_positive_unicode.txt', encoding='utf-8', mode='r') as f:
        positive_words = []
        for l in f:
            positive_words.append(l.strip())
    
    with open('website/dict/NTUSD_negative_unicode.txt', encoding='utf-8', mode='r') as f:
        negative_words = []
        for l in f:
            negative_words.append(l.strip())


    article = text
    score = 0
    jieba_result = jieba.cut(article, cut_all=False, HMM=True)
    for word in jieba_result:
        if word in positive_words:
            score += 1
        elif word in negative_words:
            score -= 1
        else:
            pass
    
    senti = 0
    if score > 3:
        senti = 1
    if score <0:
        senti = -1
    
    return senti
        
@views.route('/picker1_stock',methods=['POST'])
def picker_stock():
    stock = json.loads(dict(request.form)['type'])
    stock = str(stock)
    money_type = ['1']

    if '2' in stock:
        money_type.append('2')
    if '3' in stock:
        money_type.append('3')

    user_portfolios = list(map(lambda Portfolios:Portfolios.serialize(Portfolios.id),current_user.portfolios))
    result2 = Stocks.query.filter(and_(Stocks.t1.in_(money_type),Stocks.t3 == stock[-1])).all()
    
    t = []
    for i in result2:
        t.append({"stock_id":i.id,
                  "stock_name":i.name})

    return jsonify({"data":t})
    

    # 新增股票 從推薦
@views.route('/add_stock_picker', methods=['POST'])
def add_stock_pciker():
    if request.method == 'POST':
        stock_id = request.form.get('stockId')
        stock = Stocks.query.get(stock_id)
        portfolio_id = request.form.get('portfolio_id')
        this_portfolio = Portfolios.query.get(portfolio_id)
        if stock and (stock not in this_portfolio.selected_stocks): 
            this_portfolio.selected_stocks.append(stock)
            db.session.commit()
    return redirect(url_for('views.Picker1'))
 