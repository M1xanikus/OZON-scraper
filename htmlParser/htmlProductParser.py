from bs4 import BeautifulSoup

class HTMLProductParser:
    def __init__(self, html_code: str, product_name: str):
        self.html = html_code
        self.product_name = product_name
        self.soup = BeautifulSoup(html_code, "html.parser")

    def get_title(self) -> str:
        title = self.soup.find("h1", class_="lz6_28 tsHeadline550Medium")
        return title.text.strip() if title else "Нет заголовка"

    def get_price(self) -> str:
        price = self.soup.find("span", class_="lz_28 zl_28 lz4_28")
        return price.text.strip() if price else "Цена не найдена"

    def get_description(self) -> str:
        desc = self.soup.find("div", class_="RA-a1")
        return desc.text.strip() if desc else "Описание отсутствует"

    def get_characteristics(self) -> dict:
        characteristics = {}
        char_blocks = self.soup.select(".r4k_28")
        for block in char_blocks:
            # Ищем все пары ключ-значение внутри блока
            key_value_pairs = block.find_all("dl",class_="rk8_28")

            for pair in key_value_pairs:
                key_elem = pair.find("dt", class_="rk7_28")

                value_elem = pair.find("dd", class_="r7k_28")

                if key_elem and value_elem:
                    key = key_elem.text.strip()
                    value = " ".join([el.text.strip() for el in value_elem.find_all(string=True)])
                    characteristics[key] = value
        return characteristics

    def get_rating(self) -> dict:
        rating_container = self.soup.select_one('div.sx7_31')
        if not rating_container:
            return {"error": "Рейтинг не найден"}

        overall_rating = rating_container.find("span")
        overall_rating = overall_rating.text.strip() if overall_rating else "Нет данных"

        return {
            "overall_rating": overall_rating,
        }

    def get_reviews(self) -> list:
        reviews = []

        # Находим все контейнеры с отзывами
        reviews_containers = self.soup.find_all("div", class_="rt1_31")
        for container in reviews_containers:
            # Убираем рекомендации
            for recommendations in container.find_all("div", class_="jp7_25"):
                recommendations.decompose()

            # Проверяем, есть ли в контейнере отзывы после удаления рекомендаций
            review_blocks = container.find_all("div", class_="r2t_31")
            if not review_blocks:
                continue  # Пропускаем пустые контейнеры

            for block in review_blocks:
                review = {}

                # Имя пользователя
                reviewer_tag = block.find("span", class_="p8u_31")
                review["reviewer"] = reviewer_tag.get_text(strip=True) if reviewer_tag else "Неизвестный"

                # Дата отзыва
                date_tag = block.find("div", class_="x5p_31")
                review["date"] = date_tag.get_text(strip=True) if date_tag else "Нет даты"

                # Текст отзыва
                comment_tag = block.find("span", class_="p7x_31")
                review["comment"] = comment_tag.get_text(strip=True) if comment_tag else "Нет данных"

                # Рейтинг (количество звезд)
                review["rating"] = self.extract_rating(block)

                # Дополнительные данные (например, цвет товара)
                product_color_tag = block.find("a", class_="y3p_31")
                review["product_color"] = product_color_tag.get_text(strip=True) if product_color_tag else "Нет данных"

                # Изображения или видео (если есть)
                media_links = [media.get("src", "") for media in block.find_all("img", class_="pw4_31 b933-a")]

                review["media"] = media_links

                reviews.append(review)

        return reviews

    def extract_rating(self, block) -> int:
        rating_block = block.find("div", class_="a5d25-a a5d25-a0")
        if not rating_block:
            return 0

        active_stars = rating_block.find_all("svg", style=lambda s: s and "rgb(255, 165, 0)" in s)
        return len(active_stars)

    def get_product_data(self) -> dict:
        return {
            "Название": self.get_title(),
            "Цена": self.get_price().replace('\u2009', ' '),
            "Описание": self.get_description(),
            "Характеристики": self.get_characteristics(),
            "Оценка": self.get_rating(),
            "Отзывы": self.get_reviews(),
            "URL товара": "https://ozon.by/product/" + self.product_name + "/"
        }

    def get_all_links(self) -> list:
        return [a["href"] for a in self.soup.find_all("a", href=True)]

    def get_all_images(self) -> list:
        return [img["src"] for img in self.soup.find_all("img", src=True)]

    def get_text_content(self) -> str:
        return self.soup.get_text(separator=" ", strip=True)

    def find_by_selector(self, selector: str):
        return self.soup.select(selector)