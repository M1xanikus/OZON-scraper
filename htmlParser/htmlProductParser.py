import os

from bs4 import BeautifulSoup
import json


class HTMLProductParser:
    def __init__(self, html_code: str, product_name: str, config_path: str = 'config.json'):
        self.html = html_code
        self.product_name = product_name
        self.soup = BeautifulSoup(html_code, "html.parser")
        file_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "configUpdater"))
        config_path = os.path.join(file_root, config_path)
        # Загрузка конфигурации из JSON-файла
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # Получаем селекторы из конфига
        self.selectors = self.config.get("selectors", {})

    def get_title(self) -> str:
        title_selector = self.selectors.get("title", {})
        title = self.soup.find(
            title_selector.get("tag", "h1"),
            class_=title_selector.get("class", "")
        )
        return title.text.strip() if title else "Нет заголовка"

    def get_price(self) -> str:
        price_selector = self.selectors.get("price", {})
        price = self.soup.find(
            price_selector.get("tag", "span"),
            class_=price_selector.get("class", "")
        )
        return price.text.strip() if price else "Цена не найдена"

    def get_description(self) -> str:
        desc_selector = self.selectors.get("description", {})
        desc = self.soup.find(
            desc_selector.get("tag", "div"),
            class_=desc_selector.get("class", "")
        )
        return desc.text.strip() if desc else "Описание отсутствует"

    def get_characteristics(self) -> dict:
        characteristics = {}
        char_selectors = self.selectors.get("characteristics", {})

        container_selector = char_selectors.get("container", {})
        char_blocks = self.soup.find_all(
            container_selector.get("tag", "div"),
            class_=container_selector.get("class", "")
        )

        for block in char_blocks:
            pair_selector = char_selectors.get("key_value_pair", {})
            key_value_pairs = block.find_all(
                pair_selector.get("tag", "dl"),
                class_=pair_selector.get("class", "")
            )

            for pair in key_value_pairs:
                key_selector = char_selectors.get("key", {})
                key_elem = pair.find(
                    key_selector.get("tag", "dt"),
                    class_=key_selector.get("class", "")
                )

                value_selector = char_selectors.get("value", {})
                value_elem = pair.find(
                    value_selector.get("tag", "dd"),
                    class_=value_selector.get("class", "")
                )

                if key_elem and value_elem:
                    key = key_elem.text.strip()
                    value = " ".join([el.text.strip() for el in value_elem.find_all(string=True)])
                    characteristics[key] = value
        return characteristics

    def get_rating(self) -> dict:
        rating_selectors = self.selectors.get("rating", {})
        container_selector = rating_selectors.get("container", {})
        rating_container = self.soup.find(
            container_selector.get("tag", "div"),
            class_=container_selector.get("class", "")
        )

        if not rating_container:
            return {"error": "Рейтинг не найден"}

        value_selector = rating_selectors.get("value", {})
        overall_rating = rating_container.find(value_selector.get("tag", "span"))
        overall_rating = overall_rating.text.strip() if overall_rating else "Нет данных"

        return {"overall_rating": overall_rating}

    def get_reviews(self) -> list:
        reviews = []
        review_selectors = self.selectors.get("reviews", {})

        # Контейнер с отзывами
        container_selector = review_selectors.get("container", {})
        reviews_containers = self.soup.find_all(
            container_selector.get("tag", "div"),
            class_=container_selector.get("class", "")
        )

        for container in reviews_containers:
            # Убираем рекомендации (пока оставляем хардкод, так как нет в конфиге)
            for recommendations in container.find_all("div", class_="jp7_25"):
                recommendations.decompose()

            # Блоки с отзывами
            block_selector = review_selectors.get("review_block", {})
            review_blocks = container.find_all(
                block_selector.get("tag", "div"),
                class_=block_selector.get("class", "")
            )

            if not review_blocks:
                continue

            for block in review_blocks:
                review = {}

                # Имя пользователя
                reviewer_selector = review_selectors.get("reviewer", {})
                reviewer_tag = block.find(
                    reviewer_selector.get("tag", "span"),
                    class_=reviewer_selector.get("class", "")
                )
                review["reviewer"] = reviewer_tag.get_text(strip=True) if reviewer_tag else "Неизвестный"

                # Дата отзыва
                date_selector = review_selectors.get("date", {})
                date_tag = block.find(
                    date_selector.get("tag", "div"),
                    class_=date_selector.get("class", "")
                )
                review["date"] = date_tag.get_text(strip=True) if date_tag else "Нет даты"

                # Текст отзыва
                comment_selector = review_selectors.get("comment", {})
                comment_tag = block.find(
                    comment_selector.get("tag", "span"),
                    class_=comment_selector.get("class", "")
                )
                review["comment"] = comment_tag.get_text(strip=True) if comment_tag else "Нет данных"

                # Рейтинг (количество звезд)
                review["rating"] = self.extract_rating(block)

                # Цвет товара
                color_selector = review_selectors.get("product_color", {})
                product_color_tag = block.find(
                    color_selector.get("tag", "a"),
                    class_=color_selector.get("class", "")
                )
                review["product_color"] = product_color_tag.get_text(strip=True) if product_color_tag else "Нет данных"

                # Медиа (изображения)
                media_selector = review_selectors.get("media", {})
                media_links = [
                    media.get("src", "") for media in block.find_all(
                        media_selector.get("tag", "img"),
                        class_=media_selector.get("class", "")
                    )
                ]
                review["media"] = media_links

                reviews.append(review)

        return reviews

    def extract_rating(self, block) -> int:
        review_selectors = self.selectors.get("reviews", {})
        rating_selector = review_selectors.get("rating", {})
        rating_block = block.find(
            rating_selector.get("tag", "div"),
            class_=rating_selector.get("class", "")
        )

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