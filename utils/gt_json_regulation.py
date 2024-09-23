#this script translates the ground truth data into json format 
import pandas as pd
from io import StringIO
import json

def regulate_table(data):
    table_data = StringIO(data)
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(table_data)
    rows = []
    
    for index, row in df.iterrows():
        #print(index)
        row_object = {}
        for key,val in row.items():
            if(isinstance(key, str)):
                key = key.strip()
            if(isinstance(val, str)):
                val = val.strip()
            row_object[key] = val
            
        rows.append(row_object)
    return rows
        
def regulate_kv(data):
    kvs_content = []
    kv_pairs = data.split('\n')
    for kv in kv_pairs:
        kvs = kv.split(',', 1)
        key = kvs[0]
        if(len(kvs) > 1):
            val = kvs[1]
        else:
            val = ''
        object = {}
        if(isinstance(key, str)):
                key = key.strip()
        if(isinstance(val, str)):
            val = val.strip()
        object[key] = val
        kvs_content.append(object)
        #print(key,val)
    return kvs_content 

def regulate_template(path):
    # Open the file in read mode
    records = []
    with open(path, 'r') as file:
        # Read line by line
        
        rid = 0
        record = {}
        object = []
        block = {}
        type = ''
        content = ''

        for line in file:
            line = line.strip()
            if('#Record' in line):
                #add previous record into records 
                if(len(record) > 0 ):
                    record['content'] = object
                    records.append(record)
                #initialie a new record and setup the record id
                rid = int(line[-1])
                record = {}
                record['id'] = rid
                object = []
            else:
                if('-TABLE' in line):
                    #add the processed block into object
                    if(content != ''):
                        block['content'] = content
                        object.append(block)
                    #set up a new block
                    block = {}
                    block['type'] = 'table'
                    type = 'table'
                    content = ''
                elif('-KV' in line):
                    #add the processed block into object
                    if(content != ''):
                        block['content'] = content
                        object.append(block)
                    #set up a new block
                    block = {}
                    block['type'] = 'kv'
                    type = 'kv'
                    content = ''
                else:
                    #process a row of data 
                    if(type == 'table'):
                        content += line + '\n'
                    else:
                        content += line + '\n'
        
        #last line, add last block and last records
        if(content != ''):
            block['content'] = content
            object.append(block)
        record['content'] = object
        records.append(record)

    return records 

def regular_full(records):
    new_records = []
    for record in records:
        new_record = {}
        new_record['id'] = record['id']
        object = record['content']
        new_object = []
        for block in object:
            new_block = {}
            new_block['type'] = block['type']
            if(block['type'] == 'table'):
                content = regulate_table(block['content'])
            elif(block['type'] == 'kv'):
                content = regulate_kv(block['content'])
            new_block['content'] = content
            new_object.append(new_block)
        new_record['content'] = new_object
        new_records.append(new_record)
    return new_records
            
def write_json(out, path):
    with open(path, 'w') as json_file:
        json.dump(out, json_file, indent=4)

if __name__ == "__main__":
    in_path = '/Users/yiminglin/Documents/Codebase/Pdf_reverse/data/truths/key_value_truth/complaints & use of force/Champaign IL Police Complaints/investigations.txt'
    out_path = '/Users/yiminglin/Documents/Codebase/Pdf_reverse/data/truths/key_value_truth/complaints & use of force/Champaign IL Police Complaints/investigations.json'
    records = regulate_template(in_path)
    records = regular_full(records)
    write_json(records, out_path)
    


