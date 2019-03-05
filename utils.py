# utils.py
# -----------------------
import os
import xlsxwriter


def increment_by_int(old_value, increment_value):
    if increment_value is None:
        return old_value
    else:
        return old_value + increment_value


def set_value_by_int(old_value, new_value):
    if new_value is None:
        return old_value
    else:
        return new_value


def save_trials_data_to_excel(saved_dir, fname, data_dict):
    if not os.path.exists(saved_dir):
        os.makedirs(saved_dir)
    fpath = os.path.join(saved_dir, fname)
    workbook = xlsxwriter.Workbook(fpath)
    worksheet = workbook.add_worksheet()

    row = 0
    col = 0
    for trial_id in data_dict.keys():
        # write column names (titles) first
        if row == 0:
            worksheet.write(0, 0, 'trial_id')
            col += 1
            for col_name in data_dict[trial_id].keys():
                worksheet.write(row, col, col_name)
                col += 1
        # write the data
        row += 1
        col = 0
        worksheet.write(row, col, trial_id)

        trial_stat = data_dict[trial_id]
        for col_name, value in trial_stat.items():
            worksheet.write(row, col+1, value)
            col += 1
    # close the file and save the data
    workbook.close()
