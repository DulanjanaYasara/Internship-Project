import gspread
from oauth2client.service_account import ServiceAccountCredentials


class SpreadsheetConnector:
    """Used to connect with the Google Spreadsheet"""

    def __init__(self, json_data_file):
        # use creds to create a client to interact with the Google Drive API
        """

        :type json_data_file: str
        :param json_data_file: path to the json file
        """
        self.scope = ['https://spreadsheets.google.com/feeds']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(json_data_file, self.scope)
        self.client = gspread.authorize(self.creds)

    def export_row(self, workbook_name, row_index, sheetNo=1, column_data=list([]), column_index=list([])):
        # type: (str, int, int, list, list) -> None
        """Used to export list of data into columns based on their column indexes and the respective row index"""
        if row_index <= 1:
            print 'Error in writing'
            return

        # Find a workbook by name and open the sheet
        sheet = self.client.open(workbook_name).get_worksheet(sheetNo - 1)
        for i in range(len(column_data)):
            sheet.update_cell(row_index, column_index[i], column_data[i])

    def export_cell_range(self, workbook_name, data, cell_range, sheet_no=1):
        # type: (str, list, str, int) -> None
        """Used to export list of data into a cell range"""

        # 'data' should be given as a list proceeding row-wise
        # 'cell_range' should be given as a text like 'A1:C7'

        # Find a workbook by name and open the sheet
        sheet = self.client.open(workbook_name).get_worksheet(sheet_no - 1)

        # Update cell range
        cell_list = sheet.range(cell_range)
        for i, j in enumerate(cell_list):
            j.value = data[i]
        sheet.update_cells(cell_list)  # Update in batch

    def import_row(self, row_index, workbook_name, sheet_no=1, columns=list([])):
        # type: (int, str, int, list) -> list
        """Used to import list of data from columns based on their column indexes and the respective row index"""
        if row_index <= 1:
            print 'Error in reading'
            return []

        # Find the workbook by name and open sheet
        sheet = self.client.open(workbook_name).get_worksheet(sheet_no - 1)
        ans = []
        for i in range(len(columns)):
            ans.append(sheet.cell(row_index, columns[i]).value)

        return ans

    def import_all(self, workbook_name, sheet_no=1):
        # type: (str, int) -> list
        """Used to import all data in the spreadsheet"""

        # Find the workbook by name and open sheet
        sheet = self.client.open(workbook_name).get_worksheet(sheet_no - 1)
        return sheet.get_all_values()

    def import_row_all(self, workbook_name, row_index, sheet_no=1):
        # type: (str, int, int) -> list
        """Used to import all data of the respective row"""

        # Find the workbook by name and open sheet
        sheet = self.client.open(workbook_name).get_worksheet(sheet_no - 1)
        return sheet.row_values(row_index)

    def import_column_all(self, workbook_name, column_index, sheet_no=1):
        # type: (str, int, int) -> list

        """Used to import all data of the respective column"""

        # Find the workbook by name and open sheet
        sheet = self.client.open(workbook_name).get_worksheet(sheet_no - 1)
        return sheet.col_values(column_index)
