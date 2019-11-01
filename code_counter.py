"""
    Count Counter
    A program that counts the lines of code and code characters in a code-base
    Author      :   Israel Dryer
    Modified    :   2019-11-01

"""
import PySimpleGUI as sg
from os import system
import statistics as stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')


def clean_data(values):
    """ clean and parse the raw data """
    raw = values['IN_OUT'].split('\n')
    # remove whitespace
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


def save_data(clean_code, code_stats, window):
    """ save clean code and stats to file """
    with open('output.txt', 'w') as f:
        # write statistics to file
        f.write('STATISTICS\n' + '='*25 + '\n')
        for key, value in code_stats.items():
            f.write('{}: {:,.0f}\n'.format(key, value))
        
        # write clean data to file
        f.write('\n\nCLEAN CODE\n' + '='*25 + '\n')
        for row in clean_code:
            f.write(row + '\n')
    
    # update display
    with open('output.txt', 'r') as f:
        window['IN_OUT'].update(f.read())


def display_charts(char_cnt, window):
    """ create charts to display in window """

    def draw_figure(canvas, figure, loc=(0, 0)):
        """ matplotlib helper function """
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    figure = plt.figure(num=1, figsize=(10, 10))

    # histogram
    plt.subplot(121)
    plt.hist(char_cnt)
    plt.title('character count per line')
    plt.ylabel('frequency')

    # line plot
    plt.subplot(122)
    x = range(0, len(char_cnt))
    y = char_cnt
    plt.plot(y)
    plt.fill_between(x, y)
    plt.title('compressed code line counts')
    plt.xlabel('code line number')
    plt.ylabel('number of characters') 

    draw_figure(window['IMG'].TKCanvas, figure)


def display_stats(code_stats, window):
    """ display code stats in the window """
    display = (
          "Lines of code: {lines:,d}" +         
        "\nTotal chars: {count:,d}" + 
        "\nChars per line: {char_per_line:,d}" + 
        "\nMean: {mean:,.0f}" + 
        "\nMedian: {median:,.0f}" +        
        "\nPStDev: {pstdev:,.0f}" + 
        "\nMin: {min:,d}" +           
        "\nMax: {max:,d}") 
    window['STATS'].update(display.format(**code_stats))


def click_file(window):
    """ file button click event; open file and load to screen """
    filename = sg.popup_get_file('Select a file containing Python code:', title='Code Counter')
    if filename is None:
        return
    with open(filename) as f:
        raw = f.read()
        window['IN_OUT'].update(raw)


def click_submit(window, values):
    """ submit button click event; clean and save data """
    clean_code, char_cnt, code_stats = clean_data(values)
    save_data(clean_code, code_stats, window)
    display_charts(char_cnt, window)
    display_stats(code_stats, window)


def btn(name, **kwargs):
    """ create button with default settings """
    return sg.Button(name, size=(16, 1), font=(sg.DEFAULT_FONT, 12), **kwargs)


def main():
    """ main program and GUI loop """
    sg.ChangeLookAndFeel('BrownBlue')
    
    layout = [
        [btn('Load FILE'), btn('CALC!'), btn('RESET'),
         sg.Text('PASTE python code or LOAD from file; then click CALC!', font=(sg.DEFAULT_FONT, 12))],
        [sg.Multiline(key='IN_OUT', size=(160, 25), font=(sg.DEFAULT_FONT, 12))],
        [sg.Canvas(size=(434, 288), key='IMG'), sg.Multiline('', font=(sg.DEFAULT_FONT, 12), key='STATS')]]

    window = sg.Window('Code Counter', layout, resizable=True, finalize=True)
    window['IN_OUT'].expand(expand_x=True, expand_y=True)
    window['STATS'].expand(expand_x=True, expand_y=True)
    window.maximize()

    while True:
        event, values = window.read()
        if event is None:
            break
        if event == 'Load FILE':
            click_file(window)
        if event == 'CALC!':
            try:
                click_submit(window, values)
            except:
                continue
        if event == 'RESET':
            window['IN_OUT'].update('')


if __name__ == '__main__':
    main()