# CIS 41B Exercise - CO2 Linear Regression with Pandas, NumPy and Matplotlib

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Adapted from PandasDataFrameDashboard in Dataframes.py:
# - kept one class that builds the DataFrame and returns values from it
# - changed the source to pd.read_csv() (Pandas.ipynb) and the output to NumPy
#   arrays, because LinearRegression has to receive arrays, not the DataFrame
# - removed the statistics methods, the calculations belong to LinearRegression
class CO2Data:

    X_COLUMN = "decimal"    # the date as a decimal year, so the slope is per year
    Y_COLUMN = "average"    # measured values, interpolated has estimates in the gaps
    MISSING = -99.99        # what average holds for a month with no measurement

    def __init__(self, filename):
        # Not in the notebooks: na_values (dropna() is on the Missing Data Semantics
        # slide of Pandas Series.pdf). Why: the 5 months marked -99.99 are unusable,
        # I got a slope of 1.76 with them and 1.58 without. How: read_csv() loads
        # -99.99 as NaN and dropna() removes those rows, so x and y stay paired.
        df = pd.read_csv(filename, na_values=self.MISSING)
        self.__df = df[[self.X_COLUMN, self.Y_COLUMN]].dropna()

    @property
    def x(self):
        return self.__df[self.X_COLUMN].to_numpy()

    @property
    def y(self):
        return self.__df[self.Y_COLUMN].to_numpy()

    def __len__(self):
        return len(self.__df)


# Adapted from class_trend() in Numpy.ipynb:
# - kept returning a slope and an intercept for an x array and a y array
# - replaced np.polyfit(), which this assignment doesn't allow, with the given
#   mean/sum formulas. They work on whole arrays, so there are no loops
# - changed x from np.arange() to the array passed in (dates, not 0, 1, 2...)
class LinearRegression:

    def __init__(self, x, y):
        if len(x) < 2 or np.min(x) == np.max(x):
            raise ValueError("A regression line needs at least 2 different x values")
        self.__x = x
        self.__y = y
        self.__slope, self.__intercept = self.__calculate_line()

    def __calculate_line(self):
        x_mean = np.mean(self.__x)
        y_mean = np.mean(self.__y)
        numerator = np.sum((self.__x - x_mean) * (self.__y - y_mean))
        denominator = np.sum((self.__x - x_mean) ** 2)
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        return slope, intercept

    @property
    def slope(self):
        return self.__slope

    @property
    def intercept(self):
        return self.__intercept

    @property
    def predicted(self):
        return self.__slope * self.__x + self.__intercept


# Adapted from the practice plot in Data Visualization.ipynb:
# - kept fig, ax = plt.subplots(), the title, the axis labels and plt.show()
# - added ax.scatter() for the observations and ax.plot() for the calculated line
#   (Scatter Plot vs. Line Plot section), with labels and ax.legend() (Example 3)
class CO2Plot:

    def __init__(self, x, y, predicted):
        self.__x = x
        self.__y = y
        self.__predicted = predicted

    def show(self):
        fig, ax = plt.subplots()
        ax.scatter(self.__x, self.__y, s=8, label="Observed monthly average")
        ax.plot(self.__x, self.__predicted, color="red", label="Linear regression")
        ax.set_title("Atmospheric CO2: Observations and Linear Regression")
        ax.set_xlabel("Year")
        ax.set_ylabel("CO2 (ppm)")
        ax.legend()
        plt.show()


def main():
    try:
        data = CO2Data("CO2.csv")
        x = data.x
        y = data.y
        regression = LinearRegression(x, y)
    except (OSError, KeyError, ValueError) as error:
        print(f"Could not calculate the regression: {error}")
        return

    print(f"Observations used: {len(data)}")
    print(f"Slope: {regression.slope:.4f} ppm per year")
    print(f"Intercept: {regression.intercept:.2f} ppm")
    CO2Plot(x, y, regression.predicted).show()


if __name__ == "__main__":
    main()
