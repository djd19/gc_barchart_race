import re
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.animation as animation


from functools import cached_property
from collections import defaultdict
from IPython.display import HTML


class BCGenerator:

    def __init__(self, folder_path, data_path=None,
                 save_path=None, name_map=None,
                 title="Group Chat Message Count"):
        """Initialise instance.

        Parameters
        ----------
        folder_path : str
            Path to folder containing data. Output will 
            be saved at this location.
        save_path : str
            Path where barchart race should be save.
            Extension should be mp4.
        """

        self.folder_path = folder_path
        self.title = title

        if name_map is not None:
            assert isinstance(name_map, dict), f"name_map must be a dict. Received a {type(name_map).__name__}."
        self.name_map = name_map

        self.data_path = f"{folder_path}/data.txt" if data_path is None else data_path
        self.save_path = f"{folder_path}/barchart_race.mp4" if save_path is None else save_path

    @cached_property
    def count_df(self):

        data = defaultdict(lambda: defaultdict(int))

        pattern = re.compile(
            r"(\d{1,2}\/\d{1,2}\/\d{2}), (\d{1,2}:\d{1,2}) - ([^:]*):")
        date_format = "%m/%d/%y"

        with open(self.data_path, "r") as f:
            for line in f.readlines():
                match = pattern.match(line)

                if match:
                    date = datetime.datetime.strptime(
                        match.group(1), date_format)
                    name = match.group(3)

                    data[name][date] += 1

        df = pd.DataFrame(data)

        start_date = min(df.index)
        end_date = max(df.index)

        df.reindex(pd.date_range(start_date, end_date, freq="D"))
        df = df.fillna(0)
        
        if self.name_map is not None:
            df = df.rename(columns=self.name_map)

        return df

    @cached_property
    def cumulative_count_df(self):

        df = self.count_df
        df = df.cumsum(axis=0)

        return df

    @cached_property
    def dates(self):

        return self.count_df.index

    # TODO:
    def assign_colors(self):
        """Keep colors the same for each person."""

        pass

    def _draw_barchart(self, date, ax, n=10):

        day = self.cumulative_count_df.loc[date].sort_values().tail(n)

        ax.clear()
        ax.barh(day.index, day)

        str_date = datetime.datetime.strftime(date, "%Y-%m-%d")
        ax.text(1, 0.4, str_date, transform=ax.transAxes, color="#777777",
                size=40, ha="right", weight=800)
        ax.text(0, 1.025, self.title, transform=ax.transAxes,
                size=24, weight=600, ha="left")

        ax.text(0.99, 0.025, 'by @delacruz', transform=ax.transAxes,
                ha='right', color='#777777',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='white'))

    def generate_barchart(self, time_interval_between_frames=200, *args, **kwargs):
        """Save Bar Chart Animation race.

        Parameters
        ----------
        interval_between_frames : int
            Time in milliseconds between frames.
        """

        fig, ax = plt.subplots(figsize=(15, 8))
        animator = animation.FuncAnimation(
            fig, lambda date: self._draw_barchart(date, ax, *args, **kwargs),
            frames=self.dates, interval=time_interval_between_frames)

        HTML(animator.save(self.save_path))
