# excel_utils.py
# -----------------------
import os
import xlsxwriter
import xlrd


def read_excel(excel_fname, id_col_name, sheet_name, func_id_data_type=None):
    book = xlrd.open_workbook(excel_fname)
    sheet = book.sheet_by_name(sheet_name)

    # read header values into the list
    col_names = [str(sheet.cell(0, col_index).value) for col_index in xrange(sheet.ncols)]
    data_dict = {}
    for row_index in xrange(1, sheet.nrows):
        col_data = {}
        for col_index in xrange(sheet.ncols):
            col_data[col_names[col_index]] = str(sheet.cell(row_index, col_index).value)

        if func_id_data_type is not None:
            data_dict[func_id_data_type(col_data[id_col_name])] = col_data
        else:
            data_dict[str(col_data[id_col_name])] = col_data

    return data_dict


def fill_excel_col(dest_excel_fname, dest_col_name, dest_id_col_name, dest_sheet_name
                   , source_excel_name, source_col_name, source_id_col_name, source_sheet_name
                   , func_expected_data_type=None):
    # read the source excel into data_dict
    source_data = read_excel(source_excel_name, source_id_col_name, source_sheet_name)

    # read the destinated excel
    destinated_excel = xlrd.open_workbook(dest_excel_fname)
    destinated_sheet = destinated_excel.sheet_by_name(dest_sheet_name)

    edited_excel_fname = '' + os.path.basename(dest_excel_fname)
    edited_excel_dir = os.path.dirname(dest_excel_fname)
    edited_destinated_excel = xlsxwriter.Workbook(os.path.join(edited_excel_dir, edited_excel_fname))
    edited_destinated_sheet = edited_destinated_excel.add_worksheet(destinated_sheet_name)

    # find destinated id column index
    destinated_id_col_index = 0
    for col_index in xrange(destinated_sheet.ncols):
        if str(destinated_sheet.cell(0, col_index).value) == dest_id_col_name:
            destinated_id_col_index = col_index
            break

    # find destinated column index
    destinated_col_index = 0
    for col_index in xrange(destinated_sheet.ncols):
        if str(destinated_sheet.cell(0, col_index).value) == dest_col_name:
            destinated_col_index = col_index
            break

    for row_index in xrange(0, destinated_sheet.nrows):
        # copy all other values
        for col_index in xrange(destinated_sheet.ncols):
            edited_destinated_sheet.write(row_index, col_index, destinated_sheet.cell(row_index, col_index).value)
        # if row_index is 0, we just copy column names (titles), then continue
        if row_index == 0:
            continue

        destinated_id = str(destinated_sheet.cell(row_index, destinated_id_col_index).value)
        # skip empty row
        if destinated_id.strip() == '':
            continue

        if destinated_id in source_data:
            source_value = source_data[destinated_id][source_col_name]
            # convert to expected data type
            if func_expected_data_type is not None:
                source_value = func_expected_data_type(source_value)
            edited_destinated_sheet.write(row_index, destinated_col_index, source_value)

    # save the excel
    edited_destinated_excel.close()


def fill_excel_cols(dest_excel_fname, dest_col_names, dest_id_col_name, dest_sheet_name
                    , source_excel_name, source_col_names, source_id_col_name, source_sheet_name
                    , func_expected_data_type=None):
    for i, dest_col_name in enumerate(dest_col_names):
        source_col_name = source_col_names[i]
        fill_excel_col(dest_excel_fname, dest_col_name, dest_id_col_name, dest_sheet_name
                       , source_excel_name, source_col_name, source_id_col_name, source_sheet_name
                       , func_expected_data_type)


def func_to_int(value):
    return int(float(value))


def func_to_float(value):
    return float(value)


if __name__ == '__main__':
    sour_excel_fname = '/Users/lguan/Documents/Study/Research/Gaze-Dataset/data_processing/csv/1551846098049_meta.xlsx'
    sour_id_name = 'trial_id'
    sour_col_names = ['total_frame', 'avg_error']
    sour_sheet_name = 'Sheet1'
    destinated_excel_fname = '/Users/lguan/Documents/Study/Research/Gaze-Dataset/data_processing/csv/table.xlsx'
    destinated_id_name = 'TrialNumber'
    destinated_col_names = ['NumberOfFrames', 'AverageValError']
    destinated_sheet_name = 'Sheet1'
    # print(read_excel(source_excel_fname, source_id_name, func_id_data_type=func_to_int))
    fill_excel_cols(destinated_excel_fname, destinated_col_names, destinated_id_name, destinated_sheet_name, sour_excel_fname, sour_col_names, sour_id_name, sour_sheet_name, func_to_float)



