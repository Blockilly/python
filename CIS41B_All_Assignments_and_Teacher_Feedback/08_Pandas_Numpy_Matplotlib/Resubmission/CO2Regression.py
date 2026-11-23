import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class CO2Data:
    def __init__(self, filename):
        self.df = pd.read_csv(filename)
        # -99.99 in the average column means that month wasn't measured.
        # Keeping only the rows where average isn't -99.99 drops those 5 months,
        # otherwise they pull the regression line down.
        self.df = self.df[self.df["average"] != -99.99]

    def get_x(self):
        return self.df["decimal"].to_numpy()

    def get_y(self):
        return self.df["average"].to_numpy()


class LinearRegression:
    def __init__(self, x, y):
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        self.slope = numerator / denominator
        self.intercept = y_mean - self.slope * x_mean
        self.predicted = self.slope * x + self.intercept


class CO2Plot:
    def show(self, x, y, predicted):
        fig, ax = plt.subplots()
        ax.scatter(x, y, s=8, label="Observed CO2")
        ax.plot(x, predicted, color="red", label="Regression line")
        ax.set_title("Atmospheric CO2 with Linear Regression")
        ax.set_xlabel("Year")
        ax.set_ylabel("CO2 (ppm)")
        ax.legend()
        plt.show()


def main():
    data = CO2Data("CO2.csv")
    x = data.get_x()
    y = data.get_y()

    regression = LinearRegression(x, y)
    print(f"Slope: {regression.slope:.4f} ppm per year")
    print(f"Intercept: {regression.intercept:.2f}")

    CO2Plot().show(x, y, regression.predicted)


if __name__ == "__main__":
    main()
