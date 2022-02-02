# img_viewer.py
import pandas as pd
import PySimpleGUI as sg
import os.path

# First the window layout in 2 columns
Kerns = ['All', 'RBF', 'Linear', 'Poly', 'Sigmoid']
file_list_column = [
    
    
    [sg.Text("Corpus Folder Path"),
     sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
     sg.FolderBrowse()],
    [sg.Listbox( values=[], enable_events=True, size=(40, 10), key="-FILE LIST-" )],
    
    
    
    [sg.Text('Settings: ')],
    [
     sg.Text('MFW', size=(10, 1)), sg.InputText(key='-mfw-', default_text = '1000', size = (10, 1)),
     sg.Text('Culling', size=(10, 1)), sg.InputText(key='-cull-', default_text = '0', size = (10, 1))
    
    ],
    [
     sg.Text('Chunking', size=(10, 1)), sg.InputText(key='-chunk-', default_text = '1', size = (10, 1)),
     sg.Text('Kernel', size=(10, 1)), sg.Combo(['All', 'RBF', 'Linear', 'Poly', 'Sigmoid'], key = '-kernel-', size=(10,5), default_value = 'All', enable_events=True)
 
    ],
    [ sg.Text("Summary", size=(10,1)), sg.Checkbox("", default = False, size = (2,1), key = '-summary-'), sg.Text('', size=(10,1)), sg.Button('Update Settings'), sg.Button('Default')
     ],
    
    [sg.Text('____________________________________________________')],
    [sg.Text("Export Path:"), sg.In(size=(25, 1), enable_events=True, key="-export_path-"),
     sg.FolderBrowse()],
     
    [sg.Text("File Name:"), sg.InputText('Housman Export', size=(25,1), key = "-export_name-"), sg.Button('Export')],
    [sg.Text('____________________________________________________')],
    [sg.Text('(Optional) Data Assessment'), sg.Button('Create Permutations')],
    [sg.Text("Classify every N'th step:"), sg.Input(size = (10,1), key = '-entered_cycles-', default_text = '5'), sg.Button('Mass Classify')]

  
]


results_column = [
    [sg.Button('Classify', size=(25,1))],
    [sg.Text("Your results will appear here")],
    [sg.Text(size=(70, 30), key="-RES-", )],
    ]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(results_column)
    ]
]

window = sg.Window("A.I. Housman", layout)
Pressed = None 
# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    
    if event == 'Classify':
        if Pressed == 1 and values['-summary-'] == False:
            final = Housman(folder, nMFW = int(entered_nMFW), culling = int(entered_Culling), chunks = int(entered_Chunking), Kernels = (entered_Kernel), summary = entered_Summary)
            Shown_DF = final.to_string()
            window["-RES-"].update(Shown_DF)
        elif Pressed == 1 and values['-summary-'] == True:
            final = Housman(folder, nMFW = int(entered_nMFW), culling = int(entered_Culling), chunks = int(entered_Chunking), Kernels = (entered_Kernel), summary = entered_Summary)
            window["-RES-"].update(final)
        else:
            final = Housman(folder)
            Shown_DF = final.to_string()
            window["-RES-"].update(Shown_DF)
        
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".txt"))
        ]
        window["-FILE LIST-"].update(fnames)
        
    if event == 'Update':
      entered_nMFW = values['-mfw-']
      entered_Culling = values['-cull-']
      entered_Chunking = values ['-chunk-']
      entered_Kernel = values ['-kernel-'].lower()
      entered_Summary = values['-summary-']
      Pressed = 1
     
    if event == 'Default':
      window["-mfw-"].update('1000')
      window["-cull-"].update('00')
      window["-chunk-"].update('1')

      
    if event == 'Export':
        #export_path = values['-export_path-'] + '/' + values['-export_name-'] + '.xlsx'
        #writer = pd.ExcelWriter(export_path)
        export_path = values['-export_path-'] + '/' + values['-export_name-'] + '.csv'
        
        try: 
            #final.to_excel(writer)
            final.to_csv(export_path)
            #writer.save()
        except:
            export_error = "ERROR! It appears you have not created anything to classify. Use the 'classify' Button first!"
            window["-RES-"].update(export_error)

    if event == 'Create Permutations':
        data = folder = values["-FOLDER-"]
        author_set = Genre_Prep(data)
        calc_update = ("-"*40 + "\n")*2 + "Total of " + str(len(author_set)) + " different permutations" + "\n" + ("-"*40 + "\n")*2
        window["-RES-"].update(calc_update)
    
    if event == 'Mass Classify':
        entered_nMFW = values['-mfw-']
        entered_Culling = values['-cull-']
        entered_Chunking = values ['-chunk-']
        entered_Kernel = values ['-kernel-'].lower()
        entered_Summary = values['-summary-']
        Pressed = 1
        temp_list = []
        entered_cycles = int(values['-entered_cycles-'])
        
        for i in range(0, len(author_set), entered_cycles):
            #temp_list.append((author_set[i], Housman(data = Data_Assess(author_set[i], data), nMFW = int(entered_nMFW), culling = int(entered_Culling), chunks = int(entered_Chunking), Kernels = (entered_Kernel), summary = entered_Summary)))
            temp_list.append((Housman(data = Data_Assess(author_set[i], data), nMFW = int(entered_nMFW), culling = int(entered_Culling), chunks = int(entered_Chunking), Kernels = (entered_Kernel), summary = entered_Summary)))
        
        #final = pd.DataFrame(temp_list)
        final = pd.concat(temp_list)
        window["-RES-"].update(final)
        

        

window.close()


"""
FEATURE MAP:
    - Move settings menu to above file browser                                  [DONE]
    - Make Results viewer significantly larger                                  [DONE]
    - Add Kernel Selection                                                      [DONE]
    - Improve how results are shown ('Overall Classificiation' etc.)            [DONE]      
        - Add 'Data Assessment' tab to GUI - which can:                         [DONE]
            - Be given a folder of text files                                   [DONE]
            - Create all possible permutations of training data                 [DONE]
            - Create permutations of 2/3+ texts from each author                [Parked]
            - Classify all data based on steps (i.e every 5th or 10th etc.)     [DONE]
            - Show the above classifications in a concise summary               [DONE]
    - Allow export of all classifications                                       [DONE]
    - Clean up text formatting on summary classifications
    - Add 'History' tab                                                         [Parked]

"""


