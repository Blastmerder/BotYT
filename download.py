from pytubefix import YouTube
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from pydub import AudioSegment
import requests
import os
import re
from PIL import Image


# установка аудио

def download_audio(yt, output_path='.'):
    """Скачивание и конвертация аудио с использованием pydub"""
    audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
    temp_file = audio_stream.download(output_path=output_path)
    
    # Конвертация в MP3 с настройками качества
    mp3_file = os.path.splitext(temp_file)[0] + '.mp3'
    AudioSegment.from_file(temp_file).export(
        mp3_file,
        format='mp3',
        bitrate='192k',
        tags={
            'title': yt.title,
            'artist': yt.author
        }
    )
    
    os.remove(temp_file)
    return mp3_file

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

def get_thumbnail(yt, filename='thumbnail.jpg'):
    """Скачивание и обработка превью"""
    thumbnail_url = yt.thumbnail_url.replace('default.jpg', 'maxresdefault.jpg')
    response = requests.get(thumbnail_url)
    
    if response.status_code != 200:
        thumbnail_url = yt.thumbnail_url
        response = requests.get(thumbnail_url)
    
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
    video_url = input("Введите URL YouTube видео: ")
    
    try:
        yt = YouTube(video_url)
        print(f"\nОбработка: {yt.title}")
        
        mp3_file = download_audio(yt)
        thumbnail = get_thumbnail(yt)
        
        set_metadata(mp3_file, yt.title, yt.author, thumbnail)
        os.remove(thumbnail)
        
        print(f"\nУспешно сохранено: {os.path.basename(mp3_file)}")
        print(f"Исполнитель: {clean_metadata_text(yt.author)}")
        print(f"Название: {clean_metadata_text(yt.title)}\n")

    except Exception as e:
        print(f"\nОшибка: {str(e)}")
