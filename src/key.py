import json
import extract
import numpy as np
import scipy.stats
import sys
sys.path.append('/Users/yiminglin/Documents/Codebase/Pdf_reverse/')
from model import model 
import networkx as nx
model_name = 'gpt4o'

def get_relative_locations(path):
    line_number = 0
    phrases = {}
    with open(path, 'r') as file:
        # Iterate over each line in the file
        for line in file:
            phrase = line.strip()
            if(phrase not in phrases):
                phrases[phrase] = [line_number]
            else:
                phrases[phrase].append(line_number)
            line_number += 1
    return phrases
            
def write_dict(path, d):
    with open(path, 'w') as json_file:
        json.dump(d, json_file)

def read_dict(file):
    #print(file)
    with open(file, 'r') as file:
        data = json.load(file)
    return data 


def get_extracted_path(path):
    path = path.replace('raw','extracted')
    path = path.replace('.pdf','.txt')
    return path

def get_relative_location_path(extracted_path):
    path = extracted_path[:-4] + '_relative_location.csv'
    return path

def perfect_match(v1,v2,k):
    if(len(v1)!=len(v2)):
        return 0
    delta = abs(v1[0] - v2[0])
    for i in range(len(v1)):
        if(abs(v1[i]-v2[i])-delta > k):
            #print(delta, v1[i],v2[i])
            return 0
    return 1
    
def is_subsequence(seq1, seq2, k):#len(seq1) < len(seq2)
    i = 0
    j = 0 
    matched_count = 0
    while(True):
        if(abs(seq1[i] - seq2[j]) <= k):
            matched_count += 1
            i += 1
            j += 1
        else:
            j += 1
        if(i == len(seq1) or j == len(seq2)):
            break
    if(matched_count < len(seq1)):
        return 0
    return 1


def partial_perfect_match(v1,v2,k):#len(v1) < len(v2)
    delta = abs(v1[0] - v2[0])
    new_v1 = []
    if(v1[0] < v2[0]):
        for v in v1:
            new_v1.append(v + delta)
    else:
        for v in v1:
            new_v1.append(v - delta)
    if(is_subsequence(new_v1,v2,k)):
        return 1
    return 0

def perfect_align_clustering(phrases_vec,k):
    mp = {}
    remap = {}
    id = 0
    phrases = []
    for phrase, vec in phrases_vec.items():
        if(len(vec) > 1):#phrase appearing only one time is trievally perfectly align with any other one-time phrase and discard them 
            phrases.append(phrase)

    for i in range(len(phrases)):
        pi = phrases[i]
        vi = phrases_vec[pi]
        if(pi not in mp):
            mp[pi] = id
            remap[id] = [pi]
            id += 1
        else:
            continue
        for j in range(i+1, len(phrases)):
            pj = phrases[j]
            vj = phrases_vec[pj]

            #optimization: pj in mp denotes that pj must be at least perfectly match with one phrase before pi, but pi is not in mp
            #so pi and pj must be not perfectly aligned, and thus skip comparison 
            if(pj in mp):
                continue

            if(perfect_match(vi,vj,k) == 1):
                mp[pj] = id-1
                remap[id-1].append(pj)
    
    return mp, remap

def result_gen_from_response(response, s):
    lst = []
    if('|' not in response and 'no' in response.lower()):
        for i in range(s):
            lst.append(0)
        return lst
    l = response.split('|')
    for i in range(len(l)+1):
        lst.append(1)
    for i in range(s - (len(l) + 1)):
        lst.append(0)
    return lst

def candidate_key_clusters_selection(clusters):
    #clusters: cid -> [list of phrases]
    instruction = 'The following list contains possibly keys and values extracted from a table. Return to me all the keys without explanation, and seperate each key by |. If no key is found, return NO.' 
    mp = {}
    cids = []
    for cid, l in clusters.items():
        if(len(l) == 1):
            continue
        context = ", ".join(l)
        prompt = (instruction,context)
        response = model(model_name,prompt)
        print(response)
        lst = result_gen_from_response(response, len(l))
        print(lst)
        p, w = mean_confidence_interval(lst)
        print(p,w)
        mp[cid] = (p,w)
        cids.append(cid)

    #topology order to select maximal key set 
    out_degree = {}
    for i in range(len(cids)):
        ci = cids[i]
        for j in range(i+1, len(cids)):
            cj = cids[j]
            if(mp[ci][0] > mp[cj][0] and mp[ci][1] < mp[cj][1]):
                #ci dominates cj, add edge from cj to ci
                if(cj not in out_degree):
                    out_degree[cj] = 1
            elif(mp[ci][0] < mp[cj][0] and mp[ci][1] > mp[cj][1]):
                #cj dominates ci, add edge from ci to cj
                if(ci not in out_degree):
                    out_degree[ci] = 1
    candidate_key_clusters = []
    for cid in cids:
        if(cid not in out_degree):
            candidate_key_clusters.append(cid)
    print(candidate_key_clusters)
    return candidate_key_clusters 

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, h

def cluster_partial_match(c1,c2,phrases_vec,k):
    # print(c1)
    # print(c2)
    l1 = len(phrases_vec[c1[0]])
    l2 = len(phrases_vec[c2[0]])
    #print(l1,l2)
    nc1 = []
    nc2 = []
    if(l1 < l2):
        nc1 = c1
        nc2 = c2
    else:
        nc1 = c2
        nc2 = c1
    for i in range(len(nc1)):
        for j in range(i+1, len(nc2)):
            if(partial_perfect_match(phrases_vec[nc1[i]],phrases_vec[nc2[j]],k) == 1):
                print(nc1[i],phrases_vec[nc1[i]])
                print(nc2[j],phrases_vec[nc2[j]])
                print('')
                return 1
    return 0
        

def clustering_group(phrases_vec, clusters, k=1):
    G = nx.DiGraph()

    # Add edges
    nodes = []
    edges = []
    for n, v in clusters.items():
        nodes.append(n)

    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            #print(nodes[i], nodes[j])
            if(cluster_partial_match(clusters[nodes[i]], clusters[nodes[j]], phrases_vec, k) == 1):
                edges.append((nodes[i], nodes[j]))
            #break
        #break

    G.add_edges_from(edges)

    # Find weakly connected components
    wcc = list(nx.weakly_connected_components(G))

    # Print the weakly connected components
    # print("Weakly Connected Components:")
    for component in wcc:
        print(list(component))
    

if __name__ == "__main__":
    root_path = extract.get_root_path()
    tested_paths = []
    tested_paths.append(root_path + '/data/raw/complaints & use of force/Champaign IL Police Complaints/Investigations_Redacted.pdf')
    tested_paths.append(root_path + '/data/raw/complaints & use of force/UIUC PD Use of Force/22-274.releasable.pdf')
    tested_paths.append(root_path + '/data/raw/certification/CT/DecertifiedOfficersRev_9622 Emilie Munson.pdf')
    tested_paths.append(root_path + '/data/raw/certification/IA/Active_Employment.pdf')
    tested_paths.append(root_path + '/data/raw/certification/MT/RptEmpRstrDetail Active.pdf')
    tested_paths.append(root_path + '/data/raw/certification/VT/Invisible Institue Report.pdf')

    id = 0
    tested_id = 2 #starting from 1
    k=1

    for path in tested_paths:
        id += 1
        if(id != tested_id):
            continue
        #print(path)
        extracted_path = get_extracted_path(path)
        #print(extracted_path)
        phrases = get_relative_locations(extracted_path)
        out_path = get_relative_location_path(extracted_path)
        phrases = read_dict(out_path)
        mp, remap = perfect_align_clustering(phrases,k)
        #clustering_group(phrases, remap, k)
        candidate_key_clusters_selection(remap)
        