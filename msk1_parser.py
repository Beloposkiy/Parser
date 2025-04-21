import os
import requests
from datetime import datetime
from io import BytesIO

from bs4 import BeautifulSoup
from PIL import Image

class Msk1Parser:
    def __init__(self, save_directory="images"):
        self.save_directory = save_directory
        os.makedirs(self.save_directory, exist_ok=True)

    def get_publication_date(self, soup):
        date_tag = soup.find('time')
        if not date_tag:
            return 'Дата не найдена'
        date_str = date_tag.get('datetime')
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return date.strftime("%d.%m.%Y")

    def get_title(self, soup):
        title_tag = soup.find('h1')
        return title_tag.get_text(strip=True) if title_tag else "Заголовок не найден"

    def get_main_text(self, soup):
        blocks = soup.find_all('div', attrs={"data-article-block-text": True})
        if not blocks:
            return "Текст не найден"

        paragraphs = []
        stop_phrase = "Самую оперативную информацию о жизни столицы можно узнать изTelegram-канала MSK1.RU:"

        for block in blocks:
            for p in block.find_all('p'):
                text = p.get_text(strip=True)
                if stop_phrase in text:
                    # Обрезаем всё после появления фразы (включая саму фразу)
                    return "\n".join(paragraphs)
                if text:
                    paragraphs.append(text)

        return "\n".join(paragraphs)

    def get_all_images(self, soup):
        image_paths = []

        # Только теги <img>, у которых class строго ['image_nZVrb']
        image_tags = soup.find_all('img', class_='image_nZVrb')
        filtered_tags = [tag for tag in image_tags if tag.get('class') == ['image_nZVrb']]

        for idx, img_tag in enumerate(filtered_tags[:-1]):
            img_url = img_tag.get('src')
            if not img_url:
                continue
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            elif img_url.startswith("/"):
                img_url = "https://msk1.ru" + img_url

            try:
                response = requests.get(img_url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    img = img.resize((1000, 667))
                    image_name = f"image-msk1-{idx}.jpg"
                    image_path = os.path.join(self.save_directory, image_name)
                    img.save(image_path, format="JPEG")
                    image_paths.append(image_path)
            except Exception as e:
                print(f"Ошибка при загрузке изображения: {e}")
                continue

        return image_paths

    def parse_article(self, url, parse_images=True):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return f"Ошибка запроса: {response.status_code}", None

            soup = BeautifulSoup(response.content, 'html.parser')

            date = self.get_publication_date(soup)
            title = self.get_title(soup)
            text = self.get_main_text(soup)
            images = self.get_all_images(soup) if parse_images else []

            result_text = f"{date}\n{title}\n\n{text}\n"
            return result_text, images

        except Exception as e:
            import traceback
            return f'Ошибка:\n\n{e}\n\n{traceback.format_exc(limit=3)}', None

