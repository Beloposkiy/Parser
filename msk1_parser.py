import os
import traceback
from datetime import datetime
from io import BytesIO

import requests
from PIL import Image
from bs4 import BeautifulSoup


class Msk1Parser:
    def __init__(self, save_directory="images"):
        self.save_directory = save_directory
        os.makedirs(self.save_directory, exist_ok=True)
        self.session = requests.Session()

    def parse(self, url, parse_images=False):
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Дата
            date_tag = soup.find('time')
            if not date_tag:
                date = 'Дата не найдена'
            else:
                date_str = date_tag.get('datetime')
                date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z").strftime("%d.%m.%Y")

            # Заголовок
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "Заголовок не найден"

            # Основной текст
            blocks = soup.find_all('div', attrs={"data-article-block-text": True})
            paragraphs = []
            stop_phrase = "Самую оперативную информацию о жизни столицы можно узнать изTelegram-канала MSK1.RU:"

            for block in blocks:
                for p in block.find_all('p'):
                    text = p.get_text(strip=True)
                    if stop_phrase in text:
                        break
                    if text:
                        paragraphs.append(text)

            all_text = "\n".join(paragraphs)

            # Изображения
            image_paths = []
            if parse_images:
                image_tags = soup.find_all('img', class_='image_nZVrb')
                filtered_tags = [tag for tag in image_tags if tag.get('class') == ['image_nZVrb']]

                os.makedirs(self.save_directory, exist_ok=True)

                for idx, img_tag in enumerate(filtered_tags[:-1]):  # исключаем последнее изображение
                    image_url = img_tag.get('src')
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url
                    elif image_url.startswith("/"):
                        image_url = "https://msk1.ru" + image_url

                    img_response = requests.get(image_url)
                    if img_response.status_code == 200:
                        image_name = f"image-msk1-{idx}.jpg"
                        image_path = os.path.join(self.save_directory, image_name)

                        img = Image.open(BytesIO(img_response.content)).convert("RGB")
                        img = img.resize((1000, 667))
                        img.save(image_path, format="JPEG")

                        image_paths.append(image_path)

            return f'{date}\n\"{title}\"\n{all_text}', image_paths

        except Exception as e:
            return f'Error:\n\n{e}\n\n{traceback.format_exc(limit=3)}', None