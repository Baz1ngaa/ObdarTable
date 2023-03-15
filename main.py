
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text 
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
from os import getenv
from sys import exit
import aiogram.utils.markdown as fmt
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
import asyncio
from docx import Document
from docx.shared import Inches
from sqlite import db_start, create_profile, edit_profile
import sqlite3
import os
import olefile



API_TOKEN = '5914668302:AAEYN4cPDQvI3_9CWCKwLHSzwmhkhXLBfZM'
#5877501026:AAFdnaKLklAtL6fqvP3JQAa5ol5wwlPttM0 test
#5914668302:AAEYN4cPDQvI3_9CWCKwLHSzwmhkhXLBfZM main
 
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
available_region = ["Київ (GMT+2)", "Європа (GMT+1)"]
available_klass = ["8А", "8Б", "9А", "9Б", "10А", "10Б", "10В", "11А", "11Б", "11В"]
available_lessons = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця"]
class student(StatesGroup):
    waiting_for_region = State()
    waiting_for_klass = State()
    ready=State()
    waiting_for_table=State()
    waiting_for_gettable=State()
db=sqlite3.connect('telbot.db')
sql=db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS profileTel (
    login TEXT,
    region TEXT,
    klass TEXT)""")
db.commit()


def textget():
    import docx
    from docx import Document
    from docx.shared import Inches
    doc = docx.Document("lesson.docx")
    columnsName=''
    Table={}       
    WeekDays=['monday', 'tuesday', 'wednesday', 'thursday','friday']  
    i=-1      
    for table in doc.tables:
        for row in table.columns:
            for cell in row.cells:
                if(cell.text=='8-А'):
                    columnsName='8-А'
                    i=0
                if(cell.text=='8-Б'):
                    columnsName='8-Б'
                    i=0
                if(cell.text=='9-А'):
                    columnsName='9-А'
                    i=0
                if(cell.text=='9-Б'):
                    columnsName='9-Б'
                    i=0
                if(cell.text=='10-А'):
                    columnsName='10-А'
                    i=0
                if(cell.text=='10-Б'):
                    columnsName='10-Б'
                    i=0
        
                if(cell.text=='10-В'):
                    columnsName='10-В'
                    i=0
                if(cell.text=='11-А'):
                    columnsName='11-А'
                    i=0
                if(cell.text=='11-Б'):
                    columnsName='11-Б'
                    i=0
                if(cell.text=='11-В'):
                    columnsName='11-В'
                    i=0
                if(i==-1):
                        continue
                classList=Table.get(columnsName)
                nDay=i//10
                if(classList==None):
                        Table.update({columnsName: {}})        
                else:
                        currentDay=WeekDays[nDay]
                        dayList=classList.get(currentDay)
                        textTable=cell.text.replace("\n", "")
                        if(dayList==None):
                                classList.update({currentDay: [textTable]})
                        else:
                                dayList.append(cell.text)
                                classList.update({currentDay: dayList})
                        Table.update({columnsName: classList})
                        i=i+1
                
     
    for key, classList in Table.items():
        for keyDay, dayList in classList.items():
            for i in range(len(dayList)):
                if(dayList[i]==''):
                        dayList[i]="Вiкно"
                        
                changeN=dayList[i]
                changeN=changeN.replace("\n","")
                dayList[i]=changeN

    return(Table)
    


async def cmd_start(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for region in available_region:
        keyboard.add(region)
    await message.answer(f"Привіт, {message.from_user.full_name}, я допоможу тобі з розкладом. Для початку вибери часовий пояс:", reply_markup=keyboard)
    await state.set_state(student.waiting_for_region.state)
    global user_id
    user_id=message.from_user.id
    
    

   


async def region_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_region=message.text.lower())
    global user_region
    user_region=message.text.lower()
    sql.execute(f'UPDATE profileTel SET region = "{user_region}" WHERE login = "{user_id}"')
    db.commit()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for klass in available_klass:
        keyboard.add(klass)
    await message.answer("Тепер вибери свій клас:", reply_markup=keyboard)
    await state.set_state(student.waiting_for_klass.state)
    

async def klass_chosen(message: types.Message, state: FSMContext):

    await state.update_data(chosen_klass=message.text.lower())
    global user_klass
    user_klass=message.text.lower()
    sql.execute(f'UPDATE profileTel SET klass = "{user_klass}" WHERE login = "{user_id}"')
    db.commit()
    user_data = await state.get_data()
    await message.answer("Добре, для продовження натисніть /getTable ")
    await state.set_state(student.waiting_for_gettable.state)


    
async def get_table(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for lesson in available_lessons:
        keyboard.add(lesson)
    await message.answer("Тепер вибери день тижня:", reply_markup=keyboard)
    await state.set_state(student.waiting_for_table.state)
    user_id=message.from_user.id
    sql.execute(f"SELECT login FROM profileTel WHERE login = '{user_id}'")
    if sql.fetchone() is None:
        sql.execute(f"INSERT INTO profileTel VALUES (?,?,?)", (user_id, user_region, user_klass))
        db.commit()

    

async def waiting_table(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    TableFinish=textget()
    sql.execute(f"SELECT region, klass FROM profileTel WHERE login= '{message.from_user.id}' ")
    region, klass=sql.fetchone()
    if ( region== 'київ (gmt+2)'):
        if ( klass== '8а'):
            if(message.text=="Понеділок"):
                await message.answer(f" 1.{TableFinish.get('8-А').get('monday')[0]}(9:25-10:10) \n2.{TableFinish.get('8-А').get('monday')[1]}(10:25-11:10) \n3.{TableFinish.get('8-А').get('monday')[2]}(11:25-12:10) \n4.{TableFinish.get('8-А').get('monday')[3]}(12:20-13:05) \n5.{TableFinish.get('8-А').get('monday')[4]}(13:30-14:15) \n6.{TableFinish.get('8-А').get('monday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('8-А').get('monday')[6]}(16:00-16:45) \n8.{TableFinish.get('8-А').get('monday')[7]}(16:55-17:40) \n9.{TableFinish.get('8-А').get('monday')[8]}(17:50-18:35) \n10.{TableFinish.get('8-А').get('monday')[9]}(18:45-19:30) ")
            if(message.text=="Вівторок"):
                await message.answer(f" 1.{TableFinish.get('8-А').get('tuesday')[0]}(9:25-10:10) \n2.{TableFinish.get('8-А').get('tuesday')[1]}(10:25-11:10) \n3.{TableFinish.get('8-А').get('tuesday')[2]}(11:25-12:10) \n4.{TableFinish.get('8-А').get('tuesday')[3]}(12:20-13:05) \n5.{TableFinish.get('8-А').get('tuesday')[4]}(13:30-14:15) \n6.{TableFinish.get('8-А').get('tuesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('8-А').get('tuesday')[6]}(16:00-16:45) \n8.{TableFinish.get('8-А').get('tuesday')[7]}(16:55-17:40) \n9.{TableFinish.get('8-А').get('tuesday')[8]}(17:50-18:35) \n10.{TableFinish.get('8-А').get('tuesday')[9]}(18:45-19:30) ")
            if(message.text=="Середа"):
                await message.answer(f" 1.{TableFinish.get('8-А').get('wednesday')[0]}(9:25-10:10) \n2.{TableFinish.get('8-А').get('wednesday')[1]}(10:25-11:10) \n3.{TableFinish.get('8-А').get('wednesday')[2]}(11:25-12:10) \n4.{TableFinish.get('8-А').get('wednesday')[3]}(12:20-13:05) \n5.{TableFinish.get('8-А').get('wednesday')[4]}(13:30-14:15) \n6.{TableFinish.get('8-А').get('wednesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('8-А').get('wednesday')[6]}(16:00-16:45) \n8.{TableFinish.get('8-А').get('wednesday')[7]}(16:55-17:40) \n9.{TableFinish.get('8-А').get('wednesday')[8]}(17:50-18:35) \n10.{TableFinish.get('8-А').get('wednesday')[9]}(18:45-19:30) ")
            if(message.text=="Четвер"):
                await message.answer(f" 1.{TableFinish.get('8-А').get('thursday')[0]}(9:25-10:10) \n2.{TableFinish.get('8-А').get('thursday')[1]}(10:25-11:10) \n3.{TableFinish.get('8-А').get('thursday')[2]}(11:25-12:10) \n4.{TableFinish.get('8-А').get('thursday')[3]}(12:20-13:05) \n5.{TableFinish.get('8-А').get('thursday')[4]}(13:30-14:15) \n6.{TableFinish.get('8-А').get('thursday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('8-А').get('thursday')[6]}(16:00-16:45) \n8.{TableFinish.get('8-А').get('thursday')[7]}(16:55-17:40) \n9.{TableFinish.get('8-А').get('thursday')[8]}(17:50-18:35) \n10.{TableFinish.get('8-А').get('thursday')[9]}(18:45-19:30) ")
            if(message.text=="П'ятниця"):
                await message.answer(f" 1.{TableFinish.get('8-А').get('friday')[0]}(9:25-10:10) \n2.{TableFinish.get('8-А').get('friday')[1]}(10:25-11:10) \n3.{TableFinish.get('8-А').get('friday')[2]}(11:25-12:10) \n4.{TableFinish.get('8-А').get('friday')[3]}(12:20-13:05) \n5.{TableFinish.get('8-А').get('friday')[4]}(13:30-14:15) \n6.{TableFinish.get('8-А').get('friday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('8-А').get('friday')[6]}(16:00-16:45) \n8.{TableFinish.get('8-А').get('friday')[7]}(16:55-17:40) \n9.{TableFinish.get('8-А').get('friday')[8]}(17:50-18:35) \n10.{TableFinish.get('8-А').get('friday')[9]}(18:45-19:30) ")
        if ( klass== '8б'):
           if(message.text=="Понеділок"):
               await message.answer(f" 1.{TableFinish.get('8-Б').get('monday')[0]}(9:25-10:10) \n2.{TableFinish.get('8-Б').get('monday')[1]}(10:25-11:10) \n3.{TableFinish.get('8-Б').get('monday')[2]}(11:25-12:10) \n4.{TableFinish.get('8-Б').get('monday')[3]}(12:20-13:05) \n5.{TableFinish.get('8-Б').get('monday')[4]}(13:30-14:15) \n6.{TableFinish.get('8-Б').get('monday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('8-Б').get('monday')[6]}(16:00-16:45) \n8.{TableFinish.get('8-Б').get('monday')[7]}(16:55-17:40) \n9.{TableFinish.get('8-Б').get('monday')[8]}(17:50-18:35) \n10.{TableFinish.get('8-Б').get('monday')[9]}(18:45-19:30) ")
           if(message.text=="Вівторок"):
               await message.answer(f" 1.{TableFinish.get('8-Б').get('tuesday')[0]}(9:25-10:10) \n2.{TableFinish.get('8-Б').get('tuesday')[1]}(10:25-11:10) \n3.{TableFinish.get('8-Б').get('tuesday')[2]}(11:25-12:10) \n4.{TableFinish.get('8-Б').get('tuesday')[3]}(12:20-13:05) \n5.{TableFinish.get('8-Б').get('tuesday')[4]}(13:30-14:15) \n6.{TableFinish.get('8-Б').get('tuesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('8-Б').get('tuesday')[6]}(16:00-16:45) \n8.{TableFinish.get('8-Б').get('tuesday')[7]}(16:55-17:40) \n9.{TableFinish.get('8-Б').get('tuesday')[8]}(17:50-18:35) \n10.{TableFinish.get('8-Б').get('tuesday')[9]}(18:45-19:30) ")
           if(message.text=="Середа"):
               await message.answer(f" 1.{TableFinish.get('8-Б').get('wednesday')[0]}(9:25-10:10) \n2.{TableFinish.get('8-Б').get('wednesday')[1]}(10:25-11:10) \n3.{TableFinish.get('8-Б').get('wednesday')[2]}(11:25-12:10) \n4.{TableFinish.get('8-Б').get('wednesday')[3]}(12:20-13:05) \n5.{TableFinish.get('8-Б').get('wednesday')[4]}(13:30-14:15) \n6.{TableFinish.get('8-Б').get('wednesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('8-Б').get('wednesday')[6]}(16:00-16:45) \n8.{TableFinish.get('8-Б').get('wednesday')[7]}(16:55-17:40) \n9.{TableFinish.get('8-Б').get('wednesday')[8]}(17:50-18:35) \n10.{TableFinish.get('8-Б').get('wednesday')[9]}(18:45-19:30) ")
           if(message.text=="Четвер"):
               await message.answer(f" 1.{TableFinish.get('8-Б').get('thursday')[0]}(9:25-10:10) \n2.{TableFinish.get('8-Б').get('thursday')[1]}(10:25-11:10) \n3.{TableFinish.get('8-Б').get('thursday')[2]}(11:25-12:10) \n4.{TableFinish.get('8-Б').get('thursday')[3]}(12:20-13:05) \n5.{TableFinish.get('8-Б').get('thursday')[4]}(13:30-14:15) \n6.{TableFinish.get('8-Б').get('thursday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('8-Б').get('thursday')[6]}(16:00-16:45) \n8.{TableFinish.get('8-Б').get('thursday')[7]}(16:55-17:40) \n9.{TableFinish.get('8-Б').get('thursday')[8]}(17:50-18:35) \n10.{TableFinish.get('8-Б').get('thursday')[9]}(18:45-19:30) ")
           if(message.text=="П'ятниця"):
               await message.answer(f" 1.{TableFinish.get('8-Б').get('friday')[0]}(9:25-10:10) \n2.{TableFinish.get('8-Б').get('friday')[1]}(10:25-11:10) \n3.{TableFinish.get('8-Б').get('friday')[2]}(11:25-12:10) \n4.{TableFinish.get('8-Б').get('friday')[3]}(12:20-13:05) \n5.{TableFinish.get('8-Б').get('friday')[4]}(13:30-14:15) \n6.{TableFinish.get('8-Б').get('friday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('8-Б').get('friday')[6]}(16:00-16:45) \n8.{TableFinish.get('8-Б').get('friday')[7]}(16:55-17:40) \n9.{TableFinish.get('8-Б').get('friday')[8]}(17:50-18:35) \n10.{TableFinish.get('8-Б').get('friday')[9]}(18:45-19:30) ")


        if ( klass== '9а'):
           if(message.text=="Понеділок"):
               await message.answer(f" 1.{TableFinish.get('9-А').get('monday')[0]}(9:25-10:10) \n2.{TableFinish.get('9-А').get('monday')[1]}(10:25-11:10) \n3.{TableFinish.get('9-А').get('monday')[2]}(11:25-12:10) \n4.{TableFinish.get('9-А').get('monday')[3]}(12:20-13:05) \n5.{TableFinish.get('9-А').get('monday')[4]}(13:30-14:15) \n6.{TableFinish.get('9-А').get('monday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('9-А').get('monday')[6]}(16:00-16:45) \n8.{TableFinish.get('9-А').get('monday')[7]}(16:55-17:40) \n9.{TableFinish.get('9-А').get('monday')[8]}(17:50-18:35) \n10.{TableFinish.get('9-А').get('monday')[9]}(18:45-19:30) ")
           if(message.text=="Вівторок"):
               await message.answer(f" 1.{TableFinish.get('9-А').get('tuesday')[0]}(9:25-10:10) \n2.{TableFinish.get('9-А').get('tuesday')[1]}(10:25-11:10) \n3.{TableFinish.get('9-А').get('tuesday')[2]}(11:25-12:10) \n4.{TableFinish.get('9-А').get('tuesday')[3]}(12:20-13:05) \n5.{TableFinish.get('9-А').get('tuesday')[4]}(13:30-14:15) \n6.{TableFinish.get('9-А').get('tuesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('9-А').get('tuesday')[6]}(16:00-16:45) \n8.{TableFinish.get('9-А').get('tuesday')[7]}(16:55-17:40) \n9.{TableFinish.get('9-А').get('tuesday')[8]}(17:50-18:35) \n10.{TableFinish.get('9-А').get('tuesday')[9]}(18:45-19:30) ")
           if(message.text=="Середа"):
               await message.answer(f" 1.{TableFinish.get('9-А').get('wednesday')[0]}(9:25-10:10) \n2.{TableFinish.get('9-А').get('wednesday')[1]}(10:25-11:10) \n3.{TableFinish.get('9-А').get('wednesday')[2]}(11:25-12:10) \n4.{TableFinish.get('9-А').get('wednesday')[3]}(12:20-13:05) \n5.{TableFinish.get('9-А').get('wednesday')[4]}(13:30-14:15) \n6.{TableFinish.get('9-А').get('wednesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('9-А').get('wednesday')[6]}(16:00-16:45) \n8.{TableFinish.get('9-А').get('wednesday')[7]}(16:55-17:40) \n9.{TableFinish.get('9-А').get('wednesday')[8]}(17:50-18:35) \n10.{TableFinish.get('9-А').get('wednesday')[9]}(18:45-19:30) ")
           if(message.text=="Четвер"):
               await message.answer(f" 1.{TableFinish.get('9-А').get('thursday')[0]}(9:25-10:10) \n2.{TableFinish.get('9-А').get('thursday')[1]}(10:25-11:10) \n3.{TableFinish.get('9-А').get('thursday')[2]}(11:25-12:10) \n4.{TableFinish.get('9-А').get('thursday')[3]}(12:20-13:05) \n5.{TableFinish.get('9-А').get('thursday')[4]}(13:30-14:15) \n6.{TableFinish.get('9-А').get('thursday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('9-А').get('thursday')[6]}(16:00-16:45) \n8.{TableFinish.get('9-А').get('thursday')[7]}(16:55-17:40) \n9.{TableFinish.get('9-А').get('thursday')[8]}(17:50-18:35) \n10.{TableFinish.get('9-А').get('thursday')[9]}(18:45-19:30) ")
           if(message.text=="П'ятниця"):
               await message.answer(f" 1.{TableFinish.get('9-А').get('friday')[0]}(9:25-10:10) \n2.{TableFinish.get('9-А').get('friday')[1]}(10:25-11:10) \n3.{TableFinish.get('9-А').get('friday')[2]}(11:25-12:10) \n4.{TableFinish.get('9-А').get('friday')[3]}(12:20-13:05) \n5.{TableFinish.get('9-А').get('friday')[4]}(13:30-14:15) \n6.{TableFinish.get('9-А').get('friday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('9-А').get('friday')[6]}(16:00-16:45) \n8.{TableFinish.get('9-А').get('friday')[7]}(16:55-17:40) \n9.{TableFinish.get('9-А').get('friday')[8]}(17:50-18:35) \n10.{TableFinish.get('9-А').get('friday')[9]}(18:45-19:30) ")


        if ( klass== '9б'):
           if(message.text=="Понеділок"):
               await message.answer(f" 1.{TableFinish.get('9-Б').get('monday')[0]}(9:25-10:10) \n2.{TableFinish.get('9-Б').get('monday')[1]}(10:25-11:10) \n3.{TableFinish.get('9-Б').get('monday')[2]}(11:25-12:10) \n4.{TableFinish.get('9-Б').get('monday')[3]}(12:20-13:05) \n5.{TableFinish.get('9-Б').get('monday')[4]}(13:30-14:15) \n6.{TableFinish.get('9-Б').get('monday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('9-Б').get('monday')[6]}(16:00-16:45) \n8.{TableFinish.get('9-Б').get('monday')[7]}(16:55-17:40) \n9.{TableFinish.get('9-Б').get('monday')[8]}(17:50-18:35) \n10.{TableFinish.get('9-Б').get('monday')[9]}(18:45-19:30) ")
           if(message.text=="Вівторок"):
               await message.answer(f" 1.{TableFinish.get('9-Б').get('tuesday')[0]}(9:25-10:10) \n2.{TableFinish.get('9-Б').get('tuesday')[1]}(10:25-11:10) \n3.{TableFinish.get('9-Б').get('tuesday')[2]}(11:25-12:10) \n4.{TableFinish.get('9-Б').get('tuesday')[3]}(12:20-13:05) \n5.{TableFinish.get('9-Б').get('tuesday')[4]}(13:30-14:15) \n6.{TableFinish.get('9-Б').get('tuesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('9-Б').get('tuesday')[6]}(16:00-16:45) \n8.{TableFinish.get('9-Б').get('tuesday')[7]}(16:55-17:40) \n9.{TableFinish.get('9-Б').get('tuesday')[8]}(17:50-18:35) \n10.{TableFinish.get('9-Б').get('tuesday')[9]}(18:45-19:30) ")
           if(message.text=="Середа"):
               await message.answer(f" 1.{TableFinish.get('9-Б').get('wednesday')[0]}(9:25-10:10) \n2.{TableFinish.get('9-Б').get('wednesday')[1]}(10:25-11:10) \n3.{TableFinish.get('9-Б').get('wednesday')[2]}(11:25-12:10) \n4.{TableFinish.get('9-Б').get('wednesday')[3]}(12:20-13:05) \n5.{TableFinish.get('9-Б').get('wednesday')[4]}(13:30-14:15) \n6.{TableFinish.get('9-Б').get('wednesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('9-Б').get('wednesday')[6]}(16:00-16:45) \n8.{TableFinish.get('9-Б').get('wednesday')[7]}(16:55-17:40) \n9.{TableFinish.get('9-Б').get('wednesday')[8]}(17:50-18:35) \n10.{TableFinish.get('9-Б').get('wednesday')[9]}(18:45-19:30) ")
           if(message.text=="Четвер"):
               await message.answer(f" 1.{TableFinish.get('9-Б').get('thursday')[0]}(9:25-10:10) \n2.{TableFinish.get('9-Б').get('thursday')[1]}(10:25-11:10) \n3.{TableFinish.get('9-Б').get('thursday')[2]}(11:25-12:10) \n4.{TableFinish.get('9-Б').get('thursday')[3]}(12:20-13:05) \n5.{TableFinish.get('9-Б').get('thursday')[4]}(13:30-14:15) \n6.{TableFinish.get('9-Б').get('thursday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('9-Б').get('thursday')[6]}(16:00-16:45) \n8.{TableFinish.get('9-Б').get('thursday')[7]}(16:55-17:40) \n9.{TableFinish.get('9-Б').get('thursday')[8]}(17:50-18:35) \n10.{TableFinish.get('9-Б').get('thursday')[9]}(18:45-19:30) ")
           if(message.text=="П'ятниця"):
               await message.answer(f" 1.{TableFinish.get('9-Б').get('friday')[0]}(9:25-10:10) \n2.{TableFinish.get('9-Б').get('friday')[1]}(10:25-11:10) \n3.{TableFinish.get('9-Б').get('friday')[2]}(11:25-12:10) \n4.{TableFinish.get('9-Б').get('friday')[3]}(12:20-13:05) \n5.{TableFinish.get('9-Б').get('friday')[4]}(13:30-14:15) \n6.{TableFinish.get('9-Б').get('friday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('9-Б').get('friday')[6]}(16:00-16:45) \n8.{TableFinish.get('9-Б').get('friday')[7]}(16:55-17:40) \n9.{TableFinish.get('9-Б').get('friday')[8]}(17:50-18:35) \n10.{TableFinish.get('9-Б').get('friday')[9]}(18:45-19:30) ")

        if ( klass== '10а'):
           if(message.text=="Понеділок"):
               await message.answer(f" 1.{TableFinish.get('10-А').get('monday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-А').get('monday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-А').get('monday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-А').get('monday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-А').get('monday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-А').get('monday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-А').get('monday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-А').get('monday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-А').get('monday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-А').get('monday')[9]}(18:45-19:30) ")
           if(message.text=="Вівторок"):
               await message.answer(f" 1.{TableFinish.get('10-А').get('tuesday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-А').get('tuesday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-А').get('tuesday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-А').get('tuesday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-А').get('tuesday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-А').get('tuesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-А').get('tuesday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-А').get('tuesday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-А').get('tuesday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-А').get('tuesday')[9]}(18:45-19:30) ")
           if(message.text=="Середа"):
               await message.answer(f" 1.{TableFinish.get('10-А').get('wednesday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-А').get('wednesday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-А').get('wednesday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-А').get('wednesday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-А').get('wednesday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-А').get('wednesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-А').get('wednesday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-А').get('wednesday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-А').get('wednesday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-А').get('wednesday')[9]}(18:45-19:30) ")
           if(message.text=="Четвер"):
               await message.answer(f" 1.{TableFinish.get('10-А').get('thursday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-А').get('thursday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-А').get('thursday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-А').get('thursday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-А').get('thursday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-А').get('thursday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-А').get('thursday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-А').get('thursday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-А').get('thursday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-А').get('thursday')[9]}(18:45-19:30) ")
           if(message.text=="П'ятниця"):
               await message.answer(f" 1.{TableFinish.get('10-А').get('friday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-А').get('friday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-А').get('friday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-А').get('friday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-А').get('friday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-А').get('friday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-А').get('friday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-А').get('friday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-А').get('friday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-А').get('friday')[9]}(18:45-19:30) ")


        if ( klass== '10б'):
           if(message.text=="Понеділок"):
               await message.answer(f" 1.{TableFinish.get('10-Б').get('monday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-Б').get('monday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-Б').get('monday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-Б').get('monday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-Б').get('monday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-Б').get('monday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-Б').get('monday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-Б').get('monday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-Б').get('monday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-Б').get('monday')[9]}(18:45-19:30) ")
           if(message.text=="Вівторок"):
               await message.answer(f" 1.{TableFinish.get('10-Б').get('tuesday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-Б').get('tuesday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-Б').get('tuesday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-Б').get('tuesday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-Б').get('tuesday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-Б').get('tuesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-Б').get('tuesday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-Б').get('tuesday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-Б').get('tuesday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-Б').get('tuesday')[9]}(18:45-19:30) ")
           if(message.text=="Середа"):
               await message.answer(f" 1.{TableFinish.get('10-Б').get('wednesday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-Б').get('wednesday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-Б').get('wednesday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-Б').get('wednesday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-Б').get('wednesday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-Б').get('wednesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-Б').get('wednesday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-Б').get('wednesday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-Б').get('wednesday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-Б').get('wednesday')[9]}(18:45-19:30) ")
           if(message.text=="Четвер"):
               await message.answer(f" 1.{TableFinish.get('10-Б').get('thursday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-Б').get('thursday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-Б').get('thursday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-Б').get('thursday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-Б').get('thursday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-Б').get('thursday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-Б').get('thursday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-Б').get('thursday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-Б').get('thursday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-Б').get('thursday')[9]}(18:45-19:30) ")
           if(message.text=="П'ятниця"):
               await message.answer(f" 1.{TableFinish.get('10-Б').get('friday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-Б').get('friday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-Б').get('friday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-Б').get('friday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-Б').get('friday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-Б').get('friday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-Б').get('friday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-Б').get('friday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-Б').get('friday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-Б').get('friday')[9]}(18:45-19:30) ")


        if ( klass== '10в'):
           if(message.text=="Понеділок"):
               await message.answer(f" 1.{TableFinish.get('10-В').get('monday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-В').get('monday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-В').get('monday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-В').get('monday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-В').get('monday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-В').get('monday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-В').get('monday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-В').get('monday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-В').get('monday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-В').get('monday')[9]}(18:45-19:30) ")
           if(message.text=="Вівторок"):
               await message.answer(f" 1.{TableFinish.get('10-В').get('tuesday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-В').get('tuesday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-В').get('tuesday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-В').get('tuesday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-В').get('tuesday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-В').get('tuesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-В').get('tuesday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-В').get('tuesday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-В').get('tuesday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-В').get('tuesday')[9]}(18:45-19:30) ")
           if(message.text=="Середа"):
               await message.answer(f" 1.{TableFinish.get('10-В').get('wednesday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-В').get('wednesday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-В').get('wednesday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-В').get('wednesday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-В').get('wednesday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-В').get('wednesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-В').get('wednesday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-В').get('wednesday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-В').get('wednesday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-В').get('wednesday')[9]}(18:45-19:30) ")
           if(message.text=="Четвер"):
               await message.answer(f" 1.{TableFinish.get('10-В').get('thursday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-В').get('thursday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-В').get('thursday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-В').get('thursday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-В').get('thursday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-В').get('thursday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-В').get('thursday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-В').get('thursday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-В').get('thursday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-В').get('thursday')[9]}(18:45-19:30) ")
           if(message.text=="П'ятниця"):
               await message.answer(f" 1.{TableFinish.get('10-В').get('friday')[0]}(9:25-10:10) \n2.{TableFinish.get('10-В').get('friday')[1]}(10:25-11:10) \n3.{TableFinish.get('10-В').get('friday')[2]}(11:25-12:10) \n4.{TableFinish.get('10-В').get('friday')[3]}(12:20-13:05) \n5.{TableFinish.get('10-В').get('friday')[4]}(13:30-14:15) \n6.{TableFinish.get('10-В').get('friday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('10-В').get('friday')[6]}(16:00-16:45) \n8.{TableFinish.get('10-В').get('friday')[7]}(16:55-17:40) \n9.{TableFinish.get('10-В').get('friday')[8]}(17:50-18:35) \n10.{TableFinish.get('10-В').get('friday')[9]}(18:45-19:30) ")


        if ( klass== '11а'):
           if(message.text=="Понеділок"):
               await message.answer(f" 1.{TableFinish.get('11-А').get('monday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-А').get('monday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-А').get('monday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-А').get('monday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-А').get('monday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-А').get('monday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-А').get('monday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-А').get('monday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-А').get('monday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-А').get('monday')[9]}(18:45-19:30) ")
           if(message.text=="Вівторок"):
               await message.answer(f" 1.{TableFinish.get('11-А').get('tuesday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-А').get('tuesday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-А').get('tuesday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-А').get('tuesday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-А').get('tuesday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-А').get('tuesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-А').get('tuesday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-А').get('tuesday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-А').get('tuesday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-А').get('tuesday')[9]}(18:45-19:30) ")
           if(message.text=="Середа"):
               await message.answer(f" 1.{TableFinish.get('11-А').get('wednesday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-А').get('wednesday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-А').get('wednesday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-А').get('wednesday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-А').get('wednesday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-А').get('wednesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-А').get('wednesday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-А').get('wednesday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-А').get('wednesday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-А').get('wednesday')[9]}(18:45-19:30) ")
           if(message.text=="Четвер"):
               await message.answer(f" 1.{TableFinish.get('11-А').get('thursday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-А').get('thursday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-А').get('thursday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-А').get('thursday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-А').get('thursday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-А').get('thursday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-А').get('thursday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-А').get('thursday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-А').get('thursday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-А').get('thursday')[9]}(18:45-19:30) ")
           if(message.text=="П'ятниця"):
               await message.answer(f" 1.{TableFinish.get('11-А').get('friday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-А').get('friday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-А').get('friday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-А').get('friday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-А').get('friday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-А').get('friday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-А').get('friday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-А').get('friday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-А').get('friday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-А').get('friday')[9]}(18:45-19:30) ")


        if ( klass== '11б'):
           if(message.text=="Понеділок"):
               await message.answer(f" 1.{TableFinish.get('11-Б').get('monday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-Б').get('monday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-Б').get('monday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-Б').get('monday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-Б').get('monday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-Б').get('monday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-Б').get('monday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-Б').get('monday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-Б').get('monday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-Б').get('monday')[9]}(18:45-19:30) ")
           if(message.text=="Вівторок"):
               await message.answer(f" 1.{TableFinish.get('11-Б').get('tuesday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-Б').get('tuesday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-Б').get('tuesday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-Б').get('tuesday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-Б').get('tuesday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-Б').get('tuesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-Б').get('tuesday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-Б').get('tuesday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-Б').get('tuesday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-Б').get('tuesday')[9]}(18:45-19:30) ")
           if(message.text=="Середа"):
               await message.answer(f" 1.{TableFinish.get('11-Б').get('wednesday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-Б').get('wednesday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-Б').get('wednesday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-Б').get('wednesday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-Б').get('wednesday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-Б').get('wednesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-Б').get('wednesday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-Б').get('wednesday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-Б').get('wednesday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-Б').get('wednesday')[9]}(18:45-19:30) ")
           if(message.text=="Четвер"):
               await message.answer(f" 1.{TableFinish.get('11-Б').get('thursday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-Б').get('thursday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-Б').get('thursday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-Б').get('thursday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-Б').get('thursday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-Б').get('thursday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-Б').get('thursday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-Б').get('thursday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-Б').get('thursday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-Б').get('thursday')[9]}(18:45-19:30) ")
           if(message.text=="П'ятниця"):
               await message.answer(f" 1.{TableFinish.get('11-Б').get('friday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-Б').get('friday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-Б').get('friday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-Б').get('friday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-Б').get('friday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-Б').get('friday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-Б').get('friday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-Б').get('friday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-Б').get('friday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-Б').get('friday')[9]}(18:45-19:30) ")


        if ( klass== '11в'):
           if(message.text=="Понеділок"):
               await message.answer(f" 1.{TableFinish.get('11-В').get('monday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-В').get('monday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-В').get('monday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-В').get('monday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-В').get('monday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-В').get('monday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-В').get('monday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-В').get('monday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-В').get('monday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-В').get('monday')[9]}(18:45-19:30) ")
           if(message.text=="Вівторок"):
               await message.answer(f" 1.{TableFinish.get('11-В').get('tuesday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-В').get('tuesday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-В').get('tuesday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-В').get('tuesday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-В').get('tuesday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-В').get('tuesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-В').get('tuesday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-В').get('tuesday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-В').get('tuesday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-В').get('tuesday')[9]}(18:45-19:30) ")
           if(message.text=="Середа"):
               await message.answer(f" 1.{TableFinish.get('11-В').get('wednesday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-В').get('wednesday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-В').get('wednesday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-В').get('wednesday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-В').get('wednesday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-В').get('wednesday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-В').get('wednesday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-В').get('wednesday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-В').get('wednesday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-В').get('wednesday')[9]}(18:45-19:30) ")
           if(message.text=="Четвер"):
               await message.answer(f" 1.{TableFinish.get('11-В').get('thursday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-В').get('thursday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-В').get('thursday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-В').get('thursday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-В').get('thursday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-В').get('thursday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-В').get('thursday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-В').get('thursday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-В').get('thursday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-В').get('thursday')[9]}(18:45-19:30) ")
           if(message.text=="П'ятниця"):
               await message.answer(f" 1.{TableFinish.get('11-В').get('friday')[0]}(9:25-10:10) \n2.{TableFinish.get('11-В').get('friday')[1]}(10:25-11:10) \n3.{TableFinish.get('11-В').get('friday')[2]}(11:25-12:10) \n4.{TableFinish.get('11-В').get('friday')[3]}(12:20-13:05) \n5.{TableFinish.get('11-В').get('friday')[4]}(13:30-14:15) \n6.{TableFinish.get('11-В').get('friday')[5]}(14:25-15:10) \n \n7.{TableFinish.get('11-В').get('friday')[6]}(16:00-16:45) \n8.{TableFinish.get('11-В').get('friday')[7]}(16:55-17:40) \n9.{TableFinish.get('11-В').get('friday')[8]}(17:50-18:35) \n10.{TableFinish.get('11-В').get('friday')[9]}(18:45-19:30) ")


    if ( region== 'європа (gmt+1)'):
       if ( klass== '8а'):
           if(message.text=="Понеділок"):
               await message.answer(f" 1.{TableFinish.get('8-А').get('monday')[0]}(8:25-9:10) \n2.{TableFinish.get('8-А').get('monday')[1]}(9:25-10:10) \n3.{TableFinish.get('8-А').get('monday')[2]}(10:25-11:10) \n4.{TableFinish.get('8-А').get('monday')[3]}(11:20-12:05) \n5.{TableFinish.get('8-А').get('monday')[4]}(12:30-13:15) \n6.{TableFinish.get('8-А').get('monday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('8-А').get('monday')[6]}(15:00-15:45) \n8.{TableFinish.get('8-А').get('monday')[7]}(15:55-16:40) \n9.{TableFinish.get('8-А').get('monday')[8]}(16:50-17:35) \n10.{TableFinish.get('8-А').get('monday')[9]}(17:45-18:30) ")
           if(message.text=="Вівторок"):
               await message.answer(f" 1.{TableFinish.get('8-А').get('tuesday')[0]}(8:25-9:10) \n2.{TableFinish.get('8-А').get('tuesday')[1]}(9:25-10:10) \n3.{TableFinish.get('8-А').get('tuesday')[2]}(10:25-11:10) \n4.{TableFinish.get('8-А').get('tuesday')[3]}(11:20-12:05) \n5.{TableFinish.get('8-А').get('tuesday')[4]}(12:30-13:15) \n6.{TableFinish.get('8-А').get('tuesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('8-А').get('tuesday')[6]}(15:00-15:45) \n8.{TableFinish.get('8-А').get('tuesday')[7]}(15:55-16:40) \n9.{TableFinish.get('8-А').get('tuesday')[8]}(16:50-17:35) \n10.{TableFinish.get('8-А').get('tuesday')[9]}(17:45-18:30) ")
           if(message.text=="Середа"):
               await message.answer(f" 1.{TableFinish.get('8-А').get('wednesday')[0]}(8:25-9:10) \n2.{TableFinish.get('8-А').get('wednesday')[1]}(9:25-10:10) \n3.{TableFinish.get('8-А').get('wednesday')[2]}(10:25-11:10) \n4.{TableFinish.get('8-А').get('wednesday')[3]}(11:20-12:05) \n5.{TableFinish.get('8-А').get('wednesday')[4]}(12:30-13:15) \n6.{TableFinish.get('8-А').get('wednesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('8-А').get('wednesday')[6]}(15:00-15:45) \n8.{TableFinish.get('8-А').get('wednesday')[7]}(15:55-16:40) \n9.{TableFinish.get('8-А').get('wednesday')[8]}(16:50-17:35) \n10.{TableFinish.get('8-А').get('wednesday')[9]}(17:45-18:30) ")
           if(message.text=="Четвер"):
               await message.answer(f" 1.{TableFinish.get('8-А').get('thursday')[0]}(8:25-9:10) \n2.{TableFinish.get('8-А').get('thursday')[1]}(9:25-10:10) \n3.{TableFinish.get('8-А').get('thursday')[2]}(10:25-11:10) \n4.{TableFinish.get('8-А').get('thursday')[3]}(11:20-12:05) \n5.{TableFinish.get('8-А').get('thursday')[4]}(12:30-13:15) \n6.{TableFinish.get('8-А').get('thursday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('8-А').get('thursday')[6]}(15:00-15:45) \n8.{TableFinish.get('8-А').get('thursday')[7]}(15:55-16:40) \n9.{TableFinish.get('8-А').get('thursday')[8]}(16:50-17:35) \n10.{TableFinish.get('8-А').get('thursday')[9]}(17:45-18:30) ")
           if(message.text=="П'ятниця"):
               await message.answer(f" 1.{TableFinish.get('8-А').get('friday')[0]}(8:25-9:10) \n2.{TableFinish.get('8-А').get('friday')[1]}(9:25-10:10) \n3.{TableFinish.get('8-А').get('friday')[2]}(10:25-11:10) \n4.{TableFinish.get('8-А').get('friday')[3]}(11:20-12:05) \n5.{TableFinish.get('8-А').get('friday')[4]}(12:30-13:15) \n6.{TableFinish.get('8-А').get('friday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('8-А').get('friday')[6]}(15:00-15:45) \n8.{TableFinish.get('8-А').get('friday')[7]}(15:55-16:40) \n9.{TableFinish.get('8-А').get('friday')[8]}(16:50-17:35) \n10.{TableFinish.get('8-А').get('friday')[9]}(17:45-18:30) ")
       if ( klass== '8б'):
          if(message.text=="Понеділок"):
              await message.answer(f" 1.{TableFinish.get('8-Б').get('monday')[0]}(8:25-9:10) \n2.{TableFinish.get('8-Б').get('monday')[1]}(9:25-10:10) \n3.{TableFinish.get('8-Б').get('monday')[2]}(10:25-11:10) \n4.{TableFinish.get('8-Б').get('monday')[3]}(11:20-12:05) \n5.{TableFinish.get('8-Б').get('monday')[4]}(12:30-13:15) \n6.{TableFinish.get('8-Б').get('monday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('8-Б').get('monday')[6]}(15:00-15:45) \n8.{TableFinish.get('8-Б').get('monday')[7]}(15:55-16:40) \n9.{TableFinish.get('8-Б').get('monday')[8]}(16:50-17:35) \n10.{TableFinish.get('8-Б').get('monday')[9]}(17:45-18:30) ")
          if(message.text=="Вівторок"):
              await message.answer(f" 1.{TableFinish.get('8-Б').get('tuesday')[0]}(8:25-9:10) \n2.{TableFinish.get('8-Б').get('tuesday')[1]}(9:25-10:10) \n3.{TableFinish.get('8-Б').get('tuesday')[2]}(10:25-11:10) \n4.{TableFinish.get('8-Б').get('tuesday')[3]}(11:20-12:05) \n5.{TableFinish.get('8-Б').get('tuesday')[4]}(12:30-13:15) \n6.{TableFinish.get('8-Б').get('tuesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('8-Б').get('tuesday')[6]}(15:00-15:45) \n8.{TableFinish.get('8-Б').get('tuesday')[7]}(15:55-16:40) \n9.{TableFinish.get('8-Б').get('tuesday')[8]}(16:50-17:35) \n10.{TableFinish.get('8-Б').get('tuesday')[9]}(17:45-18:30) ")
          if(message.text=="Середа"):
              await message.answer(f" 1.{TableFinish.get('8-Б').get('wednesday')[0]}(8:25-9:10) \n2.{TableFinish.get('8-Б').get('wednesday')[1]}(9:25-10:10) \n3.{TableFinish.get('8-Б').get('wednesday')[2]}(10:25-11:10) \n4.{TableFinish.get('8-Б').get('wednesday')[3]}(11:20-12:05) \n5.{TableFinish.get('8-Б').get('wednesday')[4]}(12:30-13:15) \n6.{TableFinish.get('8-Б').get('wednesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('8-Б').get('wednesday')[6]}(15:00-15:45) \n8.{TableFinish.get('8-Б').get('wednesday')[7]}(15:55-16:40) \n9.{TableFinish.get('8-Б').get('wednesday')[8]}(16:50-17:35) \n10.{TableFinish.get('8-Б').get('wednesday')[9]}(17:45-18:30) ")
          if(message.text=="Четвер"):
              await message.answer(f" 1.{TableFinish.get('8-Б').get('thursday')[0]}(8:25-9:10) \n2.{TableFinish.get('8-Б').get('thursday')[1]}(9:25-10:10) \n3.{TableFinish.get('8-Б').get('thursday')[2]}(10:25-11:10) \n4.{TableFinish.get('8-Б').get('thursday')[3]}(11:20-12:05) \n5.{TableFinish.get('8-Б').get('thursday')[4]}(12:30-13:15) \n6.{TableFinish.get('8-Б').get('thursday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('8-Б').get('thursday')[6]}(15:00-15:45) \n8.{TableFinish.get('8-Б').get('thursday')[7]}(15:55-16:40) \n9.{TableFinish.get('8-Б').get('thursday')[8]}(16:50-17:35) \n10.{TableFinish.get('8-Б').get('thursday')[9]}(17:45-18:30) ")
          if(message.text=="П'ятниця"):
              await message.answer(f" 1.{TableFinish.get('8-Б').get('friday')[0]}(8:25-9:10) \n2.{TableFinish.get('8-Б').get('friday')[1]}(9:25-10:10) \n3.{TableFinish.get('8-Б').get('friday')[2]}(10:25-11:10) \n4.{TableFinish.get('8-Б').get('friday')[3]}(11:20-12:05) \n5.{TableFinish.get('8-Б').get('friday')[4]}(12:30-13:15) \n6.{TableFinish.get('8-Б').get('friday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('8-Б').get('friday')[6]}(15:00-15:45) \n8.{TableFinish.get('8-Б').get('friday')[7]}(15:55-16:40) \n9.{TableFinish.get('8-Б').get('friday')[8]}(16:50-17:35) \n10.{TableFinish.get('8-Б').get('friday')[9]}(17:45-18:30) ")
 
 
       if ( klass== '9а'):
          if(message.text=="Понеділок"):
              await message.answer(f" 1.{TableFinish.get('9-А').get('monday')[0]}(8:25-9:10) \n2.{TableFinish.get('9-А').get('monday')[1]}(9:25-10:10) \n3.{TableFinish.get('9-А').get('monday')[2]}(10:25-11:10) \n4.{TableFinish.get('9-А').get('monday')[3]}(11:20-12:05) \n5.{TableFinish.get('9-А').get('monday')[4]}(12:30-13:15) \n6.{TableFinish.get('9-А').get('monday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('9-А').get('monday')[6]}(15:00-15:45) \n8.{TableFinish.get('9-А').get('monday')[7]}(15:55-16:40) \n9.{TableFinish.get('9-А').get('monday')[8]}(16:50-17:35) \n10.{TableFinish.get('9-А').get('monday')[9]}(17:45-18:30) ")
          if(message.text=="Вівторок"):
              await message.answer(f" 1.{TableFinish.get('9-А').get('tuesday')[0]}(8:25-9:10) \n2.{TableFinish.get('9-А').get('tuesday')[1]}(9:25-10:10) \n3.{TableFinish.get('9-А').get('tuesday')[2]}(10:25-11:10) \n4.{TableFinish.get('9-А').get('tuesday')[3]}(11:20-12:05) \n5.{TableFinish.get('9-А').get('tuesday')[4]}(12:30-13:15) \n6.{TableFinish.get('9-А').get('tuesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('9-А').get('tuesday')[6]}(15:00-15:45) \n8.{TableFinish.get('9-А').get('tuesday')[7]}(15:55-16:40) \n9.{TableFinish.get('9-А').get('tuesday')[8]}(16:50-17:35) \n10.{TableFinish.get('9-А').get('tuesday')[9]}(17:45-18:30) ")
          if(message.text=="Середа"):
              await message.answer(f" 1.{TableFinish.get('9-А').get('wednesday')[0]}(8:25-9:10) \n2.{TableFinish.get('9-А').get('wednesday')[1]}(9:25-10:10) \n3.{TableFinish.get('9-А').get('wednesday')[2]}(10:25-11:10) \n4.{TableFinish.get('9-А').get('wednesday')[3]}(11:20-12:05) \n5.{TableFinish.get('9-А').get('wednesday')[4]}(12:30-13:15) \n6.{TableFinish.get('9-А').get('wednesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('9-А').get('wednesday')[6]}(15:00-15:45) \n8.{TableFinish.get('9-А').get('wednesday')[7]}(15:55-16:40) \n9.{TableFinish.get('9-А').get('wednesday')[8]}(16:50-17:35) \n10.{TableFinish.get('9-А').get('wednesday')[9]}(17:45-18:30) ")
          if(message.text=="Четвер"):
              await message.answer(f" 1.{TableFinish.get('9-А').get('thursday')[0]}(8:25-9:10) \n2.{TableFinish.get('9-А').get('thursday')[1]}(9:25-10:10) \n3.{TableFinish.get('9-А').get('thursday')[2]}(10:25-11:10) \n4.{TableFinish.get('9-А').get('thursday')[3]}(11:20-12:05) \n5.{TableFinish.get('9-А').get('thursday')[4]}(12:30-13:15) \n6.{TableFinish.get('9-А').get('thursday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('9-А').get('thursday')[6]}(15:00-15:45) \n8.{TableFinish.get('9-А').get('thursday')[7]}(15:55-16:40) \n9.{TableFinish.get('9-А').get('thursday')[8]}(16:50-17:35) \n10.{TableFinish.get('9-А').get('thursday')[9]}(17:45-18:30) ")
          if(message.text=="П'ятниця"):
              await message.answer(f" 1.{TableFinish.get('9-А').get('friday')[0]}(8:25-9:10) \n2.{TableFinish.get('9-А').get('friday')[1]}(9:25-10:10) \n3.{TableFinish.get('9-А').get('friday')[2]}(10:25-11:10) \n4.{TableFinish.get('9-А').get('friday')[3]}(11:20-12:05) \n5.{TableFinish.get('9-А').get('friday')[4]}(12:30-13:15) \n6.{TableFinish.get('9-А').get('friday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('9-А').get('friday')[6]}(15:00-15:45) \n8.{TableFinish.get('9-А').get('friday')[7]}(15:55-16:40) \n9.{TableFinish.get('9-А').get('friday')[8]}(16:50-17:35) \n10.{TableFinish.get('9-А').get('friday')[9]}(17:45-18:30) ")
 
 
       if ( klass== '9б'):
          if(message.text=="Понеділок"):
              await message.answer(f" 1.{TableFinish.get('9-Б').get('monday')[0]}(8:25-9:10) \n2.{TableFinish.get('9-Б').get('monday')[1]}(9:25-10:10) \n3.{TableFinish.get('9-Б').get('monday')[2]}(10:25-11:10) \n4.{TableFinish.get('9-Б').get('monday')[3]}(11:20-12:05) \n5.{TableFinish.get('9-Б').get('monday')[4]}(12:30-13:15) \n6.{TableFinish.get('9-Б').get('monday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('9-Б').get('monday')[6]}(15:00-15:45) \n8.{TableFinish.get('9-Б').get('monday')[7]}(15:55-16:40) \n9.{TableFinish.get('9-Б').get('monday')[8]}(16:50-17:35) \n10.{TableFinish.get('9-Б').get('monday')[9]}(17:45-18:30) ")
          if(message.text=="Вівторок"):
              await message.answer(f" 1.{TableFinish.get('9-Б').get('tuesday')[0]}(8:25-9:10) \n2.{TableFinish.get('9-Б').get('tuesday')[1]}(9:25-10:10) \n3.{TableFinish.get('9-Б').get('tuesday')[2]}(10:25-11:10) \n4.{TableFinish.get('9-Б').get('tuesday')[3]}(11:20-12:05) \n5.{TableFinish.get('9-Б').get('tuesday')[4]}(12:30-13:15) \n6.{TableFinish.get('9-Б').get('tuesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('9-Б').get('tuesday')[6]}(15:00-15:45) \n8.{TableFinish.get('9-Б').get('tuesday')[7]}(15:55-16:40) \n9.{TableFinish.get('9-Б').get('tuesday')[8]}(16:50-17:35) \n10.{TableFinish.get('9-Б').get('tuesday')[9]}(17:45-18:30) ")
          if(message.text=="Середа"):
              await message.answer(f" 1.{TableFinish.get('9-Б').get('wednesday')[0]}(8:25-9:10) \n2.{TableFinish.get('9-Б').get('wednesday')[1]}(9:25-10:10) \n3.{TableFinish.get('9-Б').get('wednesday')[2]}(10:25-11:10) \n4.{TableFinish.get('9-Б').get('wednesday')[3]}(11:20-12:05) \n5.{TableFinish.get('9-Б').get('wednesday')[4]}(12:30-13:15) \n6.{TableFinish.get('9-Б').get('wednesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('9-Б').get('wednesday')[6]}(15:00-15:45) \n8.{TableFinish.get('9-Б').get('wednesday')[7]}(15:55-16:40) \n9.{TableFinish.get('9-Б').get('wednesday')[8]}(16:50-17:35) \n10.{TableFinish.get('9-Б').get('wednesday')[9]}(17:45-18:30) ")
          if(message.text=="Четвер"):
              await message.answer(f" 1.{TableFinish.get('9-Б').get('thursday')[0]}(8:25-9:10) \n2.{TableFinish.get('9-Б').get('thursday')[1]}(9:25-10:10) \n3.{TableFinish.get('9-Б').get('thursday')[2]}(10:25-11:10) \n4.{TableFinish.get('9-Б').get('thursday')[3]}(11:20-12:05) \n5.{TableFinish.get('9-Б').get('thursday')[4]}(12:30-13:15) \n6.{TableFinish.get('9-Б').get('thursday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('9-Б').get('thursday')[6]}(15:00-15:45) \n8.{TableFinish.get('9-Б').get('thursday')[7]}(15:55-16:40) \n9.{TableFinish.get('9-Б').get('thursday')[8]}(16:50-17:35) \n10.{TableFinish.get('9-Б').get('thursday')[9]}(17:45-18:30) ")
          if(message.text=="П'ятниця"):
              await message.answer(f" 1.{TableFinish.get('9-Б').get('friday')[0]}(8:25-9:10) \n2.{TableFinish.get('9-Б').get('friday')[1]}(9:25-10:10) \n3.{TableFinish.get('9-Б').get('friday')[2]}(10:25-11:10) \n4.{TableFinish.get('9-Б').get('friday')[3]}(11:20-12:05) \n5.{TableFinish.get('9-Б').get('friday')[4]}(12:30-13:15) \n6.{TableFinish.get('9-Б').get('friday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('9-Б').get('friday')[6]}(15:00-15:45) \n8.{TableFinish.get('9-Б').get('friday')[7]}(15:55-16:40) \n9.{TableFinish.get('9-Б').get('friday')[8]}(16:50-17:35) \n10.{TableFinish.get('9-Б').get('friday')[9]}(17:45-18:30) ")
 
       if ( klass== '10а'):
          if(message.text=="Понеділок"):
              await message.answer(f" 1.{TableFinish.get('10-А').get('monday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-А').get('monday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-А').get('monday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-А').get('monday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-А').get('monday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-А').get('monday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-А').get('monday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-А').get('monday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-А').get('monday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-А').get('monday')[9]}(17:45-18:30) ")
          if(message.text=="Вівторок"):
              await message.answer(f" 1.{TableFinish.get('10-А').get('tuesday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-А').get('tuesday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-А').get('tuesday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-А').get('tuesday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-А').get('tuesday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-А').get('tuesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-А').get('tuesday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-А').get('tuesday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-А').get('tuesday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-А').get('tuesday')[9]}(17:45-18:30) ")
          if(message.text=="Середа"):
              await message.answer(f" 1.{TableFinish.get('10-А').get('wednesday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-А').get('wednesday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-А').get('wednesday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-А').get('wednesday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-А').get('wednesday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-А').get('wednesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-А').get('wednesday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-А').get('wednesday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-А').get('wednesday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-А').get('wednesday')[9]}(17:45-18:30) ")
          if(message.text=="Четвер"):
              await message.answer(f" 1.{TableFinish.get('10-А').get('thursday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-А').get('thursday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-А').get('thursday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-А').get('thursday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-А').get('thursday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-А').get('thursday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-А').get('thursday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-А').get('thursday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-А').get('thursday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-А').get('thursday')[9]}(17:45-18:30) ")
          if(message.text=="П'ятниця"):
              await message.answer(f" 1.{TableFinish.get('10-А').get('friday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-А').get('friday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-А').get('friday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-А').get('friday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-А').get('friday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-А').get('friday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-А').get('friday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-А').get('friday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-А').get('friday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-А').get('friday')[9]}(17:45-18:30) ")
 
 
       if ( klass== '10б'):
          if(message.text=="Понеділок"):
              await message.answer(f" 1.{TableFinish.get('10-Б').get('monday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-Б').get('monday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-Б').get('monday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-Б').get('monday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-Б').get('monday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-Б').get('monday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-Б').get('monday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-Б').get('monday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-Б').get('monday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-Б').get('monday')[9]}(17:45-18:30) ")
          if(message.text=="Вівторок"):
              await message.answer(f" 1.{TableFinish.get('10-Б').get('tuesday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-Б').get('tuesday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-Б').get('tuesday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-Б').get('tuesday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-Б').get('tuesday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-Б').get('tuesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-Б').get('tuesday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-Б').get('tuesday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-Б').get('tuesday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-Б').get('tuesday')[9]}(17:45-18:30) ")
          if(message.text=="Середа"):
              await message.answer(f" 1.{TableFinish.get('10-Б').get('wednesday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-Б').get('wednesday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-Б').get('wednesday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-Б').get('wednesday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-Б').get('wednesday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-Б').get('wednesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-Б').get('wednesday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-Б').get('wednesday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-Б').get('wednesday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-Б').get('wednesday')[9]}(17:45-18:30) ")
          if(message.text=="Четвер"):
              await message.answer(f" 1.{TableFinish.get('10-Б').get('thursday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-Б').get('thursday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-Б').get('thursday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-Б').get('thursday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-Б').get('thursday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-Б').get('thursday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-Б').get('thursday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-Б').get('thursday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-Б').get('thursday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-Б').get('thursday')[9]}(17:45-18:30) ")
          if(message.text=="П'ятниця"):
              await message.answer(f" 1.{TableFinish.get('10-Б').get('friday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-Б').get('friday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-Б').get('friday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-Б').get('friday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-Б').get('friday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-Б').get('friday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-Б').get('friday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-Б').get('friday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-Б').get('friday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-Б').get('friday')[9]}(17:45-18:30) ")
 
 
       if ( klass== '10в'):
          if(message.text=="Понеділок"):
              await message.answer(f" 1.{TableFinish.get('10-В').get('monday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-В').get('monday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-В').get('monday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-В').get('monday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-В').get('monday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-В').get('monday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-В').get('monday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-В').get('monday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-В').get('monday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-В').get('monday')[9]}(17:45-18:30) ")
          if(message.text=="Вівторок"):
              await message.answer(f" 1.{TableFinish.get('10-В').get('tuesday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-В').get('tuesday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-В').get('tuesday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-В').get('tuesday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-В').get('tuesday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-В').get('tuesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-В').get('tuesday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-В').get('tuesday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-В').get('tuesday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-В').get('tuesday')[9]}(17:45-18:30) ")
          if(message.text=="Середа"):
              await message.answer(f" 1.{TableFinish.get('10-В').get('wednesday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-В').get('wednesday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-В').get('wednesday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-В').get('wednesday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-В').get('wednesday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-В').get('wednesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-В').get('wednesday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-В').get('wednesday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-В').get('wednesday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-В').get('wednesday')[9]}(17:45-18:30) ")
          if(message.text=="Четвер"):
              await message.answer(f" 1.{TableFinish.get('10-В').get('thursday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-В').get('thursday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-В').get('thursday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-В').get('thursday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-В').get('thursday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-В').get('thursday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-В').get('thursday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-В').get('thursday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-В').get('thursday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-В').get('thursday')[9]}(17:45-18:30) ")
          if(message.text=="П'ятниця"):
              await message.answer(f" 1.{TableFinish.get('10-В').get('friday')[0]}(8:25-9:10) \n2.{TableFinish.get('10-В').get('friday')[1]}(9:25-10:10) \n3.{TableFinish.get('10-В').get('friday')[2]}(10:25-11:10) \n4.{TableFinish.get('10-В').get('friday')[3]}(11:20-12:05) \n5.{TableFinish.get('10-В').get('friday')[4]}(12:30-13:15) \n6.{TableFinish.get('10-В').get('friday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('10-В').get('friday')[6]}(15:00-15:45) \n8.{TableFinish.get('10-В').get('friday')[7]}(15:55-16:40) \n9.{TableFinish.get('10-В').get('friday')[8]}(16:50-17:35) \n10.{TableFinish.get('10-В').get('friday')[9]}(17:45-18:30) ")
 
 
       if ( klass== '11а'):
          if(message.text=="Понеділок"):
              await message.answer(f" 1.{TableFinish.get('11-А').get('monday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-А').get('monday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-А').get('monday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-А').get('monday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-А').get('monday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-А').get('monday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-А').get('monday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-А').get('monday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-А').get('monday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-А').get('monday')[9]}(17:45-18:30) ")
          if(message.text=="Вівторок"):
              await message.answer(f" 1.{TableFinish.get('11-А').get('tuesday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-А').get('tuesday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-А').get('tuesday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-А').get('tuesday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-А').get('tuesday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-А').get('tuesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-А').get('tuesday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-А').get('tuesday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-А').get('tuesday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-А').get('tuesday')[9]}(17:45-18:30) ")
          if(message.text=="Середа"):
              await message.answer(f" 1.{TableFinish.get('11-А').get('wednesday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-А').get('wednesday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-А').get('wednesday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-А').get('wednesday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-А').get('wednesday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-А').get('wednesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-А').get('wednesday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-А').get('wednesday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-А').get('wednesday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-А').get('wednesday')[9]}(17:45-18:30) ")
          if(message.text=="Четвер"):
              await message.answer(f" 1.{TableFinish.get('11-А').get('thursday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-А').get('thursday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-А').get('thursday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-А').get('thursday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-А').get('thursday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-А').get('thursday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-А').get('thursday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-А').get('thursday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-А').get('thursday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-А').get('thursday')[9]}(17:45-18:30) ")
          if(message.text=="П'ятниця"):
              await message.answer(f" 1.{TableFinish.get('11-А').get('friday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-А').get('friday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-А').get('friday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-А').get('friday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-А').get('friday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-А').get('friday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-А').get('friday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-А').get('friday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-А').get('friday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-А').get('friday')[9]}(17:45-18:30) ")
 
 
       if ( klass== '11б'):
          if(message.text=="Понеділок"):
              await message.answer(f" 1.{TableFinish.get('11-Б').get('monday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-Б').get('monday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-Б').get('monday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-Б').get('monday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-Б').get('monday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-Б').get('monday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-Б').get('monday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-Б').get('monday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-Б').get('monday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-Б').get('monday')[9]}(17:45-18:30) ")
          if(message.text=="Вівторок"):
              await message.answer(f" 1.{TableFinish.get('11-Б').get('tuesday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-Б').get('tuesday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-Б').get('tuesday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-Б').get('tuesday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-Б').get('tuesday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-Б').get('tuesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-Б').get('tuesday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-Б').get('tuesday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-Б').get('tuesday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-Б').get('tuesday')[9]}(17:45-18:30) ")
          if(message.text=="Середа"):
              await message.answer(f" 1.{TableFinish.get('11-Б').get('wednesday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-Б').get('wednesday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-Б').get('wednesday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-Б').get('wednesday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-Б').get('wednesday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-Б').get('wednesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-Б').get('wednesday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-Б').get('wednesday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-Б').get('wednesday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-Б').get('wednesday')[9]}(17:45-18:30) ")
          if(message.text=="Четвер"):
              await message.answer(f" 1.{TableFinish.get('11-Б').get('thursday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-Б').get('thursday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-Б').get('thursday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-Б').get('thursday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-Б').get('thursday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-Б').get('thursday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-Б').get('thursday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-Б').get('thursday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-Б').get('thursday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-Б').get('thursday')[9]}(17:45-18:30) ")
          if(message.text=="П'ятниця"):
              await message.answer(f" 1.{TableFinish.get('11-Б').get('friday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-Б').get('friday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-Б').get('friday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-Б').get('friday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-Б').get('friday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-Б').get('friday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-Б').get('friday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-Б').get('friday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-Б').get('friday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-Б').get('friday')[9]}(17:45-18:30) ")
 
 
       if ( klass== '11в'):
          if(message.text=="Понеділок"):
              await message.answer(f" 1.{TableFinish.get('11-В').get('monday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-В').get('monday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-В').get('monday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-В').get('monday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-В').get('monday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-В').get('monday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-В').get('monday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-В').get('monday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-В').get('monday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-В').get('monday')[9]}(17:45-18:30) ")
          if(message.text=="Вівторок"):
              await message.answer(f" 1.{TableFinish.get('11-В').get('tuesday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-В').get('tuesday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-В').get('tuesday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-В').get('tuesday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-В').get('tuesday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-В').get('tuesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-В').get('tuesday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-В').get('tuesday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-В').get('tuesday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-В').get('tuesday')[9]}(17:45-18:30) ")
          if(message.text=="Середа"):
              await message.answer(f" 1.{TableFinish.get('11-В').get('wednesday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-В').get('wednesday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-В').get('wednesday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-В').get('wednesday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-В').get('wednesday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-В').get('wednesday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-В').get('wednesday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-В').get('wednesday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-В').get('wednesday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-В').get('wednesday')[9]}(17:45-18:30) ")
          if(message.text=="Четвер"):
              await message.answer(f" 1.{TableFinish.get('11-В').get('thursday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-В').get('thursday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-В').get('thursday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-В').get('thursday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-В').get('thursday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-В').get('thursday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-В').get('thursday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-В').get('thursday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-В').get('thursday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-В').get('thursday')[9]}(17:45-18:30) ")
          if(message.text=="П'ятниця"):
              await message.answer(f" 1.{TableFinish.get('11-В').get('friday')[0]}(8:25-9:10) \n2.{TableFinish.get('11-В').get('friday')[1]}(9:25-10:10) \n3.{TableFinish.get('11-В').get('friday')[2]}(10:25-11:10) \n4.{TableFinish.get('11-В').get('friday')[3]}(11:20-12:05) \n5.{TableFinish.get('11-В').get('friday')[4]}(12:30-13:15) \n6.{TableFinish.get('11-В').get('friday')[5]}(13:25-14:10) \n \n7.{TableFinish.get('11-В').get('friday')[6]}(15:00-15:45) \n8.{TableFinish.get('11-В').get('friday')[7]}(15:55-16:40) \n9.{TableFinish.get('11-В').get('friday')[8]}(16:50-17:35) \n10.{TableFinish.get('11-В').get('friday')[9]}(17:45-18:30) ")


 
def register_handlers_student(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(get_table,commands="gettable", state="*")
    dp.register_message_handler(region_chosen, state=student.waiting_for_region)
    dp.register_message_handler(klass_chosen, state=student.waiting_for_klass)
    dp.register_message_handler(waiting_table,state="*")




logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/gettable", description="Отримати розклад"),
        types.BotCommand(command="/start", description="Старт"),
        
    ]
    await bot.set_my_commands(commands)


async def main():
    #
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers_student(dp)
    await set_commands(bot)
    await dp.start_polling()
 #test

if __name__ == '__main__':
    asyncio.run(main())
   

   



