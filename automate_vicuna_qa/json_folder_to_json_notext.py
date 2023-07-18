# 2) run this file to convert all json files in answer folder to a list of json format to feed into vicuna. answer will be saved as myfile

import os
from dynamic_convert_short_res import convert_ans_to_finetune_form

file1 = open('myfile.jsonl', 'w')

# assign directory
directory = "converted_vicuna_answers"
collated_converted_ans = []
# iterate over files in
# that directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        print(f)
        dir_len = len(directory)
        collated_converted_ans.extend(convert_ans_to_finetune_form(f))


for line in collated_converted_ans:
    file1.write(line + '\n')

file1.close()


