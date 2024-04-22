import os

from TM1py import Hierarchy, Dimension, TM1Service
from simple_salesforce import Salesforce

from constants import prod_params

CUSTOMER_DIMENSION_NAME = "Salesforce Products"


def integrate():
    # connect to SF with Simple Salesforce package
    sf = Salesforce(
        username=os.environ.get("SF_USER"),
        password=os.environ.get("SF_PWD"),
        security_token=os.environ.get("SF_TOKEN"))

    # Define query
    query = "SELECT Id, Name, ProductCode, Age__c, Players__c From Product2"

    # query data
    data = sf.query(query)
    records = data["records"]

    # define TM1 structures in Python
    hierarchy = Hierarchy(
        name=CUSTOMER_DIMENSION_NAME,
        dimension_name=CUSTOMER_DIMENSION_NAME)

    # add element attributes to hierarchy
    hierarchy.add_element_attribute("Id", "Alias")
    hierarchy.add_element_attribute("Age", "String")
    hierarchy.add_element_attribute("Players", "String")

    cells = dict()
    for record in records:
        # add element to hierarchy
        hierarchy.add_element(record['Name'], 'Numeric')

        # write attribute values
        cells[record['Name'], "Id"] = str(record["Id"])
        cells[record['Name'], "Age"] = str(record["Age__c"])
        cells[record['Name'], "Players"] = str(record["Players__c"])

    dimension = Dimension(name=CUSTOMER_DIMENSION_NAME, hierarchies=[hierarchy])

    # connect to TM1
    with TM1Service(**prod_params) as tm1:
        # create dimension and write attribute values
        tm1.dimensions.update_or_create(dimension=dimension)
        tm1.cells.write("}ElementAttributes_" + dimension.name, cells, use_blob=True)


if __name__ == "__main__":
    integrate()