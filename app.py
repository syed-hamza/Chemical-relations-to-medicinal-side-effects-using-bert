from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import json
import random
app = Flask(__name__)
csv_data = pd.read_csv("filtered_data.csv")
csv_data = csv_data.replace([np.nan], -1)
sideffect_data = {}
with open('sideeffect_dict.json','r') as f:
    sideffect_data = json.load(f)
idf_dict = {}
with open('idf_score.json','r') as f:
    idf_dict = json.load(f)
data = ''
n = 20
for row in range(n):
    random_row = random.randint(0, len(csv_data)-1)
    data += f'''<a href="medicines?id={random_row}"><div class="max-w-md bg-gray-100 border border-gray-600 rounded-lg shadow-lg p-8 custom-container mx-4 my-4">
        <h1 class="text-xl font-bold mb-4">{csv_data["name"][random_row]}</h1>
        <p class="text-sm text-gray-700 mb-2">Use: {csv_data["use0"][random_row]} </p>
        <p class="text-sm text-gray-700 mb-2 flex">Description: {csv_data["descriptions"][row]} </p>
    </div></a>'''

@app.route('/')
def home():
    return render_template('home.html', data=data)
@app.route('/test')
def test():
    return render_template('test.html')

def content(csv):
    return f''' <p class="text-2xl justify-center text-gray-700 mb-8"> {csv["name"]}</p>
                <p class="text-lg text-gray-700 mb-8">Side-effects: {csv["sideEffects"]}</p>
                <p class="text-lg text-gray-700 mb-8">use {csv["uses"]}</p>
                <p class="text-lg text-gray-700 mb-8">Description: {csv["descriptions"]}</p>'''

def substitute(name):
    return f'''<div class="custom-container2 info-card flex-1 mr-4 border rounded-lg shadow-md">
      <h2 class="text-xl font-semibold mb-2">{name}</h2>
    </div>'''

def highlight(text,sideeffect,score):
    return f'''<span class="hover:bg-blue-300 tooltip text-blue-200" data-tooltip="{sideeffect}:{score}">{text}</span>'''


@app.route('/medicines')
def med():
    id = int(request.args.get('id'))
    maindata = ''
    dictdata = {}
    sideeffect = ''
    uses = ''
    for col in csv_data.columns:
        if(csv_data[col][id] != -1 and "substitute" not in col):
            if("sideEffect" in col):
                sideeffect+=csv_data[col][id]+", "
            if("uses" in col):
                uses+=csv_data[col][id]+", "
            else:
                dictdata[col] = csv_data[col][id]
    if sideeffect=='':
        sideeffect = "Not defined"
    if uses == '':
        uses = "Not defined"
    dictdata["sideEffects"] = sideeffect
    dictdata["uses"] = uses
    #highlighting
    temp = dictdata["descriptions"].split()
    final = ''
    for word in temp:
        word = word.lower()
        if(word[-1]=="." or word[-1]==","):
            word = word[:-1]
        if(word in sideffect_data.keys()):
            final += highlight(word,sideffect_data[word],idf_dict[word]) +" "
        else:
            final += word +" "
    dictdata["descriptions"] = final

    maindata += content(dictdata)
    #substitute part
    sub = ''
    sub_cols = [i for i in csv_data.columns if 'substitute' in i]
    for col in sub_cols:
        sub += substitute(csv_data[col][id])
    return render_template('medicines.html',maindata=maindata, sub = sub)

if __name__ == '__main__':
    app.run(debug=True)
