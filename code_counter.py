"""
    Count Counter
    A program that counts the lines of code and code characters in a code-base
    Author      :   Israel Dryer
    Modified    :   2019-10-30

"""
import PySimpleGUI as sg
from os import system


def read_file(filename):
    """ open the file and read non-code lines """
    with open(filename, 'r') as f:
        raw = f.readlines()

    # clean and parse initial raw data
    data = [row.strip() for row in raw if row.strip()]

    # identify and strip hash comments
    stage1 = []
    for row in data:
        ix = row.find('#')
        if ix == -1:
            stage1.append(row)
        else:
            if row[:ix]:
                stage1.append(row[:ix])

    # identify and strip 3x" multi-line comments
    stage2 = []
    ml_flag = False
    for row in stage1:
        ml_count = row.count(r'"""')
        if ml_count == 0 and not ml_flag:
            stage2.append(row)
        elif ml_count == 1 and ml_flag:
            ml_flag = False
            ix = row.find(r'"""')
            stage2.append(row[ix+1:])
        elif ml_count == 1 and not ml_flag:
            ml_flag = True
            ix = row.find(r'"""')
            stage2.append(row[:ix])
        else:
            continue

    # identify and strip 3x' multi-line comments
    stage3 = []
    ml_flag = False
    for row in stage2:
        ml_count = row.count(r"'''")
        if ml_count == 0 and not ml_flag:
            stage3.append(row)
        elif ml_count == 1 and ml_flag:
            ml_flag = False
            ix = row.find(r"'''")
            stage3.append(row[ix+1:])
        elif ml_count == 1 and not ml_flag:
            ml_flag = True
            ix = row.find(r"'''")
            stage3.append(row[:ix])
        else:
            continue

    final = [row for row in stage3 if row not in ('', "''", '""')]

    # row and character rounds
    char_count = []
    for row in stage3:
        char_count.append(len(row))
    line_count = len(stage3)

    return final, char_count, line_count


def main():
    filename = sg.popup_get_file('Select a file', title='Code Counter')

    if filename is None:
        sg.popup_error('No file selected', title='ERROR!')
        return
    else:
        clean_data, char_count, line_count = read_file(filename)

        with open('output.txt', 'w') as f:
            # write statistics to file
            f.write('{}statistics'.format(' '*7))
            f.write('\n{}\n'.format('*'*25))
            f.write('Count of lines: {}\n'.format(line_count))
            f.write('Count of characters: {}\n'.format(sum(char_count)))
            f.write('Avg characters per line: {}\n\n'.format(sum(char_count)//line_count))
            f.write('{}clean data'.format(' '*7))
            f.write('\n{}\n'.format('*'*25))

            # write clean data to file
            for row in clean_data:
                f.write(row + '\n')

        sg.popup_quick_message('hello')
        print('\n\nCount of lines:', line_count)
        print('Count of characters:', sum(char_count))
        print('Avg characters per line:', sum(char_count)//line_count)

        # open file with default text editor
        system('output.txt')

if __name__ == '__main__':
    main()
