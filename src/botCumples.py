from telegram.ext import Updater, CommandHandler, MessageHandler
from auth import token, userBd, passBd, ip, bd

import mysql.connector
from mysql.connector import Error

import logging

# Formato que tiene le mensaje
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger('botCumple')

# Saludo del bot
def start(update, context):
    logger.info('He recibido un comando start')
    update.message.reply_text('Bienvenido al Recordatorio de Cumpleaños')
    user_id = update.effective_user['id']
    first_name = update.effective_user['first_name']

    try:
        conexion = mysql.connector.connect(user= userBd, password= passBd,
                                host= ip,
                                database= bd)
        
        if conexion.is_connected():
            print('Conexion realizada.')
            cursor = conexion.cursor() # Permite hacer consultas (CRUD)
            crearTabla = """CREATE TABLE {0}(
                ID int PRIMARY KEY auto_increment not null,
                Nombre varchar(60) not null,
                FechaNac date not null
                ) Engine = InnoDB;""".format({first_name+str(user_id)})
            cursor.execute(crearTabla)
    except Error as ex:
        print('Error en la conexion:', ex)
    finally:
        if conexion.is_connected():
            conexion.close() # Se cerro al conexion.
            print('La conexion ha finalizado.')

def addBirthday(update, context):
    logger.info('Van hacer una insercción de tabla')
    user_id = update.effective_user['id']
    first_name = update.effective_user['first_name']

    nombre = context.args[0]
    fechaNac = context.args[1]

    try:
        conexion = mysql.connector.connect(user= userBd, password= passBd,
                                host= ip,
                                database= bd)
        
        if conexion.is_connected():
            print('Conexion realizada.')
            cursor = conexion.cursor()
            insertar = "INSERT INTO {0} (Nombre, FechaNac) VALUES ('{1}','{2}')".format(first_name+str(user_id), nombre, fechaNac)
            cursor.execute(insertar)
            conexion.commit() # Confirma la accion que estamos ejecutando.
            print('Registro realizado con exito.')
            context.bot.sendMessage(
                chat_id = user_id,
                parse_mode = "HTML",
                text = f"Cumpleaños añadido con exito."
            )

    except Error as ex:
        print('Error en la conexion:', ex)
    finally:
        if conexion.is_connected():
            conexion.close() # Se cerro al conexion.
            print('La conexion ha finalizado.')



def month(update, context):
    logger.info('Buscando los cumpleaños de este mes')
    user_id = update.effective_user['id']
    first_name = update.effective_user['first_name']

    mes = context.args[0]

    try:
        conexion = mysql.connector.connect(user= userBd, password= passBd,
                                host= ip,
                                database= bd)
        
        if conexion.is_connected():
            print('Conexion realizada.')
            cursor = conexion.cursor() # Permite hacer consultas (CRUD)
            consultaMes = "SELECT Nombre, FechaNac FROM {0} WHERE MONTH(FechaNac)={1}".format(first_name+str(user_id), mes)
            cursor.execute(consultaMes)
            resultados = cursor.fetchall()
            for fecha in resultados:
                # print(fecha[1], fecha[2])
                context.bot.sendMessage(
                    chat_id = user_id,
                    parse_mode = "HTML",
                    text =f"{fecha[0], fecha[1]}"
                )
    except Error as ex:
        print('Error en la conexion:', ex)
    finally:
        if conexion.is_connected():
            conexion.close() # Se cerro al conexion.
            print('La conexion ha finalizado.')

def help(update, context):
    logger.info('El usuario ha pedido ayuda')
    update.message.reply_text("""
    /start - Saludo del Bot
    /añadirCumple arg1 arg - Introduce un cumpleaños. Arg1 es el nombre/mote de la persona (obligatorio) y Arg2(obligatorio) la fecha de nacimiento/fecha de cumpleaños(YYYY-MM-DD).
    /esteMes arg1 - Busca los cumpleaños del mes introducido en el arg1 con el formato MM.
    """)
    

def main():
    # updater = Updater("token", use_context=True)
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('addcumple', addBirthday))
    dispatcher.add_handler(CommandHandler('mes', month))
    dispatcher.add_handler(CommandHandler('help', help))

    # Start the Bot to receive the messages
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()