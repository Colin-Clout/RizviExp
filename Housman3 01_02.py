def Housman(data, nMFW = 1000, culling = 0, Kernels = 'all', chunks = 1, summary = False):
    '''Troubleshooting --Manual Data--
    //data = '/Users/nate/Documents/Academia/Sample Corpora/Small'
    data = '/Users/nate/Desktop/Housman Data Assess/Minor Corpus'
    nMFW = 600
    culling = 0
    Kernels = 'all'
    chunks = 6
    summary = False 
    '''
    dfList = []
    import pandas as pd; import string; import collections; from sklearn import svm; from os import listdir; import re
        #troubleshooting: data = '/Users/nate/Documents/Academia/PhD Search/Test Corpus'

    if chunks == 1:
        Corpus_List = Data_Prep(data, full=True)
    else: 
        data = splitter(data, n=chunks)
        Corpus_List = Data_Prep(data, full = True)

        

    for i in range (0, len(Corpus_List)): 
        
        with open(Corpus_List[i], "r") as Corpus_List[i]: #This line and below mimics line 14 in R studio
            Document = Corpus_List[i].read().split()
        Document       = ' '.join(Document)
        Document       = Document.lower()
        Document       = Document.translate(str.maketrans('', '', string.punctuation)) #Strips punctuation
        Document       = Document.split()
    
        #The following snippet uses the counter argument to create a "Counter" type. The most_common() argument makes this into a list. 
        Doc_Stats = (collections.Counter(Document)).most_common()
    
        #Get the total number of words in the "tabl" variable.
        Word_Count = 0
        for j in range (0, len(Doc_Stats)):
            Word_Count += Doc_Stats[j][1]
        
        #Divide the Doc_stats number by the relative % word-count, and turn the corresponding data into a dictionary 
        temp_dict = { (Doc_Stats[i][0]) : (100*(Doc_Stats[i][1]/Word_Count)) for i in range(0, len(Doc_Stats)) }  
        
        #Add the dictionary to t
        dfList.append(temp_dict)                                                                
    
    #Turn the list of dictionaries into a Dataframe
    Combined_DF = pd.DataFrame(dfList) 
    
    #Use the "Data_Prep" function to extract a list of corpus names, then set the Dataframe row names to the Corpus_List Names              
    Corpus_List = Data_Prep(data, full=False)
    Combined_DF.insert(0, 'Index:', Corpus_List) 
    Combined_DF = Combined_DF.set_index('Index:')

    #Split the Corpus list. Each line becomes a tuple of the style (AUTHOR - Genre - Text Name)
    for i in range(0, len(Corpus_List)):
        Corpus_List[i] = Corpus_List[i].split('_')
    
    #Split the tuples into 3 separate lists
    Author_List, Genre_List, Text_List = [], [], []
    for i in range(0, len(Corpus_List)):
        Author_List.append(Corpus_List[i][0])
        Genre_List.append(Corpus_List[i][1])
        Text_List.append(Corpus_List[i][2:])
    
    #Merge the 'Text List', as it may contain multiple tuples (Each word from the title will be its own entry in the tuple)
    for i in range (0, len(Text_List)):
        Text_List[i] = ' '.join(Text_List[i])

    #Add the 3 lists, created above, into the dataframe    
    Combined_DF.insert(0, 'Text Name:', Text_List)
    Combined_DF.insert(0, 'Genre:', Genre_List)
    Combined_DF.insert(0, 'Author:', Author_List)
    
    #Set all "NAs" to 0
    Combined_DF = Combined_DF.fillna(0)
    
    #Below Line Culls based off of the percentage given in argument; default to 50 
    Combined_DF = Combined_DF.drop(columns=Combined_DF.columns[((Combined_DF==0).mean()>(culling/100))],axis=1)

    DFM = Combined_DF.iloc[0:(len(Combined_DF.index)), 0:(nMFW+3)] 

    test = DFM[DFM['Author:']=='ANON']
    test = test.drop(columns = ['Author:', 'Genre:', 'Text Name:'])
    candidates = list(test.index)

    train = DFM[DFM['Author:']!='ANON']
    train = train.drop(columns = ['Author:', 'Genre:', 'Text Name:'])
    
    #Now we identify a Class column which the classifier will use to organize the data; a vector of values for the classes that are already known.
    class_f = DFM[DFM['Author:']!='ANON']
    class_f = class_f['Author:']
    
    
    indexes, texts, classifiers = [], [], []
    
    if (Kernels == 'all'):
        Kernel = ['rbf', 'linear', 'poly', 'sigmoid']
        for i in range (0, len (Kernel)):
            clf = svm.SVC(kernel=Kernel[i]) 
            clf.fit(train, class_f) #Train the model using the training sets
            prediction = clf.predict(test)
            
            for j in range (0, len(prediction)):
                indexes.append(Kernel[i])
                texts.append(candidates[j])            
                classifiers.append((str(prediction[j])))
                   
    else:
        clf = svm.SVC(kernel=Kernels) 
        clf.fit(train, class_f) #Train the model using the training sets
        prediction = clf.predict(test)
        
        for j in range (0, len(prediction)):
            indexes.append(Kernels)
            texts.append(candidates[j])            
            classifiers.append((str(prediction[j])))
    
    # Housman3 01_02 Additions to improve output
    
    ANON_Texts = []
    ANON_True_Author = []
    for entry in texts:
        
        #Search for brackets in the entry of each classification output. If there are brackets, take their contents 
        # - and place them in "ANON_True_Author", else append a zero to that list.
        if "(" in entry:
            x = entry[entry.find("(")+1:entry.find(")")]
            ANON_True_Author.append(x)
            
            #This removes the brackets & Their contents from the ANON classification entry (and .txt artifacts), 
            #- and appends the results to "ANON_Texts"
            
            x = entry
            x = re.sub("[\(\[].*?[\)\]]", "", x)
            if '.txt' in x:
                x = x.replace('.txt', "")
            ANON_Texts.append(x)
            
            
        else:
            ANON_True_Author.append(0)
            ANON_Texts.append(entry)
    
    #Checks to see if the Anon author mentioned in brackets is equal to the classification result. If they are, append 1, else append 0.
    Successful = []
    for i in range (0, len(ANON_True_Author)):
        if ANON_True_Author[i] == classifiers[i]:
            Successful.append(1)
        else:
            Successful.append(0)
    
    #Create a list of every non-anonymous author from earlier "Author_List"
    #Add all of them to training_set list, then sort it (so chunks are all grouped together), and then turn it into a string
    training_set = []
    for i in range (0, len(Author_List)):
        if Author_List[i] != 'ANON':
            training_set.append(Author_List[i] + " " + Text_List[i])
    training_set = sorted(training_set)
    training_set = '\n'.join(training_set)
    
    training_output = []
    
    stats = []
    stat = "MFW: " + str(nMFW) + " \n" + "Culling: " + str(culling) + " \n" + "Kernels: " + Kernels + " \n" + "Chunks: " + str(chunks)
 
    for i in range (0, len(classifiers)):
        training_output.append(training_set)
        stats.append(stat)

    
    results = pd.DataFrame(data = [indexes, stats, training_output, ANON_Texts, ANON_True_Author, classifiers, Successful]).transpose()
    results.columns = ['Kernel', 'Stats', 'Training Data', 'ANON Text', 'True Author', 'Classification', 'Success']
            
    
    
    
        
        
    #Old results method. Saved here because it's what worked for "Summary" function that is currently broken.         
   # results = pd.DataFrame(data = [indexes, texts, classifiers]).transpose()
   # results.columns = ['Kernel', 'Text', 'Classification']
    

    #CURRENTLY SUMMARY IS  BROKEN DUE TO CHANGES MADE IN HOUSMAN3 01_02
    if summary == True:
        summary_results = temp_summary(candidates, chunks, results)
        summary_results = pd.DataFrame(summary_results)
        return(summary_results)
    else:
        return(results)
    
def Data_Prep (data, full=False):
    from os import listdir
    Corpus_List = listdir(data)
        
    for item in Corpus_List:
        if item.endswith(".txt") == False:
            Corpus_List.remove(item)
          
    if full == True:
        for i in range (0, len(Corpus_List)):
            Corpus_List[i] = data + '/' + Corpus_List[i]
        return(Corpus_List)
    else: return (Corpus_List)

def splitter(inp, n=2):    
    from math import floor; import os; import shutil
    
    x = Data_Prep(inp, full = True) 
    y = Data_Prep(inp, full = False) #Y is used within the 'try' bit for creating the export file path

    out_path = inp + '/Chunks/'
    
    
    if os.path.exists(out_path) == True:
        shutil.rmtree(out_path)
        os.makedirs(out_path)
    else: 
         os.makedirs(out_path)

    for j in range (0, len(x)):
        text = open(x[j]).read()    
        step = len(text)/n 
        i = 0
        while i < n:
                try: 
                    output = open(out_path + y[j] + '_' + str(i) + '.txt', 'w')
                    output.write( text [floor((step*i)) : floor((step*(i+1))) ])
                    
                    i += 1
                except:
                    print("Error in chunking! At " + str(y[j]))
                    i += 1
                    continue  
                

    return(out_path)

def temp_summary(candidates, chunks, results):
    temp_list = []
    for i in range (0, len(candidates), chunks):
        text = candidates[i]
        text = text.split('.txt')
        text = text[0]
        temp_DFM = results[results['Text'].str.contains(text)]
        temp_result = temp_DFM.Classification.mode()
        if len(temp_result) == 1:
            temp_result = temp_result[0]
            
        temp_list.append((text, temp_result))

    return(temp_list)
     
def Genre_Prep(data):
    import pandas as pd; import itertools;  
    #data = '/Users/nate/Desktop/16 Nov Test/Minor Corpus'             TROUBLESHOOTING LINE
    
    #Data_prep the list, then create a dataframe in the format of [author | text],  so that we can get a 'unique' value. i.e. the number of unique authors
    short = Data_Prep(data, full = False)
    
    anon_plays = []
    anon_plays[:] = (value for value in short if value[0:4] == 'ANON')
    short[:] = (value for value in short if value[0:4] != 'ANON')
            
    for i in range (0, len(short)):
        short[i] = short[i].split('_', maxsplit = 1)
        
    short_df = pd.DataFrame(short)
    unique = short_df[0].unique()
    
    #Nested for-loops which add every [author | text] combo from the *same author* into the "holder" list, then appends it to "Author_set" and clears the holder variable
    #...This creates a list of lists, which each holds every text from an individual author 
    author_set = []
    for i in range (0, len(unique)):
        holder = []
        for j in range (0, len(short)):
            if short[j][0] == unique[i]:
                holder.append(short[j])
        author_set.append(holder)
    
    #Go through the filled "author_set" variable, and re-join the [author | text] entries into author_text format, for easier processing
    for i in range (0, len(author_set)):
        for j in range (0, len(author_set[i])):
            author_set[i][j] = '_'.join(author_set[i][j])
    
    #Create every possible permutation, using a single text from each author
    author_set = list(itertools.product(*author_set))
    author_set = [list(elem) for elem in author_set] 
    
    for i in range (0, len(author_set)):
        for j in range (0, len(anon_plays)):
            author_set[i].append(anon_plays[j])

    return(author_set)

#Feed in a single list from author_set, plus the path, and then use the returned path as a housman call
def Data_Assess(segment, path):
    import os; import shutil
    
    temp_folder = path + '/Data_Assessment/'
    
    if os.path.exists(temp_folder) == True:
        shutil.rmtree(temp_folder)
        os.makedirs(temp_folder)
    else: 
         os.makedirs(temp_folder)
    
    for i in range (0, len(segment)):
        
        text = open(data + '/' + segment[i]).read()
        output = open(temp_folder + segment[i] + '.txt', 'w')
        output.write(text)
    return(temp_folder)
        
    

    
  
Housman.__doc__ = ("""Optional arguments nMFW (default 1000), and culling (default 0)
                     Defaults to all kernels - optional arguments 'rbf', 'linear', 'poly', 'sigmoid' 
                     Defaults to no chunking. If Chunks > 1, will create 'chunks' folder in data set, and classify from chunks""")
#Below commented section works to iterate across overall data set, taking one text from each author
#Works for every variable - culling, kernels, summary, chunks, etc
'''
data = '/Users/nate/Documents/Academia/PhD Search/Test Corpus'       
author_set = Genre_Prep(data)

big_boy_list = []
for i in range(0, len(author_set), 5):
    print(Housman(data = Data_Assess(author_set[i], data), summary = True))
    big_boy_list.append((author_set[i], Housman(data = Data_Assess(author_set[i], data), summary = True)))

import pandas as pd
export_ready = pd.DataFrame(big_boy_list)

'''
