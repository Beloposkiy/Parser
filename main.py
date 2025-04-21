from msk1_parser import Msk1Parser

parser = Msk1Parser()

# Ссылка на статью
url = "https://msk1.ru/text/gorod/2025/04/17/75346973/"
#url = "https://msk1.ru/text/economics/2025/04/21/75366209/"

# Запускаем парсинг
text, images = parser.parse_article(url)

# Выводим результаты
print("Текст статьи:\n")
print(text)

print("\nСписок сохранённых изображений:")
for img in images:
    print(img)