from spyre import server
import matplotlib.pyplot as plt
import pandas as pd
import glob


def create_data_frame(folder_path):
    csv_files = glob.glob(folder_path + "/*.csv")

    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    frames = []

    for file in csv_files:
        region_id = int(file.split('__')[1])
        df = pd.read_csv(file, header=1, names=headers)
        df.at[0, 'Year'] = df.at[0, 'Year'][9:]
        df = df.drop(df.index[-1])
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df = df.drop('empty', axis=1)
        df.insert(0, 'region_id', region_id, True)
        df['Week'] = df['Week'].astype(int)
        frames.append(df)
    result = pd.concat(frames).drop_duplicates().reset_index(drop=True)
    result = result.loc[(result.region_id != 12) & (result.region_id != 20)]
    result = result.replace({'region_id': {1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19, 9: 20, 10: 21,
                                           11: 9, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15, 19: 16, 21: 17,
                                           22: 18, 23: 6, 24: 1, 25: 2, 26: 6, 27: 5}})
    return result


df = create_data_frame('../lab_2/download')

reg_id_name = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька', 5: 'Житомирська',
    6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 10: 'Кіровоградська',
    11: 'Луганська', 12: 'Львівська', 13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівенська', 17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 20: 'Херсонська',
    21: 'Хмельницька', 22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим'
}


class SimpleApp(server.App):
    title = "AD lab 3 Luniaka"

    inputs = [
        {
            "type": "dropdown",
            "label": "Parameter",
            "options": [{"label": "VCI", "value": "VCI"},
                        {"label": "TCI", "value": "TCI"},
                        {"label": "VHI", "value": "VHI"}],
            "key": "parameter",
            "action_id": "update_data"
        },
        {
            "type": "dropdown",
            "label": "Region",
            "options": [{"label": reg_id_name[region_id], "value": region_id} for region_id in
                        sorted(df['region_id'].unique())],
            "key": "region",
            "action_id": "update_data"
        },
        {
            "type": "text",
            "key": "years_interval",
            "label": "Years Interval",
            "value": "1982-2024"
        },
        {
            "type": "text",
            "key": "weeks_interval",
            "label": "Weeks Interval (e.g., 1-3)",
            "value": "1-3"
        }
    ]

    controls = [{"type": "button", "label": "Update", "id": "update_data"}]

    tabs = ["Table", "Plot"]

    outputs = [{"type": "table", "id": "table", "control_id": "update_data", "tab": "Table", "on_page_load": True},
               {"type": "plot", "id": "plot", "control_id": "update_data", "tab": "Plot", "on_page_load": True}, ]

    def getData(self, params):
        parameter = params["parameter"]
        print(parameter)
        region_id = int(params["region"])
        years = params["years_interval"].split('-')
        weeks_interval = params["weeks_interval"].split('-')

        df_year = df[(df['Year'].astype(int).between(int(years[0]), int(years[1]))) &
                     (df['Week'].between(int(weeks_interval[0]), int(weeks_interval[1]))) &
                     (df['region_id'] == region_id)][['Week', parameter]].set_index('Week')

        return df_year

    def getPlot(self, params):
        fig, ax = plt.subplots(figsize=(16, 8))
        fig.tight_layout(pad=4)

        parameter = params["parameter"]
        region_id = int(params["region"])
        weeks_interval = params["weeks_interval"].split('-')
        years = params["years_interval"].split('-')

        legend_years = []
        for year in range(int(years[0]), int(years[1]) + 1):
            df_year = df[(df['Year'] == str(year)) &
                         (df['Week'].between(int(weeks_interval[0]), int(weeks_interval[1]))) &
                         (df['region_id'] == region_id)][['Week', parameter]].set_index('Week')
            df_year.plot(ax=ax, label=str(year), grid=True)
            legend_years.append(year)

        ax.set_xlabel("Weeks")
        ax.set_ylabel(parameter)
        ax.legend(legend_years, title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')

        return fig


app = SimpleApp()
app.launch()
