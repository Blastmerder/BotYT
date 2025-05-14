import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from pydub import AudioSegment
import requests
import os
import re
from PIL import Image


# установка аудио

def download_audio(url, output_path='./', name=''):
    # Настройки для аудио                                   
    options = {                                                     'format': 'bestaudio/best',
        'postprocessors': [{
        'key': 'FFmpegExtractAudio',                                'preferredcodec': 'mp3',                                    'preferredquality': '256',                              }],                                                         'outtmpl': f'{output_path}{name}',
    }                                                                                                                   
    # Скачивание

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])


def get_data(url):
    options = {                                                     'quiet': True,                                              'skip_download': True                                   }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)                                                                            # Основные метаданные

        title = info.get('title', 'Название не найдено')

        uploader = info.get('uploader', 'Автор не найден')

        artist = info.get('artist') or info.get('creator') or info.get('uploader', 'Автор не найден')

        duration = info.get('duration', 0)

        # URL превью (максимального доступного разрешения)
        thumbnail_url = info.get('thumbnail', 'Превью отсутствует')                                                                                                                         # Все доступные превью (если нужен выбор)           
        thumbnails = info.get('thumbnails', [])             
        if thumbnails:                                      
            # Выбрать превью с максимальным разрешением
            best_thumbnail = max(thumbnails, key=lambda x: x.get('width', 0))
            thumbnail_url = best_thumbnail['url']

    # Вывод информации
    print(f"Название: {title}")
    print(f"Автор: {artist}")
    print(f"Длительность: {duration} сек")

    return {
            "author": artist,
            "title": title,
            "thumbnail_url": thumbnail_url
            }

def process_thumbnail(image_path, output_size=800, threshold=15):
    """Точное удаление чёрных полос и создание квадратного изображения"""
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()
    width, height = img.size

    # Поиск верхней границы контента
    top = 0
    for y in range(height):
        row_sum = sum(pixels[x, y][0] + pixels[x, y][1] + pixels[x, y][2] for x in range(width))
        if row_sum / (width * 3) > threshold:
            top = y
            break

    # Поиск нижней границы контента
    bottom = height - 1
    for y in reversed(range(height)):
        row_sum = sum(pixels[x, y][0] + pixels[x, y][1] + pixels[x, y][2] for x in range(width))
        if row_sum / (width * 3) > threshold:
            bottom = y
            break

    # Обрезка чёрных полос
    if top > 0 or bottom < height - 1:
        img = img.crop((0, top, width, bottom + 1))

    # Центральная квадратная обрезка
    width, height = img.size
    size = min(width, height)
    left = (width - size) // 2
    top_crop = (height - size) // 2
    img = img.crop((left, top_crop, left + size, top_crop + size))

    # Финальный ресайз
    img = img.resize((output_size, output_size), Image.Resampling.LANCZOS)
    img.save(image_path, "JPEG", quality=95, optimize=True, progressive=True)
    return image_path

def get_thumbnail(url, filename='thumbnail.jpg'):
    response = requests.get(url)
    if response.status_code != 200:
        thumbnail_url = yt.thumbnail_url
        response = requests.get(url)


def get_thumbnail(url, filename='thumbnail.jpg'):
    response = requests.get(url) 
    if response.status_code != 200:
        thumbnail_url = yt.thumbnail_url
        response = requests.get(url)
    

    with open(filename, 'wb') as f:
        f.write(response.content)

    return process_thumbnail(filename)

def clean_metadata_text(text):
    """Очистка текста метаданных"""
    text = re.sub(r'\s*[\(\[].*?[\)\]]', '', text)  # Удаление скобок и их содержимого
    text = re.sub(r'(official\s*(music\s*)?video|lyrics?|hd|4k|1080p|720p|\||- topic)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip(' -_')
    return text

def set_metadata(mp3_file, title, artist, thumbnail_path):
    """Установка очищенных метаданных"""
    audio = MP3(mp3_file, ID3=ID3)

    # Очистка существующих тегов
    try:
        audio.tags.delete()
    except:
        pass

    # Нормализация данных
    clean_title = clean_metadata_text(title)
    clean_artist = clean_metadata_text(artist.split('-')[0].split('|')[0].strip())

    # Удаление платформенных суффиксов
    for suffix in ['VEVO', 'Official']:
        clean_artist = clean_artist.replace(suffix, '').strip()

    # Установка основных тегов
    audio.tags.add(TIT2(encoding=3, text=clean_title))
    audio.tags.add(TPE1(encoding=3, text=clean_artist))
    audio.tags.add(TALB(encoding=3, text=clean_title))

    # Удаление технических тегов
    for tag in ['TDRC', 'TCON', 'COMM', 'TXXX']:
        if tag in audio.tags:
            del audio.tags[tag]

    # Добавление обложки
    with open(thumbnail_path, 'rb') as f:
        audio.tags.add(APIC(
            encoding=3,
            mime='image/jpeg',
            type=3,
            data=f.read()
        ))

    audio.save()

if __name__ == "__main__":
    url = input("Введите URL YouTube видео: ")

    try:
        data = get_data(url)
        mp3_file = download_audio(url)
        thumbnail = get_thumbnail(data["thumbnail_url"])

        set_metadata(mp3_file, data["title"], data["author"], thumbnail)
        os.remove(thumbnail)

        
        set_metadata(mp3_file, data["title"], data["author"], thumbnail)
        os.remove(thumbnail)
        

    except Exception as e:
        print(f"\nОшибка: {str(e)}")
