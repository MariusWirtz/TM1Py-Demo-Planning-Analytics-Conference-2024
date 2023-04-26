from TM1py import TM1Service

from constants import dev_params, prod_params

CUBE_NAME = "Sales"
ANONYMIZE_DIMENSION = "Customer"

# drop cube from dev
with TM1Service(**dev_params) as tm1_dev:
    if tm1_dev.cubes.exists(CUBE_NAME):
        dimensions_names = tm1_dev.cubes.get_dimension_names(CUBE_NAME)
        tm1_dev.cubes.delete(CUBE_NAME)

        for dimension_name in dimensions_names:
            tm1_dev.dimensions.delete(dimension_name=dimension_name)

with TM1Service(**prod_params) as tm1_prod:
    tm1_prod.cells.clear(cube="Sales", version="{[Version].[Forecast]}")

    if tm1_prod.dimensions.exists("Salesforce Customer"):
        tm1_prod.dimensions.delete("Salesforce Customer")

