# pip install python-telegram-bot
# pip install python-telegram-bot==13.7

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,ConversationHandler
from telegram import ReplyKeyboardMarkup
from telegram.ext import *
from telegram import Bot
from utils1 import *
from keys import test_bot as token
import io

print('Starting up bot...')

# # fill assess arbitrary marks conversation handler stats
INIT_F , RESPOND = range(2)
CREDS, AVAILABLE_ASS ,WAITING_FOR_RESPONSE = range(3)
CREDS, FILE = range(2)
ASK_FILE, ASK_QUESTION ,AVAILABLE_ASS, WAITING_FOR_RESPONSE = range(4)


help_text = '''/e_side_marks_note لطباعة كشف علامات جانبي الكتروني 
/side_marks_note لطباعة كشف العلامات الجانبي 
/fill_assess_arbitrary لتسجيل العلامات العشوائية 
/empty_assess لمسح علامات الصف 
/official_marks لطباعة ملف العلامات الرسمية 
/certs لطباعة ملف الشهادات 
/tables لطباعة ملفات الجداول 
/cancel لألغاء العملية'''

# TODO: make sure of every fallback function (cancle function)in the handler conversation 

# Define a function to handle incoming files
def init_empty_fill(update, context):
    update.message.reply_text("هل تريد مسح علامات صف ؟ \n اعطيني اسم المستخدم و كلمة السر من فضلك ؟ \n مثلا 9981058924/123456") 
    return CREDS

def print_available_assessments(update, context):
    user = update.message.from_user
    context.user_data['creds'] = update.message.text.split('/')
    username = context.user_data['creds'][0]
    password = context.user_data['creds'][1]
    print(username, password)
    if get_auth(username, password) == False:
        update.message.reply_text("اسم المستخدم او كلمة السر خطأ") 
    else:
        update.message.reply_text("انتظر لحظة لو سمحت") 
        auth = get_auth(username,password)
        # TODO: handle empty editable_assessments list
        editable_assessments = get_editable_assessments(auth ,username)
        data_to_enter_marks = get_required_data_to_enter_marks(auth ,username)
        string = assessments_commands_text(editable_assessments)
        update.message.reply_text(string)
        context.user_data['assessments'] = editable_assessments
        context.user_data['data_to_enter_marks'] = data_to_enter_marks
        return  AVAILABLE_ASS
    
def fill_assess_empty(update, context):
    user = update.message.from_user
    if update.message.text == '/cancel':
        return cancel(update, context)
    else:
        code = update.message.text.replace('/','')
        update.message.reply_text("انتظر لحظة لو سمحت")         
        editable_assessments = context.user_data['assessments'] 
        data_to_enter_marks = context.user_data['data_to_enter_marks']  
        username , password = context.user_data['creds'][0] , context.user_data['creds'][1]
        if code == 'All_asses':
            assess_data = [i for i in editable_assessments]
            for assessment in assess_data:
                wanted_grades = [i for i in data_to_enter_marks if i.get('assessment_id') == assessment['gradeId']]
                enter_marks_arbitrary_controlled_version(username,password,wanted_grades,assessment['AssesId'])
        else:
            assess_data = [i for i in editable_assessments if i.get('code') == code][0]
            wanted_grades = [i for i in data_to_enter_marks if i.get('assessment_id') == assess_data['gradeId']]
            assess_data = [i for i in editable_assessments if i.get('code') == code][0]
            wanted_grades = [i for i in data_to_enter_marks if i.get('assessment_id') == assess_data['gradeId']]
            enter_marks_arbitrary_controlled_version(username,password,wanted_grades,assess_data['AssesId'])
            update.message.reply_text("هل تريد مسح علامات صف اخر؟ نعم | لا",reply_markup=ReplyKeyboardMarkup([['نعم', 'لا']], one_time_keyboard=True))
            return WAITING_FOR_RESPONSE
        # End of conversation
        update.message.reply_text("تمام انتهينا")
        return ConversationHandler.END

def handle_response(update, context):
    response = update.message.text
    if response == 'نعم':
        return AVAILABLE_ASS
    else:
        update.message.reply_text("تمام انتهينا")
        return ConversationHandler.END
    
def receive_file(update, context ):
    '''
        dispatcher.add_handler(MessageHandler(Filters.document, receive_file))
    '''
    
    # # Check if the message contains a document
    # if not update.message.document:
    #     update.message.reply_text('Please send an Excel file.')
    #     return
    message = update.message
    if message.document:
        file_id = message.document.file_id
        context.user_data['file'] = file_id
        receive_file_massage = '''
        /document_marks  طباعة سجل العلامات و ادخال العلامات معا
        /document طباعة سجل العلامات الرسمي من الملف فقط
        /marks ادخال العلامات من الملف فقط
        '''
        update.message.reply_text(receive_file_massage)  
        return ASK_QUESTION
    else:
        update.message.reply_text('No document file received. Please send a document file.')
        return ConversationHandler.END
    
 
    # # Get the file object and read its content
    # file_obj = context.bot.get_file(update.message.document.file_id)
    # file_bytes = io.BytesIO(file_obj.download_as_bytearray())
    # update.message.reply_text("انتظر لحظة لو سمحت")     
    # fill_official_marks_doc_wrapper_offline(Read_E_Side_Note_Marks(file_content=file_bytes))
    # files = count_files()
    # chat_id = update.message.chat.id
    # send_files(bot, chat_id, files)
    # delete_send_folder()

    # update.message.reply_text('تم بنجاح')
    return ASK_QUESTION

def handle_question(update, context):
    question = update.message.text.replace('/','')
    file_id = context.user_data['file']
    # Get the file object and read its content
    file_obj = context.bot.get_file(file_id)
    file_bytes = io.BytesIO(file_obj.download_as_bytearray())
    
    if question == 'document_marks':
        update.message.reply_text('انشاء سجل علامات و ادخال العلامات من الملف')
    elif question == 'document':
        update.message.reply_text("انتظر لحظة لو سمحت")     
        fill_official_marks_doc_wrapper_offline(Read_E_Side_Note_Marks(file_content=file_bytes))
        files = count_files()
        chat_id = update.message.chat.id
        send_files(bot, chat_id, files)
        delete_send_folder()
    elif question == 'marks':
        update.message.reply_text('ادخال العلامات')
    else:
        update.message.reply_text('ادخال خاطيء')
        return ASK_QUESTION

    return ConversationHandler.END

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

def send_files(bot, chat_id, files):
    for file in files:
        bot.send_document(chat_id=chat_id, document=open(file, 'rb'))

# Lets us use the /help command
def help_command(update, context):
    update.message.reply_text(help_text)

# Log errors
def error(update, context):
    print(f'Update {update} caused error {context.error}')

def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text("تم ")
    return ConversationHandler.END

def get_user_creds(update, context):
    # code
    pass

def check_user_creds(update, context):
    # code
    pass

def init_fill(update, context):
    update.message.reply_text("هل تريد تسجل علامات عشوائي ؟ \n اعطيني اسم المستخدم و كلمة السر من فضلك ؟ \n مثلا 9981058924/123456") 
    return CREDS

def print_available_assessments(update, context):
    user = update.message.from_user
    context.user_data['creds'] = update.message.text.split('/')
    username = context.user_data['creds'][0]
    password = context.user_data['creds'][1]
    print(username, password)
    if get_auth(username, password) == False:
        update.message.reply_text("اسم المستخدم او كلمة السر خطأ") 
    else:
        update.message.reply_text("انتظر لحظة لو سمحت") 
        auth = get_auth(username,password)
        # TODO: handle empty editable_assessments list
        editable_assessments = get_editable_assessments(auth ,username)
        data_to_enter_marks = get_required_data_to_enter_marks(auth ,username)
        string = assessments_commands_text(editable_assessments)
        update.message.reply_text(string)
        context.user_data['assessments'] = editable_assessments
        context.user_data['data_to_enter_marks'] = data_to_enter_marks
        return  AVAILABLE_ASS
    
def fill_assess_arbitrary(update, context):
    user = update.message.from_user
    if update.message.text == '/cancel':
        return cancel(update, context)
    else:
        code = update.message.text.replace('/','')
        update.message.reply_text("انتظر لحظة لو سمحت")         
        editable_assessments = context.user_data['assessments'] 
        data_to_enter_marks = context.user_data['data_to_enter_marks']  
        username , password = context.user_data['creds'][0] , context.user_data['creds'][1]
        if code == 'All_asses':
            assess_data = [i for i in editable_assessments]
            for assessment in assess_data:
                wanted_grades = [i for i in data_to_enter_marks if i.get('assessment_id') == assessment['gradeId']]
                enter_marks_arbitrary_controlled_version(username,password,wanted_grades,assessment['AssesId'],int(assessment['max_mark']*.75),assessment['max_mark'])
        else:
            assess_data = [i for i in editable_assessments if i.get('code') == code][0]
            wanted_grades = [i for i in data_to_enter_marks if i.get('assessment_id') == assess_data['gradeId']]
            assess_data = [i for i in editable_assessments if i.get('code') == code][0]
            wanted_grades = [i for i in data_to_enter_marks if i.get('assessment_id') == assess_data['gradeId']]
            enter_marks_arbitrary_controlled_version(username,password,wanted_grades,assess_data['AssesId'],assess_data['pass_mark'],assess_data['max_mark'])
            update.message.reply_text("هل تريد تعبئة علامات صف اخر؟ نعم | لا",reply_markup=ReplyKeyboardMarkup([['نعم', 'لا']], one_time_keyboard=True))
            return WAITING_FOR_RESPONSE            
        # End of conversation
        update.message.reply_text("تمام انتهينا")
        return ConversationHandler.END

def init_receive(update, context):
    update.message.reply_text("هل تريد تفريغ العلامات على المنظومة و تعبئة سجل العلامات الرسمي من السجل الالكتروني ؟ \n اعطيني اسم المستخدم و كلمة السر من فضلك ؟ \n مثلا 9981058924/123456") 
    return CREDS

def check_creds(update, context):
    if update.message.text == '/cancel':
        return cancel(update, context)
    else:
        user = update.message.from_user
        context.user_data['creds'] = update.message.text.split('/')
        username = context.user_data['creds'][0]
        password = context.user_data['creds'][1]
        # update.message.reply_text("Thanks for sharing! You're a credentials user {} and password {}.".format(context.user_data['creds'][0], context.user_data['creds'][1] ) )
        print(username, password)
        if get_auth(username, password) == False:
            update.message.reply_text("اسم المستخدم او كلمة السر خطأ") 
            return CREDS                                    
        else:
            print('moving to next function')
            update.message.reply_text('0000ارسل ملف العلامات الجانبي الالكتروني؟')            
            return FILE
        
def init_side_marks(update, context):
    update.message.reply_text("هل تريد كشف علامات جانبي ؟ \n اعطيني اسم المستخدم و كلمة السر من فضلك ؟ \n مثلا 9981058924/123456") 
    return CREDS

def send_side_marks_note_doc(update, context):
    user = update.message.from_user
    if update.message.text == '/cancel':
        return cancel(update, context)
    else:
        update.message.reply_text("انتظر لحظة لو سمحت")         
        context.user_data['creds'] = update.message.text.split('/')
        username = context.user_data['creds'][0]
        password = context.user_data['creds'][1]
        print(username, password)
        if get_auth(username, password) == False:
            update.message.reply_text("اسم المستخدم او كلمة السر خطأ") 
        else:
            side_marks_document(username, password)
            files = count_files()
            chat_id = update.message.chat.id
            send_files(bot, chat_id, files)
            delete_send_folder()
            return ConversationHandler.END

def init_certs (update, context): 
    update.message.reply_text("هل تريد طباعة شهادات الطلاب ؟ \n اعطيني اسم المستخدم و كلمة السر من فضلك ؟ \n مثلا 9981058924/123456") 
    return CREDS

def send_students_certs(update, context):
    user = update.message.from_user
    if update.message.text == '/cancel':
        return cancel(update, context)
    else:
        context.user_data['creds'] = update.message.text.split('/')
        username = context.user_data['creds'][0]
        password = context.user_data['creds'][1]
        # update.message.reply_text("Thanks for sharing! You're a credentials user {} and password {}.".format(context.user_data['creds'][0], context.user_data['creds'][1] ) )
        print(username, password)
        if get_auth(username, password) == False:
            update.message.reply_text("اسم المستخدم او كلمة السر خطأ") 
        else:
            update.message.reply_text("هل تريد استخراج نتائج الفصل الثاني؟ نعم|لا")
            if update.message.text == 'نعم':            
                create_certs_wrapper(username, password , term2=True)
            else:
                create_certs_wrapper(username, password)
            files = count_files()
            chat_id = update.message.chat.id
            send_files(bot, chat_id, files)
            delete_send_folder()
            return ConversationHandler.END

def init_tables (update, context): 
    update.message.reply_text("هل تريد طباعة جداول علامات الطلاب ؟ \n اعطيني اسم المستخدم و كلمة السر من فضلك ؟ \n مثلا 9981058924/123456") 
    return CREDS

def send_students_tables(update, context):
    user = update.message.from_user
    if update.message.text == '/cancel':
        return cancel(update, context)
    else:
        context.user_data['creds'] = update.message.text.split('/')
        username = context.user_data['creds'][0]
        password = context.user_data['creds'][1]
        # update.message.reply_text("Thanks for sharing! You're a credentials user {} and password {}.".format(context.user_data['creds'][0], context.user_data['creds'][1] ) )
        print(username, password)
        if get_auth(username, password) == False:
            update.message.reply_text("اسم المستخدم او كلمة السر خطأ") 
        else:
            update.message.reply_text("هل تريد استخراج نتائج الفصل الثاني؟ نعم|لا")
            if update.message.text == 'نعم':
                create_tables_wrapper(username, password, term2=True)
            else:
                create_tables_wrapper(username, password)
            files = count_files()
            chat_id = update.message.chat.id
            send_files(bot, chat_id, files)
            delete_send_folder()
            return ConversationHandler.END

def init_official_marks(update, context):
    update.message.reply_text("هل تريد سجل علامات رسمي ؟ \n قم باعطائي اسم المستخدم و كلمة السر من فضلك ؟ \n مثلا 9981058924/123456") 
    return CREDS

def send_official_marks_doc(update, context):
    if update.message.text == '/cancel':
        return cancel(update, context)
    else:
        user = update.message.from_user
        context.user_data['creds'] = update.message.text.split('/')
        username = context.user_data['creds'][0]
        password = context.user_data['creds'][1]
        # update.message.reply_text("Thanks for sharing! You're a credentials user {} and password {}.".format(context.user_data['creds'][0], context.user_data['creds'][1] ) )
        print(username, password)
        if get_auth(username, password) == False:
            update.message.reply_text("اسم المستخدم او كلمة السر خطأ") 
        else:
            update.message.reply_text("انتظر لحظة لو سمحت") 
            fill_official_marks_doc_wrapper(username, password)
            files = count_files()
            chat_id = update.message.chat.id
            send_files(bot, chat_id, files)
            delete_send_folder()
            return ConversationHandler.END

def init_e_side_marks(update, context):
    update.message.reply_text("هل تريد كشف علامات جانبي الكتروني ؟ \n اعطيني اسم المستخدم و كلمة السر من فضلك ؟ \n مثلا 9981058924/123456") 
    return CREDS

def send_e_side_marks_note_doc(update, context):
    user = update.message.from_user
    if update.message.text == '/cancel':
        return cancel(update, context)
    else:
        update.message.reply_text("انتظر لحظة لو سمحت")         
        context.user_data['creds'] = update.message.text.split('/')
        username = context.user_data['creds'][0]
        password = context.user_data['creds'][1]
        print(username, password)
        if get_auth(username, password) == False:
            update.message.reply_text("اسم المستخدم او كلمة السر خطأ") 
        else:
            create_e_side_marks_doc(username, password)
            files = count_files()
            chat_id = update.message.chat.id
            send_files(bot, chat_id, files)
            delete_send_folder()
            return ConversationHandler.END


# Run the program
if __name__ == '__main__':
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    bot = Bot(token=token)
    
    # Commands
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('start', start))

    # Log all errors
    dp.add_error_handler(error)

    fill_assess_arbitrary_marks_conv = ConversationHandler(
        entry_points=[CommandHandler('fill_assess_arbitrary', init_fill)],
                                        states={
                                            CREDS: [MessageHandler(Filters.text & ~Filters.command, print_available_assessments)],
                                            AVAILABLE_ASS: [MessageHandler(Filters.text , fill_assess_arbitrary)],
                                            WAITING_FOR_RESPONSE: [MessageHandler(Filters.text, handle_response)],                                            
                                        },
                                        fallbacks=[CommandHandler('cancel', cancel)],
                                        allow_reentry=True  # To allow restarting the conversation while it's in progress
                                                        ) 

    fill_assess_arbitrary_empty_marks_conv = ConversationHandler(
        entry_points=[CommandHandler('empty_assess', init_empty_fill)],
                                        states={
                                            CREDS: [MessageHandler(Filters.text & ~Filters.command, print_available_assessments)],
                                            AVAILABLE_ASS: [MessageHandler(Filters.text , fill_assess_empty)],
                                            WAITING_FOR_RESPONSE: [MessageHandler(Filters.text, handle_response)],
                                        },
                                        fallbacks=[CommandHandler('cancel', cancel)],
                                        allow_reentry=True  # To allow restarting the conversation while it's in progress
                                                        ) 

    send_side_marks_note_doc_conv = ConversationHandler(
        entry_points=[CommandHandler('side_marks_note', init_side_marks)],
                                        states={
                                            CREDS : [MessageHandler(Filters.text , send_side_marks_note_doc)]
                                        },
                                        fallbacks=[CommandHandler('cancel', cancel)]
                                                        )

    send_students_certs_conv = ConversationHandler(
                                        entry_points=[CommandHandler('certs', init_certs)],
                                        states={
                                            CREDS : [MessageHandler(Filters.text , send_students_certs)]
                                        },
                                        fallbacks=[CommandHandler('cancel', cancel)]
                                                        )

    send_students_tables_conv = ConversationHandler(
                                        entry_points=[CommandHandler('tables', init_tables)],
                                        states={
                                            CREDS : [MessageHandler(Filters.text , send_students_tables)]
                                        },
                                        fallbacks=[CommandHandler('cancel', cancel)]
                                                        )
    
    send_official_marks_doc_conv = ConversationHandler(
                                        entry_points=[CommandHandler('official_marks', init_official_marks)],
                                        states={
                                            CREDS : [MessageHandler(Filters.text , send_official_marks_doc)]
                                        },
                                        fallbacks=[CommandHandler('cancel', cancel)]
                                                        )

    send_official_marks_doc_conv_offline = ConversationHandler(
                                        entry_points=[CommandHandler('official_marks_offline', init_receive)],
                                        states={
                                            CREDS : [MessageHandler(Filters.text , check_creds )],
                                            FILE : [MessageHandler(Filters.text ,receive_file)]
                                        },
                                        fallbacks=[CommandHandler('cancel', cancel)]
                                                        )
    # send_students_absent_doc_conv = ConversationHandler(
    
    send_side_marks_note_doc_conv = ConversationHandler(
                                    entry_points=[CommandHandler('e_side_marks_note', init_e_side_marks)],
                                        states={
                                            CREDS : [MessageHandler(Filters.text , send_e_side_marks_note_doc)]
                                        },
                                        fallbacks=[CommandHandler('cancel', cancel)]
                                                        )
    receive_file_handler_conv = ConversationHandler(
                                    entry_points=[MessageHandler(Filters.document, receive_file)],
                                        states={
                                            ASK_QUESTION: [MessageHandler(Filters.text, handle_question)]
                                        },
                                        fallbacks=[]
                                                        )
        
        

    # Add the conversation handler to the dispatcher
    dp.add_handler(send_side_marks_note_doc_conv)
    dp.add_handler(send_side_marks_note_doc_conv)
    dp.add_handler(send_official_marks_doc_conv)
    dp.add_handler(fill_assess_arbitrary_marks_conv)
    dp.add_handler(fill_assess_arbitrary_empty_marks_conv)
    dp.add_handler(send_official_marks_doc_conv_offline)
    # dp.add_handler(MessageHandler(Filters.document, receive_file))
    dp.add_handler(receive_file_handler_conv)
    dp.add_handler(send_students_certs_conv)

    # Run the bot
    updater.start_polling(1.0)
    updater.idle()
    
    
    
    