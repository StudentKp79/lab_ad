from spyre import server
import matplotlib.pyplot as plt
import pandas as pd
import glob

def create_data_frame(folder_path):
    csv_files = glob.glob(folder_path + "/*.csv")
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    frames = []

    for file in csv_files:
        try:
            region_id = int(file.split('__')[1])
            df = pd.read_csv(file, header=1, names=headers)
            df.at[0, 'Year'] = df.at[0, 'Year'][9:]
            df = df.drop(df.index[-1])
            df = df[df['VHI'] != -1]
            df = df.drop('empty', axis=1)
            df.insert(0, 'region_id', region_id, True)
            df['Week'] = df['Week'].astype(int)
            frames.append(df)
        except Exception as e:
            print(f"Error processing file {file}: {e}")
    result = pd.concat(frames).drop_duplicates().reset_index(drop=True)
    result = result.loc[(result.region_id != 12) & (result.region_id != 20)]
    result = result.replace({'region_id': {1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19, 9: 20, 10: 21,
                                           11: 9, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15, 19: 16, 21: 17,
                                           22: 18, 23: 6, 24: 1, 25: 2, 26: 6, 27: 5}})
    return result

df = create_data_frame('download')

reg_id_name = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька', 5: 'Житомирська',
    6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 10: 'Кіровоградська',
    11: 'Луганська', 12: 'Львівська', 13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівенська', 17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 20: 'Херсонська',
    21: 'Хмельницька', 22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим'
}

class DataApp(server.App):
    title = "Аналіз Даних Агрономії"

    inputs = [
        {
            "type": "dropdown",
            "label": "Виберіть Параметр",
            "options": [{"label": "Вегетаційний індекс (VCI)", "value": "VCI"},
                        {"label": "Тепловий індекс (TCI)", "value": "TCI"},
                        {"label": "Індекс здоров'я рослин (VHI)", "value": "VHI"}],
            "key": "parameter",
            "action_id": "update_data"
        },
        {
            "type": "dropdown",
            "label": "Виберіть Регіон",
            "options": [{"label": reg_id_name[region_id], "value": region_id} for region_id in
                        sorted(df['region_id'].unique())],
            "key": "region",
            "action_id": "update_data"
        },
        {
            "type": "dropdown",
            "key": "year_start",
            "label": "Початковий Рік",
            "options": [{"label": str(year), "value": str(year)} for year in sorted(df['Year'].astype(int).unique())],
            "action_id": "update_data"
        },
        {
            "type": "dropdown",
            "key": "year_end",
            "label": "Кінцевий Рік",
            "options": [{"label": str(year), "value": str(year)} for year in sorted(df['Year'].astype(int).unique())],
            "action_id": "update_data"
        },
        {
            "type": "text",
            "key": "weeks_interval",
            "label": "Інтервал Тижнів (наприклад, 1-3)",
            "value": "1-3"
        }
    ]

    controls = [{"type": "button", "label": "Оновити Дані", "id": "update_data"}]

    tabs = ["Таблиця", "Графік"]

    outputs = [
        {"type": "table", "id": "table", "control_id": "update_data", "tab": "Таблиця", "on_page_load": True},
        {"type": "plot", "id": "plot", "control_id": "update_data", "tab": "Графік", "on_page_load": True}
    ]

    def getData(self, params):
        parameter = params["parameter"]
        region_id = int(params["region"])
        year_start = int(params["year_start"])
        year_end = int(params["year_end"])
        weeks_interval = params["weeks_interval"].split('-')

        df_filtered = df[(df['Year'].astype(int).between(year_start, year_end)) &
                         (df['Week'].between(int(weeks_interval[0]), int(weeks_interval[1]))) &
                         (df['region_id'] == region_id)][['Year', 'Week', parameter]]

        return df_filtered

    def getPlot(self, params):
        parameter = params["parameter"]
        region_id = int(params["region"])
        year_start = int(params["year_start"])
        year_end = int(params["year_end"])
        weeks_interval = params["weeks_interval"].split('-')

        df_filtered = df[(df['Year'].astype(int).between(year_start, year_end)) &
                         (df['Week'].between(int(weeks_interval[0]), int(weeks_interval[1]))) &
                         (df['region_id'] == region_id)][['Year', 'Week', parameter]]

        fig, ax = plt.subplots(figsize=(12, 6))

        # Додавання кольорів для кожного року
        years = df_filtered['Year'].unique()
        colors = plt.cm.get_cmap('tab20', len(years))

        for i, year in enumerate(years):
            df_year = df_filtered[df_filtered['Year'] == year]
            ax.plot(df_year['Week'], df_year[parameter], label=str(year), color=colors(i))

        ax.set_title(f"Графік {parameter} для {reg_id_name[region_id]}")
        ax.set_xlabel("Тижні")
        ax.set_ylabel(parameter)
        ax.legend(title='Рік')

        return fig

# Запуск додатку
app = DataApp()
app.launch()

