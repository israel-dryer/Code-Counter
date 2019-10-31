"""
    Count Counter
    A program that counts the lines of code and code characters in a code-base
    Author      :   Israel Dryer
    Modified    :   2019-10-31

"""
import PySimpleGUI as sg
from os import system
import statistics as stats


def read_file(filename):
    """ open the file and read non-code lines """
    with open(filename, 'r') as f:
        raw = f.readlines()

    # clean and parse initial raw data
    data = [row.strip() for row in raw if row.strip()]

    # remove hash comments
    stage1 = []
    for row in data:
        if row.find('#') != -1:
            stage1.append(row[:row.find('#')])
        else:
            stage1.append(row)

    # remove " multiline comments
    stage2 = []
    ml_flag = False # multiline comment flag
    for row in stage1:
        if row.count(r'"""') == 0 and not ml_flag: # not a comment line
            stage2.append(row)
        elif row.count(r'"""') == 1 and not ml_flag: # starting comment line
            ml_flag = True
            stage2.append(row[:row.find('"""')])
        elif row.count(r'"""') == 1 and ml_flag: # ending comment line
            ml_flag = False
            stage2.append(row[row.find('"""')+1:])
        else:
            continue

    # remove ' multiline comments
    stage3 = []
    ml_flag = False # multiline comment flag
    for row in stage2:
        if row.count(r"'''") == 0 and not ml_flag: # not a comment line
            stage3.append(row)
        elif row.count(r"'''") == 1 and not ml_flag: # starting comment line
            ml_flag = True
            stage3.append(row[:row.find("'''")])
        elif row.count(r"'''") == 1 and ml_flag: # ending comment line
            ml_flag = False
            stage3.append(row[row.find("'''")+1:])
        else:
            continue

    clean_code = [row for row in stage3 if row not in ('', "''", '""')]

    # row and character rounds / for calc stats, histogram, charts
    char_cnt = [len(row) for row in clean_code] 

    # statistics
    code_stats = {
        'lines': len(clean_code), 'char_per_line': sum(char_cnt)//len(clean_code), 
        'count': sum(char_cnt), 'mean': stats.mean(char_cnt), 'median': stats.median(char_cnt), 
        'pstdev': stats.pstdev(char_cnt), 'min': min(char_cnt), 'max': max(char_cnt)}

    return clean_code, char_cnt, code_stats


def main():
    filename = sg.popup_get_file('Select a file', title='Code Counter')

    if filename is None:
        sg.popup_error('No file selected', title='ERROR!')
        return
    else:
        clean_code, char_cnt, code_stats = read_file(filename)

        with open('output.txt', 'w') as f:
            # write statistics to file
            f.write('STATISTICS\n' + '='*25 + '\n')
            for key, value in code_stats.items():
                f.write('{}: {:,.0f}\n'.format(key, value))
            
            # write clean data to file
            f.write('\n\nCLEAN CODE\n' + '='*25 + '\n')
            for row in clean_code:
                f.write(row + '\n')

        
        # open file with default text editor
        system('output.txt')


if __name__ == '__main__':
    main()