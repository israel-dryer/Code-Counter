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
#import matplotlib
#matplotlib.use('TkAgg')


def clean_data(values):
    """ clean and parse the raw data """
    raw = values['INPUT'].split('\n')
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
        for row in clean_code:
            f.write(row + '\n')
    
    # update display
    with open('output.txt', 'r') as f:
        window['OUTPUT'].update(f.read())


def display_charts(char_cnt, window):
    """ create charts to display in window """

    def draw_figure(canvas, figure, loc=(0, 0)):
        """ matplotlib helper function """
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack()
        return figure_canvas_agg

    figure = plt.figure(num=1, figsize=(4, 5))

    # histogram
    plt.subplot(211)
    plt.hist(char_cnt)
    plt.title('character count per line')
    plt.ylabel('frequency')
    plt.tight_layout()

    # line plot
    plt.subplot(212)
    x = range(0, len(char_cnt))
    y = char_cnt
    plt.plot(y)
    plt.fill_between(x, y)
    plt.title('compressed code line counts')
    plt.xlabel('code line number')
    plt.ylabel('number of characters') 
    plt.tight_layout()
    draw_figure(window['IMG'].TKCanvas, figure)


def display_stats(code_stats, window):
    """ display code stats in the window """
    window['LINES'].update('{:,d}'.format(code_stats['lines']))
    window['CHARS'].update('{:,d}'.format(code_stats['count']))
    window['CPL'].update('{:,d}'.format(code_stats['char_per_line']))
    window['MEAN'].update('{:,.0f}'.format(code_stats['mean']))
    window['MEDIAN'].update('{:,.0f}'.format(code_stats['median']))
    window['PSTDEV'].update('{:,.0f}'.format(code_stats['pstdev']))
    window['MAX'].update('{:,d}'.format(code_stats['max']))
    window['MIN'].update('{:,d}'.format(code_stats['min']))


def reset_stats(window):
    """ clear the stats fields """
    window['LINES'].update('{:,d}'.format(0))
    window['CHARS'].update('{:,d}'.format(0))
    window['CPL'].update('{:,d}'.format(0))
    window['MEAN'].update('{:,.0f}'.format(0))
    window['MEDIAN'].update('{:,.0f}'.format(0))
    window['PSTDEV'].update('{:,.0f}'.format(0))
    window['MAX'].update('{:,d}'.format(0))
    window['MIN'].update('{:,d}'.format(0))


def click_file(window):
    """ file button click event; open file and load to screen """
    filename = sg.popup_get_file('Select a file containing Python code:', title='Code Counter')
    if filename is None:
        return
    with open(filename) as f:
        raw = f.read()
        window['INPUT'].update(raw)


def click_submit(window, values):
    """ submit button click event; clean and save data """
    clean_code, char_cnt, code_stats = clean_data(values)
    save_data(clean_code, code_stats, window)
    display_charts(char_cnt, window)
    display_stats(code_stats, window)
    window['T2'].select()


def btn(name, **kwargs):
    """ create button with default settings """
    return sg.Button(name, size=(16, 1), font=(sg.DEFAULT_FONT, 12), **kwargs)

def stat(text, width=10, relief=None, justification='left', key=None):
    elem = sg.Text(text, size=(width, 1), relief=relief, justification=justification, key=key)
    return elem

def main():
    """ main program and GUI loop """
    sg.ChangeLookAndFeel('BrownBlue')
    
    tab1 = sg.Tab('Raw Code', 
        [[sg.Multiline(key='INPUT', pad=(0, 0), font=(sg.DEFAULT_FONT, 12))]], 
        background_color='gray', key='T1')
    tab2 = sg.Tab('Clean Code', 
        [[sg.Multiline(key='OUTPUT', pad=(0, 0), font=(sg.DEFAULT_FONT, 12))]], 
        background_color='gray25', key='T2')

    stat_col = sg.Column([
        [stat('Lines of code'), stat(0, 8, 'sunken', 'right', 'LINES'),
         stat('Total chars'), stat(0, 8, 'sunken', 'right', 'CHARS')],
        [stat('Chars per line'), stat(0, 8, 'sunken', 'right', 'CPL'),
         stat('Mean'), stat(0, 8, 'sunken', 'right', 'MEAN')],
        [stat('Median'), stat(0, 8, 'sunken', 'right', 'MEDIAN'),
         stat('PStDev'), stat(0, 8, 'sunken', 'right', 'PSTDEV')],
        [stat('Max'), stat(0, 8, 'sunken', 'right', 'MAX'),
         stat('Min'), stat(0, 8, 'sunken', 'right', 'MIN')]], pad=(5, 10), key='STATS')

    lf_col = [
        [btn('Load FILE'), btn('CALC!'), btn('RESET')], 
        [sg.TabGroup([[tab1, tab2]], title_color='black', key='TABGROUP')]]

    rt_col = [
        [sg.Text('Statistics', size=(20, 1), pad=((5, 5), (15, 5)), 
                    font=(sg.DEFAULT_FONT, 14, 'bold'), justification='center')],
        [stat_col], 
        [sg.Text('Visualization', size=(20, 1), 
            font=(sg.DEFAULT_FONT, 14, 'bold'), justification='center')],        
        [sg.Canvas(key='IMG')]]

    layout = [[sg.Column(lf_col, element_justification='left', pad=(0, 10), key='LCOL'), 
               sg.Column(rt_col, element_justification='center', key='RCOL')]]

    window = sg.Window('Code Counter', layout, resizable=True, finalize=True)
    
    # set screen size and position
    x1, y1 = window.get_screen_size()
    x2 = int(x1/1.6)
    y2 = int(x2/1.5)
    window.size = (x2, y2)
    pos_x = (x1 - x2)//2
    pos_y = (y1 - y2)//2
    window.move(pos_x, pos_y)
    # window.maximize()

    for elem in ['INPUT','OUTPUT','LCOL','TABGROUP']:
        window[elem].expand(expand_x=True, expand_y=True)

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
            window['INPUT'].update('')
            window['OUTPUT'].update('')
            reset_stats(window)
            

if __name__ == '__main__':
    main()