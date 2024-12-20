"""
    Анализатор прайс-листов.
    Загружает данные из прайс-листов и предоставляет
    интерфейс для поиска товара по фрагменту названия
    с сортировкой по цене за килограмм
"""

import os
from typing import List, Tuple, Dict, Optional, Union


class PriceMachine:
    """
        Класс для обработки прайс-листов
    """

    def __init__(self) -> None:
        self.data: List[Dict[str, Union[float, str]]] = []

    def load_prices(self, file_path: str = './price_lists') -> None:
        """
            Метод сканирует указанный каталог.
            Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
        """
        for file in os.listdir(file_path):
            if 'price' in file.lower():
                print(f'Обработан файл: "{file}"')
                current_file_path = os.path.join(file_path, file)
                with open(current_file_path, 'r', encoding='utf-8') as opened_file:
                    headers = opened_file.readline().strip().split(',')
                    name_index, price_index, weight_index = PriceMachine._search_product_price_weight(headers)
                    if name_index is not None and price_index is not None and weight_index is not None:
                        data_lines = opened_file.readlines()
                        for line in data_lines:
                            values = line.strip().split(',')
                            row = {
                                'name': values[name_index],
                                'price': float(values[price_index]),
                                'weight': float(values[weight_index]),
                                'price_per_kg': round(float(values[price_index]) /
                                                      float(values[weight_index]), 1),
                                'file': file
                            }
                            self.data.append(row)
                    else:
                        print(f'ВНИМАНИЕ! В файле "{file}" '
                              f'отсутствуют нужные столбцы!')
                if not self.data:
                    print('ВНИМАНИЕ! Файлы не найдены!')
            elif (file.endswith('.csv') or file.endswith('.json')
                  or file.endswith('.txt')):
                print(f'ВНИМАНИЕ! Не соответствует требованиям '
                      f'и не обработан файл: "{file}"')

    @staticmethod
    def _search_product_price_weight(headers: List[str]) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
            Метод возвращает номера столбцов
        """
        columns = {
            'название': 'name',
            'продукт': 'name',
            'товар': 'name',
            'наименование': 'name',
            'цена': 'price',
            'розница': 'price',
            'фасовка': 'weight',
            'масса': 'weight',
            'вес': 'weight'
        }
        name_index = None
        price_index = None
        weight_index = None
        for index, column in enumerate(headers):
            std_column = columns.get(column.lower(), None)
            if std_column == 'name' and name_index is None:
                name_index = index
            elif std_column == 'price' and price_index is None:
                price_index = index
            elif std_column == 'weight' and weight_index is None:
                weight_index = index

        return name_index, price_index, weight_index

    def export_to_html(self, html_file: str = './html/output.html') -> None:
        """
            Метод экспортирует данные в HTML-файл
        """
        if self.data:
            result = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Позиции продуктов</title>
            </head>
            <body>
                <table border="1">
                    <tr style='background-color: grey; color: white;'>
                        <th style="padding: 5px;">Номер</th>
                        <th style="padding: 5px;">Название</th>
                        <th style="padding: 5px;">Цена</th>
                        <th style="padding: 5px;">Фасовка</th>
                        <th style="padding: 5px;">Файл</th>
                        <th style="padding: 5px;">Цена за кг</th>
                    </tr>
            '''
            for number, item in enumerate(self.data):
                result += (
                    f'<tr>\n'
                    f'<td style="padding: 5px;">{number + 1}</td>\n'
                    f'<td style="padding: 5px;">{item["name"]}</td>\n'
                    f'<td style="padding: 5px;">{item["price"]}</td>\n'
                    f'<td style="padding: 5px;">{item["weight"]}</td>\n'
                    f'<td style="padding: 5px;">{item["file"]}</td>\n'
                    f'<td style="padding: 5px;">{item["price_per_kg"]}</td>\n'
                    '</tr>\n'
                )
            result += '''
                </table>
            </body>
            </html>
            '''
            with open(html_file, 'w', encoding='utf-8') as open_html_file:
                open_html_file.write(result)
            print(f'Данные успешно экспортированы в {html_file}')
        else:
            print('Нет данных для экспорта')

    def find_text(self, query: str) -> None:
        """
        Метод находит товары, соответствующие запросу,
        и выводит их в консоль.
        """
        filtered = [row for row in self.data if query.lower()
                    in row['name'].lower()]
        sorted_filtered = sorted(filtered, key=lambda x: x['price_per_kg'])

        if not sorted_filtered:
            print('Совпадений не найдено. Попробуйте новый поиск')
        else:
            print('{:<50} {:<10} {:<10} {:<30} {:<10}'.format(
                'Название', 'Цена', 'Фасовка', 'Файл', 'Цена за кг'))
            for row in sorted_filtered:
                print('{:<50} {:<10} {:<10} {:<30} {:.2f}'.format(
                    row['name'], row['price'], row['weight'],
                    row['file'], row['price_per_kg']))


if __name__ == '__main__':
    pm = PriceMachine()
    pm.load_prices()

    while True:
        user_input = input(
            'Введите текст для поиска (или "выйти" для выхода): '
        ).strip()
        if user_input.lower() == 'выйти':
            print('Работа завершена')
            break
        pm.find_text(user_input)
    pm.export_to_html()
