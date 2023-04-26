import pandas as pd
from TM1py import TM1Service
from mdxpy import MdxBuilder, Member, MdxHierarchySet
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from constants import prod_params

CUBE_NAME = "Sales"

CUSTOMER = "All Customers"
SEGMENT = "ON-TRADE"
VERSION = "ACT"
MEASURE = "QUANTITY"


def forecast():
    with TM1Service(**prod_params) as tm1:
        countries = ["Austria", "Belgium", "Germany", "France", "Netherlands"]
        products = tm1.elements.get_leaf_element_names("Product", "Product")

        for country in countries:

            for product in products:
                query = MdxBuilder.from_cube("Sales")
                query.where(
                    Member.of("Product", product),
                    Member.of("Country", country),
                    Member.of("Customer", CUSTOMER),
                    Member.of("Segment", SEGMENT),
                    Member.of("Sales Measure", MEASURE))
                query.add_hierarchy_set_to_column_axis(MdxHierarchySet.range(
                    Member.of("Period", "201501"),
                    Member.of("Period", "202112")))
                query.add_hierarchy_set_to_row_axis(MdxHierarchySet.member(Member.of("Version", VERSION)))

                df: pd.DataFrame = tm1.cells.execute_mdx_dataframe(query.to_mdx(), shaped=False, skip_zeros=False)
                if df.empty:
                    continue

                del df["Version"]
                df["Period"] = pd.to_datetime(df['Period'], format="%Y%m")

                last_period = df['Period'].iloc[-1]

                # Fit Holt Winters model and get forecasts
                try:
                    model_holt_winters = ExponentialSmoothing(
                        df['Value'],
                        trend='mul',
                        seasonal='mul',
                        seasonal_periods=12).fit()

                except:
                    print(f"Failed to predict {country} and {product}")
                    continue

                forecasts_holt_winters = model_holt_winters.forecast(12)

                cells = dict()
                for p, value in enumerate(forecasts_holt_winters, start=1):
                    period = last_period + pd.DateOffset(months=p)

                    cells[
                        period.strftime("%Y%m"),
                        "Forecast",
                        SEGMENT,
                        "All Customers N",
                        product,
                        country,
                        MEASURE] = int(value)

                tm1.cells.write(CUBE_NAME, cells, use_ti=True)
