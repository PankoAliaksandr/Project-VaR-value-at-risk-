# Libraries
from pandas_datareader import data as pdr
from pandas_datareader._utils import RemoteDataError
import scipy.stats as st
from datetime import date
from dateutil.relativedelta import relativedelta
from arch import arch_model


class VaR:

    # Constructor
    def __init__(self, confidence_level, standard_deviation, stock_price,
                 number_of_stocks, stock_name, start_date, end_date):

        # Download data from Yahoo Finance
        try:
            self.__stock_data = pdr.get_data_yahoo(stock_name,
                                                   start=start_date,
                                                   end=end_date)
        # handle error
        except RemoteDataError:
            print 'Stock symbol "{}" is not valid'.format(stock_name)

        self.__stock_data = self.__stock_data['Close']
        self.__returns = None
        self.__model = None
        self.__forecasted_volatility = None
        self.__z_score = None
        self.__confidence_level = confidence_level
        self.__standard_deviation = standard_deviation
        self.__number_of_stocks = number_of_stocks
        self.__stock_price = stock_price

    def get_stock_data(self):
        return self.__stock_data

    def __calculate_VaR(self, mode=0):

        if mode == 0:
            self.__z_score = st.norm.ppf(self.__confidence_level)
            amount = self.__stock_price * self.__number_of_stocks
            VaR = self.__z_score * self.__standard_deviation * amount

        if mode == 1:
            # Use last available price
            stock_price = self.__stock_data[-1]
            VaR = self.__z_score * (self.__forecasted_volatility / 100) * \
                stock_price * self.__number_of_stocks

        return VaR

    def __calculate_returns(self):
        self.__returns = 100 * self.__stock_data.pct_change().dropna()

    def get_returns(self):
        return self.__returns

    def __implement_GARCH_1_1(self):
        self.__model = arch_model(self.__returns, vol='Garch', p=1, q=1,
                                  dist='Normal')

    def __forecast_volatility(self):
        results = self.__model.fit()
        forecast = results.forecast()
        self.__forecasted_volatility = forecast.variance.iloc[-1]

    def __print_results(self):
        print('VaR value with given volatility: %f'
              % self.__VaR_value_with_given_volatility)
        print('VaR value with forecasted volatility: %f'
              % self.__VaR_value_with_forecasted_volatility)

    def main(self):
        # Task 1
        print('VaR task 1: %f' % self.__calculate_VaR())
        # Task 2
        self.__calculate_returns()
        self.__implement_GARCH_1_1()
        self.__forecast_volatility()
        print('VaR task 2: %f' % self.__calculate_VaR(mode=1))


end_date = date.today()
start_date = end_date - relativedelta(years=1)
VaR = VaR(0.95, 0.025, 126, 100000, 'AAPL', start_date, end_date)
VaR.main()
VaR.get_stock_data()
