# get_actor_concept_matrix function
import pandas as pd
import numpy as np
from util import abbreviations
from statistics import mean
from util import norm

import warnings
warnings.filterwarnings('ignore')


def get_actor_concept_matrix(df, actor_col='actor', concept_col='concept', agreement_col='agreement', abb=True, min_degree=1):
    
    """
    Expecting Agreement to be coded: 1 = agreement, 0 = disagreement.
    Degree Threshold (min_degree) is applied to both actors and concepts.
    ------------------------------------------------------------------------
    Returns actor-concept-matrix with following values:
    1 = agreement
    -1 = disagreement
    0 = no statement
    """
    
    # subset and rename for readability
    df = df[[actor_col, concept_col, agreement_col]]
    df.columns = ['Actor', 'Concept', 'Agreement']
    
    # filter with min_degree
    df = df[df.groupby('Actor').Concept.transform(len) >= min_degree]
    df = df[df.groupby('Concept').Actor.transform(len) >= min_degree]
    
    # recode agreement
    df.Agreement = df.Agreement.apply(lambda x: -1 if x == 0 else 1)
    
    # optional use of abbreviations
    if abb == True:
        df.Actor = abbreviations(df.Actor)
        df.Concept = abbreviations(df.Concept)
        
    # pivot dataframe and aggregate with mean
    df = df.pivot_table(index='Actor', columns='Concept', values='Agreement', aggfunc='mean')
    
    # recode agreement
    def recode(x):
        if x > 0:
            return 1
        if x < 0:
            return -1
        else:
            return 0
        
    df = df.applymap(recode)
    
    return df


def get_affiliation_dataframe(df, 
                            actor_col='actor', 
                            concept_col='concept', 
                            agreement_col='agreement', 
                            abb=True, 
                            min_degree=0):
    
    # subset and rename columns for generalizability
    df = df[[actor_col, concept_col, agreement_col]]
    df.columns = ['actor', 'concept', 'agreement']
    
    # use abbreviations
    if abb == True:
        df['actor'] = abbreviations(df['actor'])
        df['concept'] = abbreviations(df['concept'])
    
    # filter min_deg
    df = df.groupby('actor').filter(lambda x: len(x) >= min_degree) 
    df = df.groupby('concept').filter(lambda x: len(x) >= min_degree)
    
    # get average agreement and weight
    df = df.groupby(['actor', 'concept']).agg({'agreement':(lambda x: list(x))}).reset_index()
    df['weight'] = df.agreement.apply(lambda x: len(x))
    df['agreement'] = df.agreement.apply(lambda x: round(mean(x), 2))
    
    return df


def get_network_dataframe(df, type_='actor congruence', normalize=True):
    """ 
    df: actor-concept-matrix dataframe
    type_: desired network type output (see below)
    norm: boolean if normalization (divide by max) should be applied
    --------------------------------------------------------
    Returns edge lists for three one-mode networks:
    - congruence
    - conflict
    - subtract
    """
    # define type and raise error if wrong
    type_ = type_.split()
    if (type_[0] not in ['actor', 'concept']) | (type_[1] not in ['congruence', 'conflict', 'subtract']):
        raise TypeError('Wrong network type. Type must be "actor"/"concept" + whitespace + "congruence"/"conflict"/"subtract".')
    
    # transpose matrix for concept networks
    if type_[0] == 'concept':
        df = df.T
 
    # iterate over actors/concepts   
    i = 0    
    row_list= []
    for id1, row1 in df.iterrows():
        i += 1
        weight = 0
        a = np.array(row1)
        
        for id2, row2 in df.iloc[i:].iterrows():         
            b = np.array(row2)  
            c = a * b
            
            # network type
            if type_[1] == 'congruence': 
                weight = (c == 1).sum()
            
            if type_[1] == 'conflict':               
                weight = (c == -1).sum()
                
            if type_[1] == 'subtract':
                weight = c.sum()
            
            # only include connections with weight
            if weight != 0:
                if type_[0] == 'actor':
                    row_list.append({'actor1': id1, 'actor2': id2, 'weight': weight})
                else:
                    row_list.append({'concept1': id1, 'concept2': id2, 'weight': weight})
                
    # construct df
    df = pd.DataFrame(row_list)
    
    # normalize weights   
    if normalize == True:
        abs_weights = [abs(x) for x in df.weight]
        df.weight = [x/max(abs_weights) for x in df.weight]
    
    return df