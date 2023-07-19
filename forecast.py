import pandas as pd
from TM1py import TM1Service
from mdxpy import MdxBuilder, Member, MdxHierarchySet
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from constants import prod_params

CUBE_NAME = "Sales"

CUSTOMER = "All Customers"
SEGMENT = "ON-TRADE"
SOURCE_VERSION = "ACT"
MEASURE = "QUANTITY"


def clear(country, product):
    with TM1Service(**prod_params) as tm1:
        bedrock_filter = f"Product¦{product}&" \
                         f"country¦{country}&" \
                         f"customer¦{CUSTOMER}&" \
                         f"segment¦{SEGMENT}&" \
                         f"salesmeasure¦{MEASURE}&" \
                         f"Version¦Forecast"
        success, status, _ = tm1.processes.execute_with_return(
            process_name="}bedrock.cube.data.clear",
            pCube="Sales",
            pFilter=bedrock_filter)

        if not success:
            raise ValueError(f"Failed with status: '{status}'")


def forecast(start_period, end_period, country, product):
    print(start_period, end_period, country, product)
    with TM1Service(**prod_params) as tm1:

        query = MdxBuilder.from_cube("Sales")
        query.where(
            Member.of("Product", product),
            Member.of("Country", country),
            Member.of("Customer", CUSTOMER),
            Member.of("Segment", SEGMENT),
            Member.of("Sales Measure", MEASURE))
        query.add_hierarchy_set_to_column_axis(MdxHierarchySet.range(
            Member.of("Period", start_period),
            Member.of("Period", end_period)))
        query.add_hierarchy_set_to_row_axis(MdxHierarchySet.member(Member.of("Version", SOURCE_VERSION)))

        df: pd.DataFrame = tm1.cells.execute_mdx_dataframe(query.to_mdx(), shaped=False, skip_zeros=False)
        if df.empty:
            return

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
            return

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
