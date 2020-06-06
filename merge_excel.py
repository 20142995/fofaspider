#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import xlrd
import xlwt


def read_excel(file,index=0):
    workbook = xlrd.open_workbook(filename=file)
    sheet = workbook.sheet_by_index(0)
    nrows = sheet.nrows
    for n in range(index,nrows):
        yield sheet.row_values(n)

def write_row(sheet,n,row):
    for i in range(0,len(row)):
        sheet.write(n, i, row[i])

def merge_excel_files(excel_files):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('合并结果')
    row_values = [i for i in read_excel(excel_files[0],0)]
    for file in excel_files[1:]:
        row_values += [i for i in read_excel(file,1)]
    for n,row in enumerate(row_values):
        write_row(sheet,n,row)
    return workbook

def get_all_excel_files(path):
    excel_files = [os.path.join(path,file) for file in os.listdir(path) if '.xls' in file]
    sorted(excel_files, key=str.lower)
    return excel_files
    
def main():
    excel_files = get_all_excel_files('.')
    workbook = merge_excel_files(excel_files)
    workbook.save('merged_from.xls')

if __name__ == '__main__':
    main()
