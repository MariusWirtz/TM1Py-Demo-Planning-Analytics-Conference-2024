from TM1py import TM1Service

from constants import prod_params

LOCAL_FILE_NAME = "sales.csv"
TARGET_FILE_NAME = "sales.csv"


def deploy_file(file_name, file):
    with TM1Service(**prod_params) as tm1:
        tm1.files.update_or_create(file_name, file_content=file.read())
