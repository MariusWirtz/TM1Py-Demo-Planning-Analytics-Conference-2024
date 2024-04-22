import random

import pandas as pd
from TM1py import Element, Cube, TM1Service, Dimension, Hierarchy, NativeView, ViewTitleSelection, AnonymousSubset, \
    ViewAxisSelection

from constants import prod_params, dev_params, CUSTOMERS

CUBE_NAME = "Sales"

CASHFLOW_01 = -500_000
CASHFLOW_02 = 50_000
CASHFLOW_03 = 75_000
CASHFLOW_04 = 100_000
CASHFLOW_05 = 150_000
CASHFLOW_06 = 250_000

df = pd.read_csv("sales.csv", sep=";")

period_elements = list(df["Period"].unique().astype(str))
version_elements = list(df["Version"].unique())
segment_elements = list(df["Segment"].unique())
country_group_elements = list(df["CountryGroup"].unique())
country_elements = list(df["Country"].unique())
product_category_elements = list(df["ProdCategory"].unique())
product_elements = list(df["ProdGroup"].unique())

product_and_product_category = dict()
country_and_country_group = dict()

for (product, category) in df[["ProdGroup", "ProdCategory"]].itertuples(index=False):
    product_and_product_category[product] = category

for (country, group) in df[["Country", "CountryGroup"]].itertuples(index=False):
    country_and_country_group[country] = group


def build_investments_cube(tm1: TM1Service):
    hierarchy = Hierarchy(name="Year", dimension_name="Year")
    for element in range(2010, 2030, 1):
        hierarchy.add_element(str(element), "Numeric")
    dimension = Dimension(name="Year", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    hierarchy = Hierarchy(name="Investment Period", dimension_name="Investment Period")
    for element in range(-10, 11, 1):
        hierarchy.add_element(str(element), "Numeric")
    dimension = Dimension(name="Investment Period", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    hierarchy = Hierarchy(name="Investments Measure", dimension_name="Investments Measure")
    hierarchy.add_element("Cashflow", "Numeric")
    hierarchy.add_element("NPV", "Numeric")
    hierarchy.add_element("IRR", "Numeric")
    dimension = Dimension(name="Investments Measure", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    hierarchy = Hierarchy(name="Investment", dimension_name="Investment")
    for element in range(1, 10000, 1):
        hierarchy.add_element(f"Investment {str(element).zfill(4)}", "Numeric")
    dimension = Dimension(name="Investment", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    cube = Cube(
        name="Investments",
        dimensions=["Year", "Investment Period", "Investment", "Investments Measure"])
    tm1.cubes.update_or_create(cube)

    cells = dict()
    for investment in range(1, 10000):
        investment = "Investment " + str(investment).zfill(4)

        cells["2023", "0", investment, "Cashflow"] = int(random.normalvariate(CASHFLOW_01, CASHFLOW_01 / 5))
        cells["2023", "1", investment, "Cashflow"] = int(random.normalvariate(CASHFLOW_02, CASHFLOW_02 / 2))
        cells["2023", "2", investment, "Cashflow"] = int(random.normalvariate(CASHFLOW_03, CASHFLOW_03 / 2))
        cells["2023", "3", investment, "Cashflow"] = int(random.normalvariate(CASHFLOW_04, CASHFLOW_04 / 2))
        cells["2023", "4", investment, "Cashflow"] = int(random.normalvariate(CASHFLOW_05, CASHFLOW_05 / 2))
        cells["2023", "5", investment, "Cashflow"] = int(random.normalvariate(CASHFLOW_06, CASHFLOW_06 / 2))
    tm1.cells.write("Investments", cells, use_blob=True)

    view = NativeView(
        cube_name="Investments",
        view_name="Default",
        suppress_empty_columns=True,
        suppress_empty_rows=True,
        titles=[
            ViewTitleSelection(
                dimension_name="Year",
                selected="2023",
                subset=AnonymousSubset(
                    dimension_name="Year",
                    hierarchy_name="Year",
                    elements=["2023"]))],
        columns=[
            ViewAxisSelection(
                dimension_name="Investment Period",
                subset=AnonymousSubset(
                    dimension_name="Investment Period",
                    hierarchy_name="Investment Period",
                    elements=["0", "1", "2", "3", "4", "5"]))],
        rows=[
            ViewAxisSelection(
                dimension_name="Investment",
                subset=AnonymousSubset(
                    dimension_name="Investment",
                    hierarchy_name="Investment",
                    expression="{Tm1SubsetAll([Investment])}")),
            ViewAxisSelection(
                dimension_name="Investments Measure",
                subset=AnonymousSubset(
                    dimension_name="Investments Measure",
                    hierarchy_name="Investments Measure",
                    expression="{Tm1SubsetAll([Investments Measure])}"))])
    tm1.views.update_or_create(view=view)


def build_sales_cube(tm1: TM1Service):
    hierarchy = Hierarchy(
        name="Period",
        dimension_name="Period")
    for year in range(2000, 2030, 1):
        for month in range(1, 13, 1):
            hierarchy.add_element(
                element_name=str(year) + str(month).zfill(2),
                element_type="Numeric")
    dimension = Dimension(name="Period", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    hierarchy = Hierarchy(
        name="Version",
        dimension_name="Version",
        elements=[Element(version, 'Numeric') for version in version_elements])
    hierarchy.add_element("Forecast", "Numeric")
    dimension = Dimension(name="Version", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    hierarchy = Hierarchy(
        name="Segment",
        dimension_name="Segment")
    hierarchy.add_element("All Segments", "Consolidated")
    for segment in segment_elements:
        hierarchy.add_component(parent_name="All Segments", component_name=segment, weight=1)
    dimension = Dimension(name="Segment", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    hierarchy = Hierarchy(
        name="Customer",
        dimension_name="Customer")
    hierarchy.add_element("All Customers", "Consolidated")
    for customer in CUSTOMERS:
        hierarchy.add_component("All Customers", customer, 1)
    hierarchy.add_component("All Customers", "All Customers N", 1)
    dimension = Dimension(name="Customer", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    hierarchy = Hierarchy(name="Product", dimension_name="Product")
    for product, category in product_and_product_category.items():
        if category not in hierarchy:
            hierarchy.add_element(category, "Consolidated")
        hierarchy.add_component(category, product, 1)
    dimension = Dimension(name="Product", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    hierarchy = Hierarchy(name="Country", dimension_name="Country")
    for country, country_group in country_and_country_group.items():
        if country_group not in hierarchy:
            hierarchy.add_element(country_group, "Consolidated")
        hierarchy.add_component(country_group, country, 1)
    dimension = Dimension(name="Country", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    hierarchy = Hierarchy(name="Sales Measure", dimension_name="Sales Measure")
    hierarchy.add_element("Quantity", "Numeric")
    hierarchy.add_element("Revenue", "Numeric")
    hierarchy.add_element("Price", "Numeric")
    dimension = Dimension(name="Sales Measure", hierarchies=[hierarchy])
    tm1.dimensions.update_or_create(dimension)

    cube = Cube(
        name=CUBE_NAME,
        dimensions=["Period", "Version", "Segment", "Customer", "Product", "Country", "Sales Measure"])
    tm1.cubes.update_or_create(cube)
    data = df.astype(str).copy()
    data["Measure"] = "Quantity"
    tm1.cells.write_dataframe(
        cube_name=CUBE_NAME,
        data=data[["Period", "Version", "Segment", "Customer", "ProdGroup", "Country", "Measure", "Quantity"]],
        use_blob=True)

    view = NativeView(
        cube_name="Sales",
        view_name="Default",
        suppress_empty_columns=True,
        suppress_empty_rows=True,
        titles=[
            ViewTitleSelection(
                dimension_name="Segment",
                selected="On-Trade",
                subset=AnonymousSubset(
                    dimension_name="Segment",
                    hierarchy_name="Segment",
                    elements=["On-Trade"])),
            ViewTitleSelection(
                dimension_name="Customer",
                selected="All Customers",
                subset=AnonymousSubset(
                    dimension_name="Customer",
                    hierarchy_name="Customer",
                    elements=["All Customers"])),
            ViewTitleSelection(
                dimension_name="Sales Measure",
                selected="Quantity",
                subset=AnonymousSubset(
                    dimension_name="Sales Measure",
                    hierarchy_name="Sales Measure",
                    elements=["Quantity"]))],
        columns=[
            ViewAxisSelection(
                dimension_name="Period",
                subset=AnonymousSubset(
                    dimension_name="Period",
                    hierarchy_name="Period",
                    expression="{TM1SORT( {TM1SUBSETALL( [Period] )}, DESC)}")),
            ViewAxisSelection(
                dimension_name="Version",
                subset=AnonymousSubset(
                    dimension_name="Version",
                    hierarchy_name="Version",
                    expression="{TM1SUBSETALL( [Version] )}"))],
        rows=[
            ViewAxisSelection(
                dimension_name="Country",
                subset=AnonymousSubset(
                    dimension_name="Country",
                    hierarchy_name="Country",
                    expression="{DESCENDANTS({[Country].[Central]})}")),
            ViewAxisSelection(
                dimension_name="Product",
                subset=AnonymousSubset(
                    dimension_name="Product",
                    hierarchy_name="Product",
                    expression="{Tm1SubsetAll([Product])}"))])
    tm1.views.update_or_create(view=view, private=False)

    tm1.cells.clear(
        cube=CUBE_NAME,
        period="{[period].[202201],[period].[202202],[period].[202203]}")


def drop_sales_cubes(tm1):
    if tm1.cubes.exists(CUBE_NAME):
        dimensions_names = tm1.cubes.get_dimension_names(CUBE_NAME)
        tm1.cubes.delete(CUBE_NAME)

        for dimension_name in dimensions_names:
            tm1.dimensions.delete(dimension_name=dimension_name)


with TM1Service(**prod_params) as tm1_prod:
    with TM1Service(**dev_params) as tm1_dev:
        if tm1_prod.cubes.exists("Sales"):
            tm1_prod.cubes.delete("Sales")
        build_sales_cube(tm1_prod)

        # drop cube from dev
        drop_sales_cubes(tm1_dev)

        # cube: year, relative year, investment, measure(cashflow, NPV, IRR)
    if tm1_prod.cubes.exists("Investments"):
        tm1_prod.cubes.delete("Investments")
    build_investments_cube(tm1_prod)

    if tm1_prod.dimensions.exists("Salesforce Product"):
        tm1_prod.dimensions.delete("Salesforce Product")
