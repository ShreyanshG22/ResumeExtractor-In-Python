import os
import textract
from heapq import nlargest
from Tkinter import *
import tkFileDialog
import json
import sys
from collections import Counter
import nltk
from Queue import Queue
import threading
import string
import math
import subprocess

printable = set(string.printable)
def search(document):
	final_count = 0.0
	kl = document.strip().split(" ",1)
	disco = json.loads(kl[1])
	for i in string:
		if '*' in i:
			i = i.strip(" ").split("*")
			final_count += disco.get(i[0], 1.0)*(po - math.log10(docrel.get(i[0])))*int(i[1])
		else:
			final_count += disco.get(i, 1.0)*(po - math.log10(docrel.get(i)))
	with print_lock:	
		dc[kl[0]] = final_count


def threader():
	while True:
		document = q.get()
		search(document)
		q.task_done()

def loadtemplate():
	global direc 
	direc = tkFileDialog.askdirectory()
	if not os.path.exists(direc+'/WorkOnThis.txt') or not os.path.exists(direc+'/Dictionary.txt'):
		T.insert(INSERT, "Creating Database....\nThis is only initial process....\nWon't take time now onwards...\n.\n..\n...\n....\n.....\n....\n...\n..\n.\n")
		dictio = {}
		root_dir = direc+"/USRESUMES"
		l = 0
		with open(direc+"/WorkOnThis.txt","w") as fw:
			for root, dirs, files in os.walk(root_dir, onerror=None):
			    for filename in files:
			    	try:
					doc = os.path.join(root, filename)
					print(doc)
					document = textract.process(doc)
					document = filter(lambda x: x in printable, document)
					sentences = nltk.sent_tokenize(document.lower())
					nouns = []
					for sentence in sentences:
						for word,pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
							if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS' or pos == 'CD'):
								nouns.append(word)
					document = " ".join(nouns)
					sentences = nltk.word_tokenize(document.lower())
					count = Counter(sentences)
					docum = {}
					for k, v in count.items():
						calc = 1 + math.log10(v)
						if calc > 1.0:
							docum[str(k)] = calc
					fw.write(json.dumps(docum))
					fw.write("\n")
					l = l + 1
					dictio[str(l)] = doc
				except:
					continue
		with open(direc+"/Dictionary.txt", "w") as ff:
			ff.write(str(l)+"\n")
			ff.write(json.dumps(dictio))
		T.insert(INSERT, "Database Created....\n")

def callc():
	T.delete(1.0,END)

def reldoc(string, result_queue):
	tagcount = 0
	with open(direc+"/WorkOnThis.txt","r") as fp:
		for document in fp:
			if string in document:
				tagcount = tagcount + 1
	result_queue.put(string+":"+str(tagcount))

def threader2():
	while True:
		string = q2.get()
		reldoc(string, result_queue)
		q2.task_done()


def callback():
	T.delete(1.0,END)
	T.insert(INSERT, "Waiting for result....\n")
	global string
	string = e1.get()
	string = string.lower().split("/")
	T.insert(INSERT, direc+"\n\n")
	global po
	with open(direc+"/Dictionary.txt", "r") as fr:
		po, dictio = fr.readlines()
	po = int(po)
	po = math.log10(po)
	dic = json.loads(dictio)
	global dc
	dc = {}
	
	global result_queue
	result_queue = Queue()
	global q2
	q2 = Queue()
	for i in string:
		q2.put(i)
	global docrel 
	docrel = {}
	for _ in range(5):
		t = threading.Thread(target=threader2) 
		t.daemon = True
		t.start()
	q2.join()
	while not result_queue.empty():
		i = result_queue.get().split(":")
		docrel[i[0]] = int(i[1])
	print(docrel)
   
	global print_lock
	print_lock = threading.Lock()
	global q
	q = Queue()
	with open(direc+"/WorkOnThis.txt","r") as fp:
		k = 0
		for document in fp:
			k = k + 1
			q.put(str(k)+" "+document)
	threads = []
	for _ in range(30):
		t = threading.Thread(target=threader) 
		t.daemon = True
		t.start()
	q.join()
	
	print(po)
	top = nlargest(10, dc, key=dc.get)
	for j in range(len(top)):
		T.insert(INSERT, str(j+1)+")  "+dic.get(top[j])+"\n")
		'''if sys.platform == 'linux2':
			subprocess.call(["xdg-open", dic.get(top[j])])
		else:
			os.startfile(dic.get(top[j]))'''	
	T.insert(INSERT,"\n\n\n")

root = Tk()
root.title("Search Engine")
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))
toolbar = Frame(root, bd=8)
Button(toolbar, text = "Browse", command = loadtemplate, width = 10).pack(side=LEFT, padx=2, pady=2)
label = Label(toolbar, text='Search String')
label.pack(side = LEFT)
e1 = Entry(toolbar, bd=3) 
e1.pack(side=LEFT)
b = Button(toolbar, text="Search", width=6, command=callback)
b.pack(side=LEFT, padx=2, pady=2)
c = Button(toolbar, text="Clear", width=6, command=callc)
c.pack(side=LEFT, padx=2, pady=2)
toolbar.pack(side=TOP, fill=X)

screen = Frame(root, bd=8)
T = Text(screen, height=350, width=500)
scr = Scrollbar(screen, orient=VERTICAL, command=T.yview)
scr.pack(side=RIGHT,fill=Y)
T.config(yscrollcommand=scr.set, font=('Arial', 12))
T.pack(padx=3, pady=3)
T.insert(END, "")
screen.pack(side=BOTTOM, fill=BOTH)
mainloop()
