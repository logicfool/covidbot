#from db import *
#user1 = users
from db import *
from pyrogram import *
import pyrogram
#from pyrogram import Client,Filters
import json
import requests as r
from newsapi import *
import random
import logging as py_log
import schedule
py_log.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=py_log.INFO)
logger = py_log.getLogger()
logger.setLevel(py_log.INFO)
from threading import *
import time
import re

bot = Client("covid19bot")
newsapi_key = '' #your ews api key here!
newsapi = NewsApiClient(api_key=newsapi_key)
groupsinf = {}
userinf = {}
bot.start()
username = "@"+str(bot.get_me().username)
bot.stop()
n = "n" #A variable to be passed if you want to ignore the column in databasse update
admins = [401643149,827414826]
news = {}
news_countries = []
user_query={}
def news_q(_,query):
    a = query.data.split(":")
    if a[0] == 'news':
        user_query[str(query.from_user.id)+"_2"] = query.data
        return True
    else:
        return False

def stats_q(_,query):
    a = query.data
    if "stats" in a:
        return True
    else:
        return False
def news_r(_,query):
    a = query.data.split(":")
    if a[0] == "get_news":
        return True
    else:
        return False
def deletenow(_,query):
    a = query.data
    if "exitnow" in a:
        return True
    else:
        return False
def group_a_news(_,query):
    a = query.data.split(":")
    if a[0] == 'g':
        return True
    else:
        return False
def user_a_news(_,query):
    a = query.data.split(":")
    if a[0] == 'u':
        return True
    else:
        return False
def add_a_country(_,query):
    a = query.data.split(":")
    if a[0] == "acountry":
        return True
    else:
        return False

def del_a_country(_,query):
    a = query.data.split("|") #to add a country it will be added in this format in db eg c = "in:India,us:United States Of America" so we first split with , then again split with : added filters make a query handler now for ad and remove country
    if a[0] == 'delc':
        return True
    else:
        return False
def autonewsdelete(_,query):
    a= query.data
    if "autonewsdelete" in a:
        return True
    else:
        return False
# for g is group and u is user in callback query handler using split seee add an country callback data
news_filter = Filters.create(news_q)
stats_filter = Filters.create(stats_q)
news_return_filter = Filters.create(news_r)
delete_filter = Filters.create(deletenow)
gauto_filter = Filters.create(group_a_news)
uauto_filter = Filters.create(user_a_news)
add_country_filter = Filters.create(add_a_country)
del_country_filter = Filters.create(del_a_country)
autonewsdelete_filter = Filters.create(autonewsdelete)
#---------------------------------------------------------
def update_the_news():
    print("\n\n\n\n\n\nStarting to update news\n\n\n\n\n\n\n\n")
    global news
    if news_countries:
        for a in news_countries:
            try:
                data = newsapi.get_top_headlines(q='corona',language='en',country = '{}'.format(a))
                data = data['articles']
            except:
                return False
            no = int(news[str(a)])
            m = 0
            del news[str(a)]
            while m <= no:
                try:
                    del news[str(a)+"_{}_title".format(m)]
                    del news[str(a)+"_{}_desc".format(m)]
                    del news[str(a)+"_{}_url".format(m)]
                except:
                    pass
                m = m+1
            p = len(data) - 1
            news[str(a)] = p
            m = 0
            for d in data:
                news["{}_{}_title".format(str(a),str(m))] = d['title']
                news["{}_{}_desc".format(str(a),str(m))] = d['description']
                news["{}_{}_url".format(str(a),str(m))] = d['url']
                m = m+1
    print("\n\n\n\n\n\nCompleted Updating News\n\n\n\n\n\n")


def auto_news():
    print("Starting Auto News")
    global news_countries
    global news
    a = db.query("Select * from autonews where ison = 1")
    r = a.fetchall()
    print("Fetched Everything")
    keyboard =[]
    keyboard.append([InlineKeyboardButton("Ok got it !",callback_data= "autonewsdelete")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    for a in r:
        chat_id = a[1]
        c = a[3]
        print("cc :",c)
        if c and ((c!='') or (c!=None)):
            d = c.split(",")
            print("d: ",d)
            if (d!= '') or (d!= []) or (d!=None):
                for coun in d:
                    if coun != '':
                        e = coun.split(":")
                        print("E: ",e)
                        country = e[0]
                        name = e[1]
                        text = '**News of {}**\n\n'.format(name)
                        if country in news_countries:
                            print("Country: ",country)
                            no = int(news[str(country)])
                            m = 0
                            while m <= no:
                                n = m+1
                                title = news["{}_{}_title".format(str(country),str(m))]
                                url = news["{}_{}_url".format(str(country),str(m))]
                                text = text+"{}. [{}]({})\n".format(n,title,url)
                                m = m+1
                            print("The while Part")
                            bot.send_message(chat_id = chat_id,text = text,reply_markup = reply_markup)
                        else:
                            try:
                                print("Try Part")
                                data = newsapi.get_top_headlines(q='corona',language='en',country = '{}'.format(country))
                                data = data['articles']
                                p = len(data) - 1
                                news[str(country)] = p
                                m = 0
                                for d in data:
                                    n = m+1
                                    news["{}_{}_title".format(str(country),str(m))] = d['title']
                                    news["{}_{}_desc".format(str(country),str(m))] = d['description']
                                    news["{}_{}_url".format(str(country),str(m))] = d['url']
                                    text = text+"{}. [{}]({})\n".format(str(n),str(d['title']),str(d['url']))
                                    m = m+1
                                news_countries.append(country)
                                bot.send_message(chat_id = chat_id,text= text,reply_markup = reply_markup)
                            except:
                                print("Except Part")
                                text = text+"**Sorry No news updates available for {} right now!".format(country)
                                bot.send_message(chat_id = chat_id,text= text,reply_markup = reply_markup)
def start_schedule():
    import time
    schedule.every(83).minutes.do(update_the_news)
    schedule.every(90).minutes.do(auto_news)
    while True:
        schedule.run_pending()
        time.sleep(1)

def spam_less(b):
    chat_id = b.chat.id
    c = b.message_id
    time.sleep(7)
    bot.delete_messages(chat_id = chat_id,message_ids = c)
#-----------------------------------------------------------
@bot.on_message(Filters.command(["start{}".format(username), "start"], prefixes="/"))
def start(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    user_id  = message.from_user.id
    chat_id = message.chat['id']
    try:
        infected_by_userid = int(message.text.split(" ",1)[1])
        iby = True
        print("Received Userid")
    except:
        iby = False
        print("No text")
    try:
        a = userinf[str(user_id)]
    except:
        user = user_id
        a = check_user(user_id)
        if a:
            b = a[2]
            userinf[str(user)] = b
            userinf[str(user)+":mask_on"] = a[3]
            userinf[str(user)+":sneezed_by"] = a[4]
            if a[5]:
                userinf[str(user)+":users_infected"] = a[5]
        else:
            if iby:
                n = 'n'
                if new_user_busy:
                    time.sleep(1)
                userinf[str(user_id)] = 1
                userinf[str(user_id)+":mask_on"] = 0
                userinf[str(user_id)+":sneezed_by"] = infected_by_userid
                userinf[str(user_id)+":users_infected"] = None
                update_user(user_id,1,n,infected_by_userid)
                w = check_user(infected_by_userid)
                infected_users = w[5]
                firstname = bot.get_users(user_id).first_name
                if infected_users:
                    if infected_users!= '':
                        x = infected_users
                        x = x+",{}".format(str(user_id))
                        update_user(infected_by_userid,n,n,n,x)
                    else:
                        x = str(user_id)
                        update_user(infected_by_userid,n,n,n,x)
                    bot.send_message(chat_id = infected_by_userid,text="Yeah you infected [{}](tg://user?id={}) you've got another victim in your list!".format(firstname,user_id))
                else:
                    x = str(user_id)
                    update_user(infected_by_userid,n,n,n,x)
                    bot.send_message(chat_id = infected_by_userid,text="Yeah you infected [{}](tg://user?id={}) you've got another victim in your list!".format(firstname,user_id))
                try:
                    infec = userinf[str(infected_by_userid)+":users_infected"]
                    userinf[str(infected_by_userid)+":users_infected"] = infec+",{}".format(str(user_id))
                except:
                    userinf[str(infected_by_userid)+":users_infected"] = ",{}".format(str(user_id))
            else:
                if new_user_busy:
                    time.sleep(1)
                new_user(user_id)
                userinf[str(user_id)] = 0
                userinf[str(user_id)+":mask_on"] = 0
                userinf[str(user_id)+":sneezed_by"] = None
                userinf[str(user_id)+":users_infected"] = None
    a = bot.get_me().username
    keyboard = [[InlineKeyboardButton("Add to Group", url = 'https://telegram.me/{}?startgroup=foo'.format(a))]]
    keyboard.append([InlineKeyboardButton("Join Updates Channel",url = "t.me/mybotupdates")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    b = message.reply("I am Corona Virus (aka COVID-19)\nI will spread like fire if you dont properly maintain your hygeine and Social distance!\nAdd me to groups to have fun and get use /spreadit to get stared and also increase awareness and get latest updates on COVID19 .\nTo have fun see /help\nTo get Global Corona Statistics use \n/stats\nJoin our [Channel]({}) for updates and more news about the bot and other projects!\n**[click Here to know how to use this bot properly!](https://del.dog/howtocovid19bot)**\nThanks Stay safe and always maintain social distance and use sanitizers and masks!".format("t.me/mybotupdates"),reply_markup = reply_markup)
    if (supergroup) or (groups):
        spam_less(b)

@bot.on_message(Filters.command(["help","help{}".format(username)], prefixes='/'))
def help(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    user_id  = message.from_user.id
    chat_id = message.chat['id']
    try:
        a = userinf[str(user_id)]
    except:
        user = user_id
        a = check_user(user_id)
        if a:
            b = a[2]
            userinf[str(user)] = b
            userinf[str(user)+":mask_on"] = a[3]
            userinf[str(user)+":sneezed_by"] = a[4]
            if a[5]:
                userinf[str(user)+":users_infected"] = a[5]
        else:
            if new_user_busy:
                time.sleep(1)
            new_user(user_id)
            userinf[str(user_id)] = 0
            userinf[str(user_id)+":mask_on"] = 0
            userinf[str(user_id)+":sneezed_by"] = None
            userinf[str(user_id)+":users_infected"] = None
    if (supergroup) or (groups):
        try:
            firstname = bot.get_users(user_id).first_name
            a = bot.get_me().username
            keyboard = [[InlineKeyboardButton("Add to Group", url = 'https://telegram.me/{}?startgroup=foo'.format(a))]]
            keyboard.append([InlineKeyboardButton("Join Updates Channel",url = "t.me/mybotupdates")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id = user_id,text = "Hello [{}](tg://user?{}),\nI am The Corona Bot Add me to groups for me to get started use /spreadit in groups and here are some Commands\n/sneeze : You can spread the virus by using /sneeze in groups\n/infect : In a group reply with /infect to infect that person on purpose\n/victims : A list of users you have infected\n/maskon : Toggle mask on\n/maskoff : Toggle mask off! \n/sanitize : Sanitize the group if someone sneezed to prevent the virus from infecting users!\n/stats : See stats of corona globally or just pass the country name \nFor example: ```/stats india``` will return stats of India\n/news countryname : To see news related to corona of that country \n/autonews : To toggle Auto news updates on or off\n/addcountry : Pass a country name to add it in the news updates list\n/delcountry : Remove a country from news updates list\n/check : Reply to a user to see if he/she is infected with the virus or not! or just use this to see if you are infected or not\n\nIf you feel symptoms like **COUGH,FEVER,CHEST PAIN,BREADTH PROBLEMS** visit a Doctor and get your desired mesidcines and test's done!and if necessary quarantine yourself at home\n\nJoin our [Channel]({}) for updates and more news about the bot and other projects\n**[click Here to know how to use this bot properly!](https://del.dog/howtocovid19bot)**".format(firstname,user_id,"t.me/mybotupdates"),reply_markup = reply_markup)
            b = message.reply("Help message sent in personal chat!")
            spam_less(b)
        except:
            b = message.reply("I was not able to send you the Help message personally please message me personally to see help!")
            spam_less(b)
    else:
        firstname = bot.get_users(user_id).first_name
        a = bot.get_me().username
        keyboard = [[InlineKeyboardButton("Add to Group", url = 'https://telegram.me/{}?startgroup=foo'.format(a))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message.reply("Hello [{}](tg://user?{}),\nI am The Corona Bot Add me to groups for me to get started use /spreadit in groups and here are some Commands\n/sneeze : You can spread the virus by using /sneeze in groups\n/infect : In a group reply with /infect to infect that person on purpose\n/victims : A list of users you have infected\n/maskon : Toggle mask on\n/maskoff : Toggle mask off! \n/sanitize : Sanitize the group if someone sneezed to prevent the virus from infecting users!\n/stats : See stats of corona globally or just pass the country name \nFor example: ```/stats india``` will return stats of India\n/news countryname : To see news related to corona of that country \n/autonews : To toggle Auto news updates on or off\n/addcountry : Pass a country name to add it in the news updates list\n/delcountry : Remove a country from news updates list\n/check : Reply to a user to see if he/she is infected with the virus or not! or just use this to see if you are infected or not\n\nIf you feel symptoms like **COUGH,FEVER,CHEST PAIN,BREADTH PROBLEMS** visit a Doctor and get your desired mesidcines and test's done!and if necessary quarantine yourself at home\n\nJoin our [Channel]({}) for updates and more news about the bot and other projects\n**[click Here to know how to use this bot properly!](https://del.dog/howtocovid19bot)**".format(firstname,user_id,"t.me/mybotupdates"),reply_markup=reply_markup)

@bot.on_message(Filters.command(["check","check{}".format(username)],prefixes='/'))
def check(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    user_id = message.from_user.id
    reply = message.reply_to_message
    if reply:
        user = reply.from_user.id
        try:
            a = userinf[str(user)]
        except:
            a = check_user(user)
            if a:
                b = a[2]
                userinf[str(user)] = b
                userinf[str(user)+":mask_on"] = a[3]
                userinf[str(user)+":sneezed_by"] = a[4]
                if a[5]:
                    userinf[str(user)+":users_infected"] = a[5]
            else:
                if new_user_busy:
                    time.sleep(1)
                new_user(user)
                a = check_user(user)
                b = a[2]
                userinf[str(user)] = b
                userinf[str(user)+":mask_on"] = a[3]
                userinf[str(user)+":sneezed_by"] = a[4]
        a = userinf[str(user)]
        b = bot.get_users(user).first_name
        c = userinf[str(user)+":sneezed_by"]
        if a:
            if c:
                first = bot.get_users(c).first_name
                b = message.reply("Be aware [{}](tg://user?id={}) is infected with Corona Virus by [{}](tg://user?id={}) do not get close to him or even you might get infected and use a mask! \n\nAlways wear a mask wherever you go rather it be a telegram group or a place in real life.".format(b,user,first,c))
            else:
                b = message.reply("Be aware [{}](tg://user?id={}) is infected with Corona Virus do not get close to him or even you might get infected and use a mask! \n\nAlways wear a mask wherever you go rather it be a telegram group or a place in real life.".format(b,user))
        else:
            b = message.reply("[{}](tg://user?id={}) Is safe and has not been infected with corona!\n\nEven if he is safe that does not mean you wont get affected so please follow the rules wear a /maskon and always /sanitize your area. ".format(b,user))
        if (supergroup) or (groups):
            spam_less(b)
    else:
        try:
            a = userinf[str(user_id)]
        except:
            a = check_user(user_id)
            if a:
                b = a[2]
                userinf[str(user_id)] = b
                userinf[str(user_id)+":mask_on"] = a[3]
                userinf[str(user_id)+":sneezed_by"] = a[4]    
            else:
                if new_user_busy:
                    time.sleep(1)
                new_user(user_id)
                a = check_user(user_id)
                b = a[2]
                userinf[str(user_id)] = b
                userinf[str(user_id)+":mask_on"] = a[3]
                userinf[str(user_id)+":sneezed_by"] = a[4]
        b = bot.get_users(user_id).first_name
        a = userinf[str(user_id)]
        try:
            c = userinf[str(user_id)+":sneezed_by"]
        except:
            c = False
        if a :
            if c:
                first = bot.get_users(c).first_name
                message.reply("Be aware You are infected with Covid-19 by [{}](tg://user?id={}) and if you dont treat properly and maintain social distance you might infect other people and make it worse! Always wear a mask wherever you go in real life as well to prevent others from getting infected!".format(first,c))
            else:
                message.reply("Be aware You are infected with Covid-19 by and if you dont treat properly and maintain social distance you might infect other people and make it worse! Always wear a mask wherever you go in real life as well to prevent others from getting infected!")
            
        else:
            message.reply("Yay! you are not infected and are safe! But not for long if you dont  /maskon 😷 and /sanitize 💉💉 your area and groups properly and frequently!")
        if (supergroup) or (groups):
            spam_less(b)
            

@bot.on_message(Filters.command(["stats","stats{}".format(username),"info","info{}".format(username)],prefixes = '/'))
def info(client,message):
    chat_id = message.chat.id
    try:
        country = message.text.split(" ",1)[1]
    except:
        country = False
    if country:
        a = r.get("https://restcountries.eu/rest/v2/name/{}".format(str(country)))
        if a.status_code == 200:
            a = json.loads(a.text)
            keyboard = []
            for b in a:
                name = b['name']
                code = b['alpha2Code']
                keyboard.append([InlineKeyboardButton("{}".format(name), callback_data = "stats:{}".format(code))])
            keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            user_query[str(message.from_user.id)+"_1"] = "news:{}".format(code)
            message.reply("Please choose your desired country!",reply_markup = reply_markup)
        else:
            b = message.reply("No countries with that name found make sure you are passing the right country name that exists!")
            m = b.message_id
            time.sleep(10)
            bot.delete_messages(chat_id = chat_id,message_ids = m)
    else:
        chat_id = message.chat['id']
        b = message.reply("Processing!")
        b = b.message_id
        a = r.get("https://api.thevirustracker.com/free-api?global=stats")
        #a = a.text
        #a = a.replace("<br />\n<b>Warning</b>:  session_start(): open(/var/cpanel/php/sessions/ea-php72/sess_9c962023b9e3054cc3977e038435b451, O_RDWR) failed: No space left on device (28) in <b>/home/thevirustracker/api.thevirustracker.com/connections.php</b> on line <b>1</b><br />\n<br />\n<b>Warning</b>:  session_start(): Failed to read session data: files (path: /var/cpanel/php/sessions/ea-php72) in <b>/home/thevirustracker/api.thevirustracker.com/connections.php</b> on line <b>1</b><br />\n","")
        #a = json.loads(a)
        total_cases = re.search('"total_cases":(.+?),',a.text)[1]
        total_recovered = re.search('"total_recovered":(.+?),',a.text)[1]
        total_unresolved = re.search('"total_unresolved":(.+?),',a.text)[1]
        total_deaths = re.search('"total_deaths":(.+?),',a.text)[1]
        new_cases_today = re.search('"total_new_cases_today":(.+?),',a.text)[1]
        deaths_today = re.search('"total_new_deaths_today":(.+?),',a.text)[1]
        #total_active_cases = a['results'][0]['total_active_cases']
        #total_serious_cases = a['results'][0]['total_serious_cases']
        #total_affected_countries = a['results'][0]['total_affected_countries']
        text = "**Global Report**\n\n**Total Cases**: {}\n**Total Recovered**: {}\n**Total Unresolved**: {}\n**Total Deaths**: {}\n**New Cases Today**: {}\n**Deaths Today**: {}".format(total_cases,total_recovered,total_unresolved,total_deaths,new_cases_today,deaths_today)
        keyboard = []
        keyboard.append([InlineKeyboardButton("Delete",callback_data="exitnow")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(chat_id = chat_id,text = text,message_id = b,reply_markup=reply_markup)
        #message.reply(text)

    

@bot.on_message(Filters.command(["sneeze","sneeze{}".format(username)],prefixes='/'))
def sneeze(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    user_id = message.from_user.id
    try:
        infected = userinf[str(user_id)]
        mask = userinf[str(user_id)+":mask_on"]
    except: 
        user_db = check_user(user_id)
        if user_db:
            inf = user_db[2]
            userinf[str(user_id)] = inf
            mask_o = user_db[3]
            userinf[str(user_id)+":mask_on"] = mask_o
            if user_db[4]:
                inf_b = user_db[4]
                userinf[str(user_id)+":sneezed_by"] = inf_b
        else:
            if new_user_busy:
                time.sleep(1)
            new_user(user_id)
            user_db = check_user(user_id)
        infected = user_db[2]
        mask = user_db[3]
        userinf[str(user_id)] = infected
        userinf[str(user_id)+":mask_on"] = mask
        if user_db[4]:
            inf_b = user_db[4]
            userinf[str(user_id)+":sneezed_by"] = inf_b
    if infected == 1:
        infected = True
    else:
        infected = False
    if mask == 1:
        mask = True
    else:
        mask = False
    if (supergroup) or (groups):
        chat_id = message.chat['id']
        num1 = random.randint(1, 5)
        if (infected == True) and (mask == True):
            b = message.reply("Cannot Spread infection as you have your mask **on**\nWell thats a good choice anyway!\n\nWear a mask to prevent yourself from getting infected!")
            if (supergroup) or (groups):
                spam_less(b)
        elif (infected == True) and (mask == False):
            first_name = bot.get_users(user_id).first_name
            try:
                print("Try Part!")
                '''a = group.query.filter_by(chatid = chat_id).first()
                a.sneezed = 1'''
                infected = groupsinf[str(chat_id)]
                sneeze_remaining = groupsinf[str(chat_id)+":sneeze"]
                sneezed_by = groupsinf[str(chat_id)+":sneezed_by"]
                '''if (a.sneezed_by == '') or (a.sneezed_by == None) or (a.sneezed_by == []):
                    b = str(user_id)
                    a.sneezed_by = b
                else:
                    b = a.sneezed_by
                    b = b+",{}".format(user_id)
                    a.sneezed_by = b'''
                print("Try success")
            except:
                print("except")
                data = check_group(chat_id)
                if data:
                    pass
                else:
                    if new_group_busy:
                        time.sleep(1)
                    new_group(a=chat_id,b=0,c=0)
                    data = check_group(chat_id)
                infected = data[2]
                sneeze_remaining = data[3]
                sneezed_by = data[4]
                #message.reply("Works Till here")
                groupsinf[str(chat_id)] = infected
                groupsinf[str(chat_id)+":sneeze"] = sneeze_remaining
                groupsinf[str(chat_id)+":sneezed_by"] = sneezed_by
                print("Except Success")
            if (sneezed_by == '') or (sneezed_by == None):
                sneezed_by = user_id
            else:
                b = str(sneezed_by)
                if str(user_id) in b:
                    pass
                else:
                    b = str(b)+",{}".format(str(user_id))
                    sneezed_by = b
            if sneeze_remaining == 0:
                b = num1
                sneeze_remaining = b
            else:
                b = sneeze_remaining
                b = b + num1
                sneeze_remaining = b
            if infected == 0:
                infected = 1
            else:
                infected = 'n'
            update_group(a=chat_id,b=infected,c=sneeze_remaining,d=sneezed_by)
            groupsinf[str(chat_id)+":sneezed_by"] = sneezed_by
            groupsinf[str(chat_id)+":sneeze"] = sneeze_remaining
            groupsinf[str(chat_id)] = 1
            b = message.reply("[{}](tg://user?id={}) sneezed and has spread the virus 🦠 to prevent yourself from getting infected wear a mask! or sanitize now!".format(first_name,user_id))
            spam_less(b)
        elif (infected == False):
            if mask == False:
                b = message.reply("You are not infected!\nWell that's a good thing but that does not mean you wont wear a mask!")
            else:
                b = message.reply("You are not infected!\nWell that's a good thing and also you have your mask on I appriciate that do the same to be protected for real")
            spam_less(b)
        
    else:
        message.reply("You should use this command in groups to spread some virus! \nI said in groups but dont go sneezing everywhere in real life!!")

@bot.on_message(Filters.command(["maskon","maskon{}".format(username)],prefixes = '/'))
def maskon(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    user_id  = message.from_user.id
    chat_id = message.chat['id']
    try:
        infected = userinf[str(user_id)]
        mask = userinf[str(user_id)+":mask_on"] 
    except:
        a = check_user(user_id)
        if a:
            pass
        else:
            if new_user_busy:
                time.sleep(1)
            new_user(user_id)
        a = check_user(user_id)
        infected = a[2]
        mask = a[3]
        userinf[str(user_id)+":mask_on"] = mask
        userinf[str(user_id)] = infected
    if mask == 1:
        userinf[str(user_id)+":mask_on"] = 1
        userinf[str(user_id)] = infected
        b = message.reply("Mask On You wont be infected till you keep it on\nKeep the same passion in real life and always wear a mask!")
    else:
        if update_user_busy:
            time.sleep(1)
        update_user(a=user_id,b=n,c=1,d='n') 
        userinf[str(user_id)+":mask_on"] = 1
        userinf[str(user_id)] = infected
        b = message.reply("Mask On You wont be infected till you keep it on\nKeep the same passion in real life and always wear a mask!")
    if (supergroup) or (groups):
        spam_less(b)

@bot.on_message(Filters.command(["maskoff","maskoff{}".format(username)],prefixes = '/'))
def maskoff(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    user_id  = message.from_user.id
    chat_id = message.chat['id']
    try:
        infected = userinf[str(user_id)]
        mask = userinf[str(user_id)+":mask_on"] 
    except:
        a = check_user(user_id)
        if a:
            pass
        else:
            if new_user_busy:
                time.sleep(1)
            new_user(user_id)
        a = check_user(user_id)
        infected = a[2]
        mask = a[3]
        userinf[str(user_id)+":mask_on"] = mask
        userinf[str(user_id)] = infected
    if mask == 0:
        userinf[str(user_id)+":mask_on"] = 0
        userinf[str(user_id)] = infected
        b = message.reply("Mask off You might get infected if you keep it off\nThats a bad idea in real life so make sure you always wear a mask while going somewhere if its that important!")
    else:
        if update_user_busy:
            time.sleep(1)
        update_user(a=user_id,b=infected,c=0,d='n')
        userinf[str(user_id)+":mask_on"] = 0
        userinf[str(user_id)] = infected
        b = message.reply("Mask off You might get infected if you keep it off\nThats a bad idea in real life so make sure you always wear a mask while going somewhere if its that important!")
    if (supergroup) or (groups):
        spam_less(b)

@bot.on_message(Filters.command(["sanitize","sanitize{}".format(username)],prefixes = '/'))
def sanitize(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    if supergroup or groups:
        chat_id = message.chat['id']
        user_id = message.from_user.id
        try:
            z = userinf[str(user_id)]
            x = userinf[str(user_id)+":mask_on"]
            w = userinf[str(user_id)+":sneezed_by"]
        except:
            user_inf = check_user(user_id)
            if user_inf:
                inf = user_inf[2]
                mask_o = user_inf[3] 
                if user_inf[4]:
                    inf_by = user_inf[4]
                    userinf[str(user_id)+":sneezed_by"] = user_inf[4]
                userinf[str(user_id)] = inf
                userinf[str(user_id)+":mask_on"] = mask_o
            else:
                if new_user_busy:
                    time.sleep(1)
                new_user(user_id)
                z = check_user(user_id)
                userinf[str(user_id)] = z[2]
                userinf[str(user_id)+":mask_on"] = z[3]
        try:
            infected = groupsinf[str(chat_id)]
            infected_by = groupsinf[str(chat_id)+":sneezed_by"]
            infection_remaining = groupsinf[str(chat_id)+":sneeze"]
        except:
            data = check_group(chat_id)
            if data:
                pass
            else:
                if new_group_busy:
                    time.sleep(1)
                new_group(chat_id,0,0)
                data = check_group(chat_id)
            infected = data[2]
            if data[4]:
                infected_by = data[4]
                groupsinf[str(chat_id)+":sneezed_by"] = infected_by
            infection_remaining = data[3]
            groupsinf[str(chat_id)] = infected
            groupsinf[str(chat_id)+":sneeze"] = infection_remaining
        if infected:
            groupsinf[str(chat_id)] = 0
            groupsinf[str(chat_id)+":sneeze"] = 0
            update_group(a=chat_id,b=0,c=0,d=n)
            b = message.reply("The group was sanitized and the virus infection was destroyed!!\nEven Sanitize your House and people to be protected in real life too!")
        else:
            groupsinf[str(chat_id)] = 0
            b = message.reply("The group was sanitized and the virus infection was destroyed!!\nEven Sanitize your House and people to be protected in real life too!")
        spam_less(b)
    else:
        message.reply("Well done,Youre now sanitized and any viruses on you are destroyed!!\nDont forget to maintain such hygeine in real life!!!")
    

@bot.on_message(Filters.command(["spreadit","spreadit{}".format(username)],prefixes='/'))
def spreadit(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    user_id = message.from_user.id
    chat_id = message.chat.id
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    if supergroup or groups:
        groupsinf[str(chat_id)] = 1
        try:
            a = groupsinf[str(chat_id)+":sneezed_by"]
            if (a!= ''):
                b = a+",{}".format(user_id)
            else:
                a = user_id
        except:
            a = user_id
        groupsinf[str(chat_id)+":sneezed_by"] = a
        groupsinf[str(chat_id)+":sneeze"] = 12
        data = check_group(chat_id)
        if data:
            update_group(a=chat_id,b=1,c=12,d=a)
        else:
            if new_group_busy:
                time.sleep(1)
            new_group(chat_id,1,12,a)
        b = message.reply("Infection Spread")
        if (supergroup) or (groups):
            spam_less(b)
    else:
        message.reply("Use this command in groups")

@bot.on_message(Filters.command(["checkinfection","checkinfection{}".format(username)],prefixes='/'))
def checkinfection(client,message):
    chat_id = message.chat.id
    inf = groupsinf[str(chat_id)]
    if inf == 1:
        message.reply("Group is infected!")
    else:
        message.reply("Group is not infected")

@bot.on_message(Filters.command("users"))
def users11(client,message):
    user_id = message.from_user.id
    if user_id in admins:

        b = db.query("select * from tgusers")
        a = b.fetchall()
        e = db.query("select * from groups")
        b = e.fetchall()
        c = len(a)
        d = len(b)
        text = "Hello Admin\nTotal Users : {}\nTotal Groups : {}".format(c,d)
        message.reply(text)

@bot.on_message(Filters.command("gg"))
def groupglobals(client,message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if user_id in admins:
        try:
            infected = groupsinf[str(chat_id)]
            sneeze = groupsinf[str(chat_id)+":sneeze"]
            sneezed_by = groupsinf[str(chat_id)+":sneezed_by"]
            text = "Is infected : {}\nInfection Remaining : {}, \nInfection spread by : {}".format(infected,sneeze,sneezed_by)
            message.reply(text)
        except:
            message.reply("Group Has no infections")

@bot.on_message(Filters.command(["infect","infect{}".format(username)],prefixes='/'))
def infect(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    chat_id = message.chat.id
    user_id = message.from_user.id
    reply = message.reply_to_message
    try:
        infected = userinf[str(user_id)]
        mask = userinf[str(user_id)+":mask_on"]
    except:
        data = check_user(user_id)
        if data:
            pass
        else:
            if new_user_busy:
                time.sleep(1)
            new_user(user_id)
            data = check_user(user_id)
        infected = data[2]
        mask = data[3]
        userinf[str(user_id)] = infected
        userinf[str(user_id)+":mask_on"] = mask
    if reply:
        user = reply.from_user.id
        try:
            infected_reply = userinf[str(user)]
            mask_reply = userinf[str(user)+":mask_on"]
        except:
            data1 = check_user(user)
            if data1:
                pass
            else:
                if new_user_busy:
                    time.sleep(1)
                new_user(user)
                data1 = check_user(user)
            infected_reply = data1[2]
            mask_reply = data1[3]
            userinf[str(user_id)] = infected_reply
            userinf[str(user_id)+":mask_on"] = mask_reply
        if mask:
            b = message.reply("You have your mask on! cannot infect people use /maskoff and then again reply to a users message with /infect")
            spam_less(b)
        elif mask_reply == 1:
            first_name = bot.get_users(user).first_name
            message.reply("[{}](tg://user?id={}) has worn a mask cannot infect him!!!Its always better to wear a mask".format(first_name,user))
            spam_less(b)
        elif infected_reply == 0 and mask_reply == 0:
            first_name_reply = bot.get_users(user).first_name
            first_name = bot.get_users(user_id).first_name
            infected_reply = 1
            mask_reply = 0
            infected_by_reply = user_id
            userinf[str(user)] = infected_reply
            userinf[str(user)+":mask_on"] = mask_reply
            userinf[str(user)+":sneezed_by"] = infected_by_reply
            if update_user_busy:
                time.sleep(1)
            update_user(a=user,b=infected_reply,c=mask_reply,d=infected_by_reply)
            try:
                users_infected = str(userinf[str(user_id)+":users_infected"])
            except:
                data = check_user(user_id)
                if data[5]:
                    userinf[str(user_id)+":users_infected"] = str(data[5])
                    users_infected = userinf[str(user_id)+":users_infected"]
                else:
                    userinf[str(user_id)+":users_infected"] = ''
                    users_infected = userinf[str(user_id)+":users_infected"]
            if (users_infected != '') or (users_infected != None):
                users_infected = users_infected+",{}".format(str(user))
                userinf[str(user_id)+":users_infected"] = users_infected
            else:
                users_infected = str(user)
                userinf[str(user_id)+":users_infected"] = users_infected
            if update_user_busy:
                time.sleep(1)
            update_user(user_id,n,n,n,users_infected)
            keyboard=[]
            keyboard.append([InlineKeyboardButton("Okay I got it!",callback_data = "exitnow:{}".format(user))])
            reply = InlineKeyboardMarkup(keyboard)
            message.reply("[{}](tg://user?id={}) has been infected with the virus from [{}](tg://user?id={})!\nIf you dont want this to happen in real life make sure you wear a mask!".format(first_name_reply,user,first_name,user_id),reply_markup = reply)
        elif infected == 1:
            b = message.reply("Looks like the user is already infected !Make sure everyone stays atleast 1.5 meters away from him")
            spam_less(b)
    else:
        if (supergroup) or (groups):
            b = message.reply("Please reply to a user's message if you want to infect him! or to know more see /help in personal chat")
            spam_less(b)
        else:
            message.reply("Give this link to your friends to infect them \n```https://t.me/thecovid19bot?start={}```\n\nYou can also use this command in groups by just replying to someones message wil Infect them".format(user_id))

@bot.on_message(Filters.command(["victims","victims{}".format(username)],prefixes='/'))
def victims(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    user_id = message.from_user.id
    try:
        infected = userinf[str(user_id)]
        mask = userinf[str(user_id)+":mask_on"]
        infected_by = userinf[str(user_id)+":sneezed_by"]
        users_infected = userinf[str(user_id)+":users_infected"]
    except:
        data = check_user(user_id)
        if data:
            pass
        else:
            if new_user_busy:
                time.sleep(1)
            new_user(user_id)
            data = check_user(user_id)
        infected = data[2]
        mask = data[3]
        infected_by = data[4]
        users_infected = data[5]
        #message.reply(str(type(users_infected)))
        userinf[str(user_id)] = infected
        userinf[str(user_id)+":mask_on"] = mask
        userinf[str(user_id)+":sneezed_by"] = infected_by
        userinf[str(user_id)+":users_infected"] = users_infected
    if users_infected:
        text = ''
        num = 0
        users_infected = users_infected.split(',')
        for a in users_infected:
            if (a != '') or (a!= None) (a != 'none') or (a != 'None'):
                try:
                    user = bot.get_users(a)
                    first_name = str(user.first_name)
                    last_name = user.last_name
                    if last_name: #(last_name != None) or (last_name != '') or (str(last_name) != "<class 'NoneType'>") or (str(last_name) == 'None') or (last_name == 'None'):
                        name = first_name + " " + str(last_name)
                    else:
                        name = first_name
                    tex = "[{}](tg://user?id={})\n".format(name,a)
                    text=text+tex
                    num = num+1
                except:
                    pass
        if num > 0 :
            total = 'Total Users Infected : **{}**\n\n'.format(num)
        else:
            total = ''
        text = total+text
        if text != '':
            b = message.reply(text)
        else:
            b = message.reply("You havent infected anyone! Add me in a group and then use /sneeze or reply to someone with /infect and infect someone!")
    else:
        b = message.reply("You havent infected anyone! Add me in a group and then use /sneeze or reply to someone with /infect and infect someone!")
    if (supergroup) or (groups):
        spam_less(b)

@bot.on_message(Filters.command(['news','news{}'.format(username)],prefixes='/'))
def get_news(client,message):
    try:
        country = message.text.split(" ",1)[1]
    except:
        country = False
    print(country)
    if country:
        a = r.get("https://restcountries.eu/rest/v2/name/{}".format(str(country)))
        if a.status_code == 200:
            a = json.loads(a.text)
            keyboard = []
            for b in a:
                name = b['name']
                code = b['alpha2Code']
                keyboard.append([InlineKeyboardButton("{}".format(name), callback_data = "news:{}".format(code))])
            keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            user_query[str(message.from_user.id)+"_1"] = "news:{}".format(code)
            message.reply("Please choose your desired country!",reply_markup = reply_markup)
        else:
            message.reply("No countries with that name found make sure you are passing the right country name that exists!")
    else:
        message.reply("Pass a country name to get News about it\nLike : ```/news india```")


@bot.on_message(Filters.command(['autonews','autonews{}'.format(username)],prefixes='/'))
def set_auto_news(client,message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    data = check_news(chat_id)
    if data:
        pass
    else:
        data = create_auto_news(chat_id)
        data = check_news(chat_id)
    keyboard = []
    if (supergroup) or (groups):
        check = bot.get_chat_member(chat_id,user_id).status
        if  (check == 'administrator') or (check == 'creator'):
            if data[3]:
                keyboard.append([InlineKeyboardButton("Turn On Updates",callback_data="g:{}:1".format(chat_id,user_id))])
                keyboard.append([InlineKeyboardButton("Turn Off Updates",callback_data="g:{}:0".format(chat_id,user_id))])
                reply_markup = InlineKeyboardMarkup(keyboard)
                message.reply("Please Choose an action:",reply_markup = reply_markup)
            else:
                b = message.reply("You havent added any countries From which you wana receive news of!\nAdd one using ```/addcountry countryname```")
                spam_less(b)
        else:
            b = message.reply("Oops for that action you need to be an admin! But you can set news updates in personal chat too🤗")
            spam_less(b)
    else:
        if data[3]:
            keyboard.append([InlineKeyboardButton("Turn On Updates",callback_data="u:1".format(user_id))])
            keyboard.append([InlineKeyboardButton("Turn Off Updates",callback_data="u:0".format(user_id))])
            reply_markup = InlineKeyboardMarkup(keyboard)
            message.reply("Please Choose an action:",reply_markup = reply_markup)
        else:
            b = message.reply("You havent added any countries From which you wana receive news of!\nAdd one using ```/addcountry countryname```")
            
@bot.on_message(Filters.command(["addcountry","addcountry{}".format(username)],prefixes='/'))
def add_country(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    try:
        country = message.text.split(" ",1)[1]
    except:
        country = False
    if country:
        print('hii')
        user_id = message.from_user.id
        chat_id = message.chat.id
        if groups or supergroup:
            check = bot.get_chat_member(chat_id,user_id).status 
            if (check == 'administrator') or (check == 'creator'):
                print("admin")
                data = check_news(chat_id)
                if data:
                    pass
                else:
                    create_auto_news(chat_id)
                a = r.get("https://restcountries.eu/rest/v2/name/{}".format(str(country)))
                if a.status_code == 200:
                    a = json.loads(a.text)
                    keyboard = []
                    for b in a:
                        name = b['name']
                        code = b['alpha2Code']
                        keyboard.append([InlineKeyboardButton("{}".format(name), callback_data = "acountry:g:{}:{}".format(code,name))])
                    keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    user_query[str(message.from_user.id)+"_1"] = "news:{}".format(code)
                    message.reply("Please choose your desired country you wish to receive updates for!",reply_markup = reply_markup)
                else:
                    message.reply("Wrong Country Name Provided!")
            else:
                b = message.reply("You need to be an admin to perform that action!!!!")
                b = b.message_id
                time.sleep(7)
                bot.delete_messages(chat_id = chat_id,message_ids= b)
        else:

            a = r.get("https://restcountries.eu/rest/v2/name/{}".format(str(country)))
            if a.status_code == 200:
                a = json.loads(a.text)
                keyboard = []
                for b in a:
                    name = b['name']
                    code = b['alpha2Code']
                    keyboard.append([InlineKeyboardButton("{}".format(name), callback_data = "acountry:u:{}:{}".format(code,name))])
                keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                user_query[str(message.from_user.id)+"_1"] = "news:{}".format(code)
                message.reply("Please choose your desired country you wish to receive updates for!",reply_markup = reply_markup)
    elif country == False:
        if (groups) or (supergroup):
            check = bot.get_chat_member(chat_id,user_id).status 
            if (check == 'administrator') or (check == 'creator'):
                b = message.reply("Pass a country Name like  ```/addcountry countryname```")
            else:
                b = message.reply("You gotta be an admin to do it !!please dont spam")
            spam_less(b)
        else:
            message.reply("Pass a country Name like  ```/addcountry countryname```")
        

@bot.on_message(Filters.command(['getcm','getcm{}'.format(username)],prefixes='/'))
def get_chat_m(client,message):
    chat_id = message.chat.id
    user = message.from_user.id
    check = bot.get_chat_member(chat_id,user).status
    message.reply(check)

@bot.on_message(Filters.command(["delcountry","delcountry{}".format(username)],prefixes='/'))
def delete_country(client,message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    keyboard = []
    if supergroup or groups:
        check = bot.get_chat_member(chat_id,user_id).status
        if (check == 'administrator') or (check == 'creator'):
            data = check_news(chat_id)
            if data:
                c = data[3]
                if c:
                    d = c.split(",")
                    print("d :",d)
                    m = 0
                    if (d!=[]) or (d!= '') or (d!=None):
                        for e in d:
                            if e != '':
                                print("e:",e)
                                f = e.split(":")
                                print("f:",f)
                                cshort = f[0]
                                cfull = f[1]
                                keyboard.append([InlineKeyboardButton("{}".format(cfull),callback_data="delc|g|{}".format(e))])
                                m = 1
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        message.reply("Please choose the country you wish to remove from auto alerts:",reply_markup=reply_markup)
                    else:
                        b = message.reply("You havent added any countries to be deleted!!")
                        b = b.message_id
                        time.sleep(7)
                        bot.delete_messages(chat_id = chat_id,message_ids= b)
                else:
                    b = message.reply("You havent added any countries to be deleted!!")
                    b = b.message_id
                    time.sleep(7)
                    bot.delete_messages(chat_id = chat_id,message_ids= b)
            else:
                create_auto_news(chat_id)
                b = message.reply("You havent added any countries to be deleted!!")
                b = b.message_id
                time.sleep(7)
                bot.delete_messages(chat_id = chat_id,message_ids= b)
        else:
            b = message.reply("You need to be an admin to use that command!!!!")
            b = b.message_id
            time.sleep(7)
            bot.delete_messages(chat_id = chat_id,message_ids= b)
    else:
        data = check_news(chat_id)
        if data:
            c = data[3]
            if c:
                d = c.split(",")
                print("d :",d)
                m = 0
                if (d!=[]) or (d!= '') or (d!=None):
                    for e in d:
                        if e != '':
                            print("e :",e)
                            f = e.split(":")
                            print("f :",f)
                            cshort = f[0]
                            cfull = f[1]
                            keyboard.append([InlineKeyboardButton("{}".format(cfull),callback_data="delc|u|{}".format(e))])
                            m = 1
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    message.reply("Please choose the country you wish to remove from auto alerts:",reply_markup=reply_markup)
                else:
                    b = message.reply("You havent added any countries to be deleted!!")
                    b = b.message_id
                    time.sleep(7)
                    bot.delete_messages(chat_id = chat_id,message_ids= b)
            else:
                b = message.reply("You havent added any countries to be deleted!!")
                b = b.message_id
                time.sleep(7)
                bot.delete_messages(chat_id = chat_id,message_ids= b)
        else:
            create_auto_news(chat_id)
            b = message.reply("You havent added any countries to be deleted!!")
            b = b.message_id
            time.sleep(7)
            bot.delete_messages(chat_id = chat_id,message_ids= b)

@bot.on_message(Filters.text & Filters.incoming)
def spread_infection(client,message):
    supergroup = message.chat['type'] == 'supergroup'
    groups = message.chat['type'] == 'group'
    if supergroup or groups:
        num = random.randint(1,10)
        chat_id = message.chat['id']
        try:
            user_id = message.from_user.id
        except:
            user_id = False
        if user_id:
            try:
                infected = groupsinf[str(chat_id)]
                sneezed_by = groupsinf[str(chat_id)+":sneezed_by"]
                sneeze = groupsinf[str(chat_id+":sneeze")]
            except:
                data = check_group(chat_id)
                if data:
                    infected = data[2]
                    sneezed_by = data[4]
                    sneeze = data[3]
                    groupsinf[str(chat_id)] = infected
                    groupsinf[str(chat_id)+":sneezed_by"] = sneezed_by
                    groupsinf[str(chat_id)+":sneeze"] = sneeze
                else:
                    if new_group_busy:
                        time.sleep(1)
                    new_group(a=chat_id,b=0,c=0)
                    data = check_group(chat_id)
                    infected = data[2]
                    sneezed_by = data[4]
                    sneeze = data[3]
                    groupsinf[str(chat_id)] = infected
                    if data[4]:
                        groupsinf[str(chat_id)+":sneezed_by"] = sneezed_by
                    groupsinf[str(chat_id)+":sneeze"] = sneeze
            if groupsinf[str(chat_id)] == 1 :

                if num%2 == 0:
                    try:
                        z = userinf[str(user_id)]
                        x = userinf[str(user_id)+":mask_on"]
                        w = userinf[str(user_id)+":sneezed_by"]
                    except:
                        user_inf = check_user(user_id)
                        if user_inf:
                            inf = user_inf[2]
                            mask_o = user_inf[3]
                            if user_inf[4]:
                                inf_by = user_inf[4]
                                userinf[str(user_id)+":sneezed_by"] = inf_by
                            userinf[str(user_id)] = inf
                            userinf[str(user_id)+":mask_on"] = mask_o
                        else:
                            if new_user_busy:
                                time.sleep(1)
                            new_user(user_id)
                            user_inf = check_user(user_id)
                            if user_inf:
                                inf = user_inf[2]
                                mask_o = user_inf[3] 
                                if user_inf[4]:
                                    inf_by = user_inf[4]
                                    userinf[str(user_id)+":sneezed_by"] = inf_by
                                userinf[str(user_id)] = inf
                                userinf[str(user_id)+":mask_on"] = mask_o
                    a = sneezed_by.split(",")
                    infecting_user = random.choice(a)
                    first_name_infecting = bot.get_users(infecting_user).first_name
                    first_name = bot.get_users(user_id).first_name
                    try:
                        a = userinf[str(user_id)]
                        b = userinf[str(user_id)+":mask_on"]
                    except:
                        data = check_user(user_id)
                        a = data[2]
                        b = data[3]
                        userinf[str(user_id)] = a
                        userinf[str(user_id)+":mask_on"] = b
                        if data[4]:
                            userinf[str(user_id)+":infected_by"] = data[4]
                    if (a==0) and (b==0):
                        keyboard=[]
                        keyboard.append([InlineKeyboardButton("Okay I got it!",callback_data = "exitnow:{}".format(user_id))])
                        reply = InlineKeyboardMarkup(keyboard)
                        text = "[{}](tg://user?id={}) has been infected with the virus 🦠 by [{}](tg://user?id{})\n\nBe careful for your life!".format(first_name,user_id,first_name_infecting,infecting_user,reply_markup = reply)
                        userinf[str(user_id)] = 1
                        userinf[str(user_id)+":sneezed_by"] = infecting_user
                        if update_user_busy:
                            time.sleep(1)
                        update_user(a=user_id,b=1,c=0,d=infecting_user)
                        try:
                            users_infected = str(userinf[str(infecting_user)+":users_infected"])
                        except:
                            data = check_user(infecting_user)
                            if data:
                                users_infected = str(data[5])
                            else:
                                new_user(infecting_user)
                                users_infected = ''
                        if (users_infected != '') or (users_infected != None):
                            users_infected = users_infected+",{}".format(str(user_id))
                            userinf[str(infecting_user)+":users_infected"] = str(users_infected)
                        else:
                            users_infected = str(user_id)
                            userinf[str(infecting_user)+":users_infected"] = str(users_infected)
                        if update_user_busy:
                            time.sleep(1)
                        update_user(infecting_user,n,n,n,users_infected)
                        a = groupsinf[str(chat_id)+":sneeze"] 
                        groupsinf[str(chat_id)+":sneeze"] = a - 1
                        b = a - 1
                        if groupsinf[str(chat_id)+":sneeze"] == 0:
                            groupsinf[str(chat_id)] = 0
                            groupsinf[str(chat_id)+":sneezed_by"] = ''
                            update_group(a=chat_id,b=0,c=b,d=n)
                        else: 
                            update_group(a=chat_id,b=n,c=b,d=n)
                        bot.send_message(chat_id = chat_id,text = text)
                    else:
                        pass
                else:
                    pass
            else:
                pass

        
@bot.on_callback_query(news_filter)
def get_news(_,query):
    country = query.data.split(":")[1]
    country = str(country)
    country = country.lower()
    keyboard = []
    try:
        n = news[str(country)]
        m = 0
        while m <= n:
            title = news["{}_{}_title".format(str(country),str(m))]
            desc = news["{}_{}_desc".format(str(country),str(m))]
            url = news["{}_{}_url".format(str(country),str(m))]
            keyboard.append([InlineKeyboardButton("{}".format(title),callback_data = "get_news:{}:{}".format(str(country),str(m)))])
            m = m+1
        #keyboard.append([InlineKeyboardButton("🔙 Back", callback_data= user_query[str(query.from_user.id)+"_1"])])
        keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])
        reply_markup = InlineKeyboardMarkup(keyboard)    
        query.edit_message_text("Choose the news you wana read: ",reply_markup=reply_markup)
    except:
        try:
            data = newsapi.get_top_headlines(q='corona',language='en',country = '{}'.format(country))
            data = data['articles']
        except:
            query.answer("Sorry No news available for that country Thanks!")
            return False
        a = data
        p = len(data) - 1
        news[str(country)] = p
        m = 0
        for d in a:
            news["{}_{}_title".format(str(country),str(m))] = d['title']
            news["{}_{}_desc".format(str(country),str(m))] = d['description']
            news["{}_{}_url".format(str(country),str(m))] = d['url']
            m+=1
        news_countries.append(str(country))
        m = 0
        while m <= p:
            title = news["{}_{}_title".format(str(country),str(m))]
            desc = news["{}_{}_desc".format(str(country),str(m))]
            url = news["{}_{}_url".format(str(country),str(m))]
            keyboard.append([InlineKeyboardButton("{}".format(title),callback_data = "get_news:{}:{}".format(str(country),str(m)))])
            m = m+1
        #keyboard.append([InlineKeyboardButton("🔙 Back", callback_data= user_query[str(query.from_user.id)+"_1"])])
        keyboard.append([InlineKeyboardButton("Exit",callback_data = "exitnow")])    
        reply_markup = InlineKeyboardMarkup(keyboard)    
        query.edit_message_text("Choose the news you wana read: ",reply_markup=reply_markup)

@bot.on_callback_query(news_return_filter)
def return_news(_,query):
    print("Received")
    data = query.data.split(":")
    country = data[1]
    m = data[2]
    title = "**"+str(news["{}_{}_title".format(str(country),str(m))])+"**"
    desc = news["{}_{}_desc".format(str(country),str(m))]
    url = news["{}_{}_url".format(str(country),str(m))]
    text = "{}\n\n{}".format(title,desc)
    keyboard = [[InlineKeyboardButton("Read Full news", url = "{}".format(url))],[InlineKeyboardButton("🔙 Back", callback_data= user_query[str(query.from_user.id)+"_2"])],[InlineKeyboardButton("Exit",callback_data="exitnow")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text,reply_markup = reply_markup)


@bot.on_callback_query(delete_filter)
def delete_now(_,query):
    data = query.data.split(":")
    messageid = query.message.message_id
    try:
        userid = data[1]
        ison = 1
    except:
        ison = False
    if ison :
        user_id = query.from_user.id
        if user_id == userid:
            bot.delete_messages(chat_id = query.message.chat['id'], message_ids=messageid)
        else:
            query.answer("You are not meant to Press this!")
    else:    
        messageid = query.message.message_id
        bot.delete_messages(chat_id = query.message.chat['id'], message_ids=messageid)


@bot.on_callback_query(stats_filter)
def show_stats(_,query):
    country = query.data.split(":")[1]
    if country:
        query.edit_message_text("Processing!")
        a = r.get("https://api.thevirustracker.com/free-api?countryTotal={}".format(country))
        #a = a.text
        #a = a.replace("<br />\n<b>Warning</b>:  session_start(): open(/var/cpanel/php/sessions/ea-php72/sess_9c962023b9e3054cc3977e038435b451, O_RDWR) failed: No space left on device (28) in <b>/home/thevirustracker/api.thevirustracker.com/connections.php</b> on line <b>1</b><br />\n<br />\n<b>Warning</b>:  session_start(): Failed to read session data: files (path: /var/cpanel/php/sessions/ea-php72) in <b>/home/thevirustracker/api.thevirustracker.com/connections.php</b> on line <b>1</b><br />\n","")
        #a = json.loads(a)
        keyboard = []
        keyboard.append([InlineKeyboardButton("Delete",callback_data="exitnow")])
        reply_markup= InlineKeyboardMarkup(keyboard)
        try:
            data = re.search('"data":"(.+?)"',a.text)[1] == 'none'
        except:
            data = 0
        if data:
            query.edit_message_text("Currently no stats Available for that country",reply_markup = reply_markup)
        else:
            cn = re.search('"title":"(.+?)",',a.text)[1]
            total_cases = re.search('"total_cases":(.+?),',a.text)[1]
            total_recovered = re.search('"total_recovered":(.+?),',a.text)[1]
            total_unresolved = re.search('"total_unresolved":(.+?),',a.text)[1]
            total_deaths = re.search('"total_deaths":(.+?),',a.text)[1]
            new_cases_today = re.search('"total_new_cases_today":(.+?),',a.text)[1]
            deaths_today = re.search('"total_new_deaths_today":(.+?),',a.text)[1]
            text = "**{} Report**\n\n**Total Cases**: {}\n**Total Recovered**: {}\n**Total Unresolved**: {}\n**Total Deaths**: {}\n**New Cases Today**: {}\n**Deaths Today**: {}".format(cn,total_cases,total_recovered,total_unresolved,total_deaths,new_cases_today,deaths_today)
            query.edit_message_text(text,reply_markup=reply_markup)

@bot.on_callback_query(gauto_filter)
def group_auto_news(_,query):
    data = query.data.split(":")
    user = query.from_user.id
    chat = int(data[1])
    check = bot.get_chat_member(chat,user).status
    ison = int(data[2])
    if (check == 'administrator') or (check == 'creator'):
        update_news(chat,ison,'n')
        if ison:
            b = query.edit_message_text("Updates turned on Successfully\nThis group will receive news updates every 1.5 hrs")
            b = b.message_id
        else:
            b = query.edit_message_text("Updates turned off this group wont receive news updates anymore!")
            b = b.message_id
        time.sleep(7)
        bot.delete_messages(chat_id = chat, message_ids=b)
    else:
        query.answer("You aint allowed to touch it!!!")

@bot.on_callback_query(uauto_filter)
def user_auto_news(_,query):
    data = query.data.split(":")
    ison = int(data[1])
    user_id = query.from_user.id
    update_news(user_id,ison,'n')
    if ison:
        query.edit_message_text("Auto News Turned On\nYou will receive news updates every 1.5 hour")
    else:
        query.edit_message_text("Auto News Turned Off you wont receive news updates")

@bot.on_callback_query(add_country_filter)
def add_country_now(_,query):
    data = query.data.split(":")
    ctype = data[1]
    code = str(data[2]).lower()
    name = data[3]
    if ctype == 'g':
        chat_id = query.message.chat.id
        user = query.from_user.id
        check = bot.get_chat_member(chat_id,user).status
        if (check == 'administrator') or (check == 'creator'):
            try:
                a = check_news(chat_id)
            except:
                create_auto_news(chat_id)
                a = check_news(chat_id)
            c = a[3]
            if c and (c!= ''):
                a = "{}:{}".format(code,name)
                b = str(a) in str(c)
                if b:
                    z = query.answer("{} is already added in countries list!".format(name))
                    return ''
                else:
                    c = c+"{}:{},".format(code,name)
            else:
                c = '{}:{},'.format(code,name)
            update_news(chat_id,'n',c)
            b = query.edit_message_text("Done {} added in auto updates countries!".format(name))
            time.sleep(7)
            b = b.message_id
            bot.delete_messages(chat_id = chat_id,message_ids=b)
        else:
            query.answer("You aint allowed to touch me!")
    else:
        chat_id = query.message.chat.id
        user = query.from_user.id
        try:
            a = check_news(chat_id)
        except:
            create_auto_news(chat_id)
            a = check_news(chat_id)
        c = a[3]
        if c and (c!= ''):
            a = "{}:{}".format(code,name)
            b = str(a) in str(c)
            if b:
                query.answer("{} is already added in countries list!".format(name))
                return ''
            else:
                c = c+"{}:{},".format(code,name)
        else:
            c = '{}:{},'.format(code,name)
        update_news(chat_id,'n',c)
        query.edit_message_text("Done {} added in auto updates countries!".format(name))

@bot.on_callback_query(del_country_filter)
def del_country_now(_,query):
    data = query.data.split("|")
    chat_id = query.message.chat.id
    ctype = data[1]
    country= str(data[2])
    name = country.split(":")[1]
    if ctype == 'g':
        user = query.from_user.id
        check = bot.get_chat_member(chat_id,user).status
        if (check == 'administrator') or (check == 'creator'):
            try:
                a = check_news(chat_id)
            except:
                create_auto_news(chat_id)
                a = check_news(chat_id)
            c = a[3]
            if c and (c!= ''):
                if str(country) in c:
                    d = country+","
                    c = c.replace(d,"")
                    update_news(chat_id,'n',c)
                else:
                    pass
                b = query.edit_message_text("Done {} removed from auto updates countries!".format(name))
                print("\n\n\n\n{}\n\n\n\n".format(b))
                time.sleep(7)
                b = b.message_id
                bot.delete_messages(chat_id = chat_id,message_ids=b)
        else:
            query.answer("You aint allowed to do that!")
    else:
        try:
            a = check_news(chat_id)
        except:
            create_auto_news(chat_id)
            a = check_news(chat_id)
        c = a[3]
        if c and (c!= ''):
            if str(country) in c:
                d = country+","
                c = c.replace(d,"")
                update_news(chat_id,'n',c)
            else:
                pass
            query.edit_message_text("Done {} removed from auto updates countries!".format(name))

@bot.on_callback_query(autonewsdelete_filter)
def autodeletemnewsnow(_,query): 
    supergroup = query.message.chat.type == 'supergroup'
    groups = query.message.chat.type == 'group'
    chat_id = query.message.chat.id
    user = query.from_user.id
    if (supergroup) or (groups):
        check = bot.get_chat_member(chat_id,user).status
        if (check == 'administrator') or (check == 'creator'):
            messageid = query.message.message_id
            bot.delete_messages(chat_id = chat_id, message_ids=messageid)
        else:
            query.answer("You aint allowed to use this button!")
    else:
        messageid = query.message.message_id
        bot.delete_messages(chat_id = chat_id, message_ids=messageid)
t1 = Thread(target = start_schedule)
t1.start()
bot.run()
print("Bot shutting Down")

print("Cursor Closed")
db.commit()
print("Commited Db")

print("Db conn closed")

'''
#🦠🦠🦠🦠🦠🦠'''
