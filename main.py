API_KEY = "llx-..."

from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader

import nest_asyncio

#set async communication to retreive data from API
nest_asyncio.apply()

from sys import argv
import json
import pandas as pd

# set up parser
def set_parser():
    '''
    Setup parser with instruction to parse handwritten documents with tables

    Input: None
    Output: LlamaParse object
    '''

    parser = LlamaParse(
        api_key=API_KEY,
        premium_mode=True,
        result_type="markdown",  
        content_guideline_instruction=
        """
        These are handwritten files.
        These files contain tables.
        Tables are also handwritten. Some fully, some partially.
        Sometimes, the writting would be cursive so you must be extra carefull with those.
        Each file may contain a totally different handwriting so be careful about that too.
        These tables can have different structure from each other.
        Extract only the table from the files.
        If a column does not have a name, name it as a single space ' '. Do not remove the column.
        Do not mixup columns or make extra columns. Read writing and names properly
        Save each table as a seperate JSON looking format unless two tables are in exact same format (same column titles and handwriting).
        Maintain actuall table format
        Save each json in a list
        if a page has two tables with different formats, save them separately.
        The final result should be a dictionary/json containing tables, each table named as table_1, table_2, ...
        """
    )

    return parser


#Parse files
def parse_files(parser: LlamaParse, path: str):
    '''
    Use the preset parser to read the given file 
    and extract table out of it in JSON
    format

    Input:
    parser: LlamaParse | LlamaParse object predefined with invoice specific values
    path: str          | Path to pdf files or folder

    '''

    file_extractor = {".pdf": parser}
    table_list = SimpleDirectoryReader(
    input_dir="./tables", file_extractor=file_extractor).load_data()

    table_list = table_list[0].text

    return json.loads(table_list)


def pdf2excel():
    '''
    Generate an excel file from tables stored in a PDF file

    Each page of PDF file is stored in a separate sheet in the excel file
    '''

    parser = set_parser()
    tables = parse_files(parser=parser, path='')

    with pd.ExcelWriter('data/tables.xlsx', engine="xlsxwriter") as writer:
        for sheet_name, table in tables.items():
            df = pd.DataFrame(table)
            df.to_excel(writer, sheet_name=sheet_name, index=False, header=True)

if __name__ == '__main__':
    pdf2excel()