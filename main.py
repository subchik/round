import os
import cv2
import numpy as np
from aiogram import Bot, types 
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from moviepy.editor import VideoFileClip
import tempfile
import yandex_music

MAX_VIDEO_SIZE = 14 * 1024 * 1024
MAX_GIF_SIZE = 10 * 1024 * 1024
TOKEN = "5946399214:AAE3GvKTkw4PcOYK3dSgIrGkeiW5GwzWEeM"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
parse_mode=types.ParseMode.HTML


#============ТЕКСТОВЫЕ КОМАНДЫ============
@dp.message_handler(commands=['start'])
async def start_cmd_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_video = types.KeyboardButton("Видео")
    button_gif = types.KeyboardButton("GIF")
    button_sing = types.KeyboardButton("Исполнитель")
    keyboard.add(button_video)
    keyboard.add(button_gif)
    keyboard.add(button_sing)
    await message.answer(
"""Нажми на нужную кнопку для обработки.

<b>Видео</b> - обработка видео в виде кружка
<b>GIF</b> - обработка гифки в виде кружка
<b>Исполнитель</b> - поиск исполнителя песни по её названию

Если у вас возникли затруднения - воспользуйтесь командой <b>/help</b>""", parse_mode="HTML", reply_markup=keyboard)

@dp.message_handler(commands=['help'])
async def start_cmd_handler(message: types.Message):
    await message.answer(f"""<b>@Video_and_round_bot</b>  — это бесплатный telegram бот благодаря которому можно легко преобразовать видео в видео сообщение.
━━━━━━━━━━━━‌‌━━━━━━━━━━━━‌‌━━
<u>❗️ В чём преимущество кружочка: меньший вес ролика, более удобный формат просмотра, загружается даже при слабом интернет соединении.</u>
    
<b>📣 В разработке:</b>

> Функция скачивания ролика с разный платформ. 
> Встроеный редактор для видео.
━━━━━━━━━━━━‌‌━━━━━━━━━━━━‌‌━━
<b>Команды бота:</b>

<b>/start</b> - Начало работы с ботом.
<b>/help</b> - Остовная информация о боте и его команды.
<b>/info</b> - Общая информация о боте и разработчике.
━━━━━━━━━━━━‌‌━━━━━━━━━━━━‌‌━━
<a href="https://t.me/Round_memes">Канал бота</a>
""", parse_mode="HTML")

@dp.message_handler(commands=['info'])
async def start_cmd_handler(message: types.Message):
    await message.answer(f"""<b>Основная информация:</b>
<b>Разработчик:</b> <b>semechka#5942</b>

<b>По вопросам и багам:</b> <a href="kokosn002@gmail.com">почта</a>

<b>О боте:</b> бот был разработан за месяц, на данный момент может функционировать как отдельно так и в груповом канале""", parse_mode="HTML")

convert_counts = {
    'video': 0,
    'gif': 0
}

# функция для обработки команды users_list
@dp.message_handler(commands=['user_list'])
async def users_list(message: types.Message):
    # получаем количество преобразований видео и гифок
    video_count = convert_counts['video']
    gif_count = convert_counts['gif']
    # отправляем сообщение
    await message.answer(f"<b>Количество пользователей, которые преобразовали видео в кружок:</b> {video_count}\n \n<b>Количество пользователей, которые преобразовали гифку в кружок:</b> {gif_count}", parse_mode="HTML")

#============ОБРАБОТКА ВИДЕО============
@dp.message_handler(lambda message: message.text == "Видео")
async def send_video_handler(message: types.Message):
    keyboard = types.ReplyKeyboardRemove()
    await message.answer("Пришли мне видео, которое нужно обработать в кружок.\n \n<b>❗️ Обратите внимание: что длительность не должна превышать 60 сек. ❗️</b>", reply_markup=keyboard, parse_mode="HTML")

@dp.message_handler(content_types=types.ContentType.VIDEO)
async def video_handler(message: types.Message):
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp:
        file_info = await bot.get_file(message.video.file_id)
        file_size = file_info.file_size

        if file_size > MAX_VIDEO_SIZE:
            await bot.send_message(chat_id=message.chat.id, text="⚠️ Видео слишком много весит. Пожалуйста уменьшите вес до 14 мб.")
            return
        
        if message.video.duration > 60:
            await bot.send_message(chat_id=message.chat.id, text="⚠️ Длительность видео должна быть менее 1 минуты.")
            return
        await bot.send_message(chat_id=message.chat.id, text="📹 Видео обрабатывается...")

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_video_file:
            file_path = tmp_video_file.name
            await message.video.download(destination=file_path)

            video = cv2.VideoCapture(file_path)
            fps = int(video.get(cv2.CAP_PROP_FPS))
            frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            if frame_width < 400:
                square_size = frame_width
            else:
                square_size = 400

            x = int((frame_width - square_size) / 2)
            y = int((frame_height - square_size) / 2)

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            with tempfile.NamedTemporaryFile(suffix="_out.mp4", delete=False) as tmp_out_file:
                out_file_path = tmp_out_file.name
                out = cv2.VideoWriter(out_file_path, fourcc, fps, (square_size, square_size), isColor=True)

                while video.isOpened():
                    ret, frame = video.read()
                    if not ret:
                        break
                    square_frame = cv2.resize(frame, (square_size, square_size))
                    out.write(square_frame)

            video.release()
            del video
            out.release()
            cv2.destroyAllWindows()

            video_clip = VideoFileClip(out_file_path)
            audio_clip = VideoFileClip(file_path).audio
            video_clip = video_clip.set_audio(audio_clip)
            with tempfile.NamedTemporaryFile(suffix="_out_audio.mp4", delete=False) as tmp_final_file:
                final_file_path = tmp_final_file.name
                video_clip.write_videofile(final_file_path, fps=fps)

            video_clip.close()
            audio_clip.close()

            with open(final_file_path, "rb") as video_file:
                await bot.send_video_note(chat_id=message.chat.id, video_note=video_file)
                await bot.send_message(chat_id=message.chat.id, text="✅ Готово")
            
            convert_counts['video'] += 1
    os.remove(temp.name)

#============ОБРАБОТКА GIF============
@dp.message_handler(lambda message: message.text == "GIF")
async def send_video_handler(message: types.Message):
    keyboard = types.ReplyKeyboardRemove()
    await message.answer("Пришли мне GIF, которое нужно обработать.", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentType.ANIMATION)
async def gif_handler(message: types.Message):
    file_info = await bot.get_file(message.document.file_id)
    file_size = file_info.file_size

    if file_size > MAX_GIF_SIZE:
        await bot.send_message(chat_id=message.chat.id, text="⚠️ GIF слишком много весит. Пожалуйста уменьшите вес до 10 мб.")
        return

    await bot.send_message(chat_id=message.chat.id, text="🎞️ GIF обрабатывается...")

    file_path = f"gifs/{message.document.file_id}.mp4"
    await message.document.download(destination=file_path)

    video = cv2.VideoCapture(file_path)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if frame_width < 400:
        square_size = frame_width
    else:
        square_size = 400

    x = int((frame_width - square_size) / 2)
    y = int((frame_height - square_size) / 2)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(f"gifs/{message.document.file_id}_out.mp4", fourcc, fps, (square_size, square_size), isColor=True)

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        square_frame = cv2.resize(frame, (square_size, square_size))
        out.write(square_frame)

    # закрываем видео и освобождаем ресурсы
    video.release()
    del video
    out.release()
    cv2.destroyAllWindows()

    # объединяем видео и аудио
    video_clip = VideoFileClip(f"gifs/{message.document.file_id}_out.mp4")
    audio_clip = None
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(f"gifs/{message.document.file_id}_out_audio.mp4", fps=fps)

    # отправляем измененный видео-файл пользователю
    out_file_path = f"gifs/{message.document.file_id}_out_audio.mp4"
    with open(out_file_path, "rb") as video_file:
        await bot.send_video_note(chat_id=message.chat.id, video_note=video_file)
        await bot.send_message(chat_id=message.chat.id, text="✅ Готово")
    
    convert_counts['gif'] += 1
    # close video clips
    video_clip.close()

    # delete video files
    os.remove(f"gifs/{message.document.file_id}_out.mp4")
    os.remove(f"gifs/{message.document.file_id}_out_audio.mp4")
    os.remove(file_path)


#============ОБРАБОТКА МУЗЫКИ ПО НАЗВАНИЮ============
@dp.message_handler(lambda message: message.text == "Исполнитель")
async def send_video_handler(message: types.Message):
    keyboard = types.ReplyKeyboardRemove()
    await message.answer("Напишите название трека.", reply_markup=keyboard)

def search_track(query):
    result = yandex_music.Client().search(query, type_='track')
    if result and result.tracks:
        track = result.tracks.results[0]
        title = track.title
        artists = ', '.join([a.name for a in track.artists])
        return title, artists
    else:
        return None

# обработчик текстового сообщения
@dp.message_handler(content_types=['text'])
async def text_handler(message: types.Message):
    query = message.text.strip()
    if not query:
        return
    if query.startswith('/'):
        return
    track = search_track(query)
    if track:
        title, artists = track
        await message.answer(f'🔊<b>Трек:</b> {title}\n<b>Исполнитель:</b> {artists}', parse_mode="HTML")
    else:
        await message.answer('❌Трек не найден')

#=======Триггер на остальные форматы=======
@dp.message_handler(content_types=types.ContentTypes.AUDIO | types.ContentTypes.DOCUMENT | types.ContentTypes.PHOTO | types.ContentTypes.STICKER |types.ContentTypes.VOICE |types.ContentTypes.VIDEO_NOTE) #content_types=types.ContentTypes.AUDIO
async def handle_unsupported_content(message: types.Message):
    await message.answer("Ошибка: сообщение содержит неподдерживаемый тип контента")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)