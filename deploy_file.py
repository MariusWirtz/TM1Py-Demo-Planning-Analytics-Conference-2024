from TM1py import TM1Service

from constants import prod_params

LOCAL_FILE_NAME = "sales.csv"
TARGET_FILE_NAME = "sales.csv"


def deploy_file():
    with TM1Service(**prod_params) as tm1:
        with open(LOCAL_FILE_NAME, "rb") as file:
            tm1.files.update_or_create(TARGET_FILE_NAME, file_content=file.read())
