API_KEY = "llx-p3W98EqNfdCJBe7eCC8jYpueztFTWGpiVmOzUbcgC8oiPqcE"

from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader

import nest_asyncio

#set async communication to retreive data from API
nest_asyncio.apply()

from sys import argv
import json

# set up parser
def set_parser():
    '''
    Setup parser with instruction to parse handwritten documents with tables

    Input: None
    Output: LlamaParse object
    '''

    parser = LlamaParse(
        api_key=API_KEY,
        result_type="text",  
        parsing_instruction=
        """
        These are handwritten files.
        These files contain tables.
        Tables are also handwritten.
        Sometimes, the writting would be cursive so you must be extra carefull with those.
        Each file may contain a totally different handwriting so be careful about that too.
        These tables can have different structure from each other.
        Extract only the table from the files.
        If a column does not have a name, name it as a single space ' '. Do not remove the column.
        Do not mixup columns or make extra columns. Read writing and names properly
        Save each table as a seperate JSON file unless two tables are in exact same format (same column titles and handwriting).
        Maintain actuall table format
        Save each json in a list
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
    input_dir="./data", file_extractor=file_extractor).load_data()

    return table_list

def generate_sheets():
    '''
    Generate invoice in JSON format. Takes inputs
    from positional argument through terminal call
    '''

    parser = set_parser()
    sheet = parse_files(parser=parser, path='')

    print(sheet)

    #invoice_json = json.load(invoice)
    
    # with open('invoice.json', 'w') as file:
    #     file.writelines(invoice)


if __name__ == '__main__':
    # if not argv[1]:
    #     path = input('Input the path for your file:')
    # else:
    #     path = argv[1]
    generate_sheets()