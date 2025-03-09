from bs4 import BeautifulSoup
class HTMLProductParser:
    def __init__(self, html_code: str):
        self.html = html_code
        self.soup = BeautifulSoup(html_code, "html.parser")

    def get_title(self) -> str:
        title = self.soup.find("h1", class_="lz3_29 tsHeadline550Medium")
        return title.text.strip() if title else "Нет заголовка"

    def get_price(self) -> str:
        price = self.soup.find("span", class_="ly7_29 l7y_29 lz1_29")
        return price.text.strip() if price else "Цена не найдена"

    def get_sizes(self) -> list:
        sizes = self.soup.select(".e310-a6 span.q6b012-a")
        return [size.text.strip() for size in sizes] if sizes else ["Размеры не найдены"]

    def get_description(self) -> str:
        desc = self.soup.find("div", class_="RA-a1")
        return desc.text.strip() if desc else "Описание отсутствует"

    def get_characteristics(self) -> dict:
        characteristics = {}
        char_blocks = self.soup.select(".kr0_29")
        for block in char_blocks:
            key_elem = block.find("dt", class_="qk9_29")
            value_elem = block.find("dd", class_="q9k_29")
            if key_elem and value_elem:
                key = key_elem.text.strip()
                value = " ".join([el.text.strip() for el in value_elem.find_all(string=True)])
                characteristics[key] = value
        return characteristics

    def get_rating(self) -> dict:
        # Основной контейнер с рейтингом
        rating_container = self.soup.select_one('div.z2s_32')

        if not rating_container:
            return {"error": "Рейтинг не найден"}

        # Общий рейтинг
        overall_rating = rating_container.select_one('div.s4z_32 span')
        overall_rating = overall_rating.text.strip() if overall_rating else "Нет данных"

        # Детализация по звездам
        star_ratings = {}
        star_blocks = rating_container.select('div.z4s_32')

        for block in star_blocks:
            stars = block.select_one('.z5s_32').text.strip()
            count = block.select_one('.sz6_32').text.strip()
            star_ratings[stars] = count

        return {
            "overall_rating": overall_rating,
            "star_ratings": star_ratings
        }

    def get_reviews(self):
        reviews = []
        # Ищем все блоки с отзывами; в данном HTML отзывы находятся в контейнерах с классом "py_32"
        review_blocks = self.soup.find_all("div", class_="py_32")

        for block in review_blocks:
            review = {}
            # Извлекаем дату отзыва из элемента с классом "x2p_32"
            date_tag = block.find("div", class_="x2p_32")
            review["date"] = date_tag.get_text(strip=True) if date_tag else "Нет даты"

            # Извлекаем текст отзыва из элемента с классом "p4x_32"
            comment_tag = block.find("span", class_="p4x_32")
            review["comment"] = comment_tag.get_text(strip=True) if comment_tag else "Нет данных"

            # Извлекаем имя пользователя из элемента с классом "p5u_32"
            reviewer_tag = block.find("span", class_="p5u_32")
            review["reviewer"] = reviewer_tag.get_text(strip=True) if reviewer_tag else "Неизвестный"

            # Определяем рейтинг: сначала ищем активные звёзды (цвет "rgb(255, 168, 0)" или "rgba(255, 168, 0")
            active_stars = block.find_all("svg",
                                          style=lambda s: s and ("rgb(255, 168, 0)" in s or "rgba(255, 168, 0" in s))
            rating = len(active_stars)

            # Если активные звёзды не найдены, проверяем наличие альтернативного блока с рейтингом
            if rating == 0:
                alt_rating_div = block.find("div", class_="b7123-a b7123-a1 tsBodyControl300XSmall")
                if alt_rating_div:
                    # Если альтернативный блок найден, можно задать рейтинг 0 (либо добавить дополнительную логику для обработки этого блока)
                    rating = 0

            review["rating"] = rating
            reviews.append(review)

        return reviews

    def get_product_data(self) -> dict:
        return {
            "Название": self.get_title(),
            "Цена": self.get_price(),
            "Размеры": self.get_sizes(),
            "Описание": self.get_description(),
            "Характеристики": self.get_characteristics(),
            "Оценка": self.get_rating(),
            "Отзывы": self.get_reviews(),
        }

    def get_all_links(self) -> list:
        return [a["href"] for a in self.soup.find_all("a", href=True)]

    def get_all_images(self) -> list:
        return [img["src"] for img in self.soup.find_all("img", src=True)]

    def get_text_content(self) -> str:
        return self.soup.get_text(separator=" ", strip=True)

    def find_by_selector(self, selector: str):
        return self.soup.select(selector)
