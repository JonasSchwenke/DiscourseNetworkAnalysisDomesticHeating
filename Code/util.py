# utility functions

def colors():
    print('Fraunhofer Green: #149C7E')
    print('Yellow: #ffcc00')
    print('Blue: #538cc6')
    print('Red: #ff3b6f')

    
def printText(text):
    from IPython.display import Markdown, display
    display(Markdown(text))


def news_preprocess(text):
    import re
    
    def camel_case_split(identifier):
        """
        Source: https://stackoverflow.com/questions/29916065/how-to-do-camelcase-split-in-python
        """
        matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return [m.group(0) for m in matches]
    
    # replace faulty punctuation
    finds = re.findall("[A-ZÖÄÜßa-zöäüß0-9]{2,}\.[A-z]{2,}", text)
    for find in finds:
        text = text.replace(find, find.replace(".", ". "))
        
    text = text.replace('."', '." ')
    text = text.replace('".', '". ')
    
    
    # split camelCase words
    camel_split_tokens = []
    
    dont_split = ['GmbH', '(EnEG)', '(EnEV)', '(EnGV)', 'EEWärmeG', '(EEWärmeG)', 'KfW', '(KfW)', 'KfW-Bank', 'kWh', 
                  '(ZeBio)', 'ErP', 'EnergieAgentur', '(BfEE)', 'BfEE-Leiter' , 'enviaM', 'EnBW', 'AfD', 'GroKo', 'AKWs',
                  '(IfW)', 'EnBW', '(TWh)', 'LfA', 'LEDs', '(EnEV 2014)', '(BMWi)', 'KfW-Förderung', 'KfW-Programm',
                  'GdW', 'IfW-Präsident']

    for token in text.split():
     
        if (len(token) > 4) & (token not in dont_split):
            split = camel_case_split(token)
            if len(split) == 2:
                camel_split_tokens.append(split[0]+'.')
                camel_split_tokens.append(split[1])
            else:
                for t in split:
                    camel_split_tokens.append(t)
        else:
            camel_split_tokens.append(token)

        camel_split_text = ' '.join(camel_split_tokens).lstrip(' ')
    
    return camel_split_text
    

def abbreviations(l):
    import re
    """
    Returns list of abbreviations if found in parantheses of string
    """
    out = []
    for i in l:
        m = re.search(r"\((.*?)\)", i)
        if m == None: 
            out.append(i)
        else: 
            out.append(m.group(1))
    return out
    
    
def abs2rel(df, round_=2):
    df = df.T
    for c in df.columns:
        df[c] = round((df[c]/df[c].sum())*100, round_)
    return df.T
    
    
# normalize to any range function
def norm(a,b,l):
    out = []
    for x in l:
        norm_x = (b-a)*((x-min(l))/(max(l)-min(l)))+a
        out.append(norm_x)
    return out    