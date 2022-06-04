#!C:\Users\Moi4\Desktop\code\procpo\haikus\venv\Scripts\python.exe
import numpy as np
import io
import re
import xml.dom as dom
import json
import translators as ts
import os
def get_word_types(words):
	wordtypes = set(y if "," in x[2] else x[2] for x in words for y in (x[2].split(",")))
	return wordtypes

def load_edict():
	blob = io.open('edict_sub', 'r',encoding="EUC-JP").read()
	words=re.findall(r"(.*?)\[(.*?)\]\s+\/\((.*?)\)",blob,flags=re.M)
	wordtypes=get_word_types(words)
	maxcharcount = max(set(len(w[1]) for w in words))
	
	edict = dict()
	
	for wt in wordtypes:
		edict[wt]={j:[] for j in range(1,maxcharcount+1)}
	for w in words:
		if "," in w[2]:
			for wt in w[2].split(","):
				 edict[wt][len(w[1])].append(w)
		else:
			edict[wt][len(w[1])].append(w)
	# ~ clean up
	wkeys=edict.keys()
	nkeys=list(range(1,maxcharcount+1))
	wkey_counts={wkey:0 for wkey in wkeys}
	total_counts=0
	for wkey in wkeys:
		for nkey in nkeys:
			if edict[wkey][nkey] == []:
				del edict[wkey][nkey]
			else:
				wkey_counts[wkey]+=len(edict[wkey][nkey])
				total_counts+=len(edict[wkey][nkey])
	wkey_dist=[w/total_counts for w in wkey_counts.values()]
	return edict,wkey_dist

def get_n_hiragana(n):
	hiragana_chart = list("ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖゝゞ")
	return "".join(np.random.choice(hiragana_chart,n))

def split_int(n,parts=3,maximum_length=4):
	l=[]
	for x in range(parts):
		if sum(l) == n:
			return l
		if sum(l) == n-1:
			l.append(1)
			return l
		
		l.append(np.random.randint(1,min(n-sum(l),maximum_length)))
	l.append(n-sum(l))
	return l

def nice_split_int(n):
	return split_int(n,parts=np.random.randint(2,5),maximum_length=np.random.randint(4,6))

def build_haiku(edict,wkey_dist=None,pick_types=None,doprint=True):
	haiku=[]
	furigana=[]
	wordtypes = list(edict.keys())
	pieds=[5,7,5]
	for pied in pieds:
		line=[]
		line_furi=[]
		syls = nice_split_int(pied)
		# ~ print("syls:",syls)
		for syl in syls:
			if pick_types is None:
				if wkey_dist is not None:
					wt=np.random.choice(wordtypes,p=wkey_dist)
				else:
					wt=np.random.choice(wordtypes)
			else:
				wt=np.random.choice(pick_types)
			while not syl in edict[wt].keys():
				wt=np.random.choice(wordtypes)
			word_selection = edict[wt][syl]
			# ~ print(word_selection)
			idx=list(range(len(word_selection)))
			# ~ print(idx)
			select_idx=np.random.choice(idx)
			line.append(word_selection[select_idx][0])
			line_furi.append(word_selection[select_idx][1])
		haiku.append(line)
		furigana.append(line_furi)
	if doprint:
		print("HAIKU:",flatten_haiku(haiku,sep_out="",sep_in=""))
	return haiku,furigana
			 
	
def translate_haiku(haiku,translator_choice):
	return translator_choice(haiku,from_language='ja', to_language='en')

def flatten_haiku(haiku_list,sep_out,sep_in):
	return re.sub(r"\s","",sep_out.join([sep_in.join(line) for line in haiku_list]))

def get_haiku_ja_en(translator_choice,N,sep_out="",sep_in="",pick_types=None):
	edict,wkey_dist=load_edict()
	if sep_out == "\n" or sep_in == "\n":
		raise ValueError("Don't even think about it")
	haiku_ja_list=[]
	furigana_list=[]
	for _ in range(N):
		haiku_ja,furigana=build_haiku(edict,wkey_dist,pick_types=pick_types)
		haiku_ja_list.append(haiku_ja)
		furigana_list.append(furigana)
	translate_sep="\n\n"
	haiku_ja_list_processed=translate_sep.join([flatten_haiku(haiku_ja,
											sep_out=sep_out,
											sep_in=sep_in) for haiku_ja in haiku_ja_list])
	print("PROCESSED:",haiku_ja_list_processed)
	haiku_en_list_str = translate_haiku(haiku_ja_list_processed,
									translator_choice=translator_choice)
	haiku_en_list=haiku_en_list_str.split(translate_sep)
	return haiku_ja_list,haiku_en_list,furigana_list

def add_node(content,balise,css_class=None):
	if css_class is not None:
		return "\n<{b} class=\"{css_class}\">\n{content}\n</{b}>\n".format(content=content,b=balise,css_class=css_class)
	return "\n<{b}>\n{content}\n</{b}>\n".format(content=content,b=balise)


def get_html_haiku(haiku_ja,furigana,haiku_en,sep_display=""):
	return add_node(balise="div",css_class="haiku-box",
			content=add_node(balise="div",css_class="haiku-ja-box",
			content=add_node(balise="p",
			content=furiganize_haiku(haiku_ja,furigana,sep_out=sep_display)))
			+add_node(balise="div",css_class="haiku-en-box",
			content=add_node(balise="p",
			content=haiku_en)))

def write_page(content,fn="haiku.html",title="translator authored haikus"):
	fn = io.open(fn,"w+",encoding="utf8")
	fn.write("""<head>
			<link rel="stylesheet" href="css/haikus_styles.css">
			<meta charset="UTF-8">
			<title>{title}</title>
			</head>\n""".format(title=title))
	page_content = add_node(balise="html",
						content=add_node(balise="body",
						content=add_node(balise="div",css_class="ur-box",
						content=content
						)))
	fn.write(page_content)
	fn.close()

def furiganize_haiku(haiku_ja,furigana,sep_out="",sep_in=""):
	haiku=[]
	for line,furi_line in zip(haiku_ja,furigana):
		haiku.append(sep_in.join([furiganize_kanji(kanji,furigano) for kanji,furigano in zip(line,furi_line)]))
	return sep_out.join(haiku)

def furiganize_kanji(kanji,furigana):
	if kanji != furigana:
		return "<ruby>{k}<rt>{f}</rt></ruby>".format(k=kanji,f=furigana)
	return "{k}".format(k=kanji)

def create_page(N=5,sep_display="<br>",sep_haiku="<br>",sep_trans="/ ",translator_choice=ts.google,batch_translate=True,pick_types=None):
	content=[]
	if batch_translate:
		haiku_ja_list,haiku_en_list,furigana_list=get_haiku_ja_en(sep_out=sep_trans,sep_in="",N=N,translator_choice=translator_choice,pick_types=pick_types)
		for haiku_ja,haiku_en,furigana in zip(haiku_ja_list,haiku_en_list,furigana_list):
			content.append(get_html_haiku(haiku_ja,furigana,haiku_en,sep_display=sep_display))
	else:
		for _ in range(N):
			haiku_ja_list,haiku_en_list,furigana_list=get_haiku_ja_en(sep_out=sep_trans,sep_in="",N=1,translator_choice=translator_choice)
			haiku_ja=haiku_ja_list[0]
			haiku_en=haiku_en_list[0]
			furigana=furigana_list[0]
			content.append(get_html_haiku(haiku_ja,furigana,haiku_en,sep_display=sep_display))
	write_page(content=sep_haiku.join(content),fn="haiku.html")
	
def print_N_haikus(N=5,pick_types=None):
	edict,wkey_dist=load_edict()
	for _ in range(N):
		build_haiku(edict,wkey_dist,pick_types=pick_types)


def get_haikus_ja(N=5,pick_types=None):
	edict,wkey_dist=load_edict()
	haiku_ja_list=[]
	furigana_list=[]
	for _ in range(N):
		haiku_ja,furigana=build_haiku(edict,wkey_dist,pick_types=pick_types)
		haiku_ja_list.append(haiku_ja)
		furigana_list.append(furigana)
	return haiku_ja_list,furigana_list

def create_json_for_translate(N=5,sep_trans="",pick_types=None,fn="haikus",folder="data"):
	haiku_ja_list,furigana_list=get_haikus_ja(N=N,pick_types=pick_types)
	j={}
	j_flat=[]
	for ind,val in enumerate(zip(haiku_ja_list,furigana_list)):
		h,f = val
		flat_haiku=flatten_haiku(h,sep_out=sep_trans,sep_in="")
		j[str(ind)]={"haiku_ja":h,"haiku_ja_flat":flat_haiku,"furigana":f,"haiku_en":""}
		j_flat.append(flat_haiku)
	
	f=io.open(os.path.join(folder,"{}_raw.json".format(fn)),"w+",encoding="utf8")
	f.write(json.dumps(j,indent=4,ensure_ascii=False))
	f.close()
	
	f=io.open(os.path.join(folder,"{}_ja_flat.txt".format(fn)),"w+",encoding="utf8")
	f.write("\n\n".join(j_flat))
	f.close()

def merge_translation_json(fn="haikus",folder="data"):
	f = io.open(os.path.join(folder,"{}_raw.json".format(fn)),"r",encoding="utf8")
	j=json.loads(f.read())
	f.close()
	haikus_en = io.open(os.path.join(folder,"{}_en_flat.txt".format(fn)),"r",encoding="utf8").read().split("\n\n")
	for k in j.keys():
		j[k]["haiku_en"]=haikus_en[int(k)]
	f = io.open(os.path.join(folder,"{}_translated.json".format(fn)),"w+",encoding="utf8")
	f.write(json.dumps(j,indent=4,ensure_ascii=False))
	f.close()

def create_page_from_json(fn="haikus",sep_display="<br>",sep_haiku="<br>",folder="data",page_fn="haiku.html"):
	f = io.open(os.path.join(folder,"{}_translated.json".format(fn)),"r",encoding="utf8")
	j=json.loads(f.read())
	f.close()
	content=[]
	for k in j.keys():
		haiku_ja=j[k]["haiku_ja"]
		furigana=j[k]["furigana"]
		haiku_en=j[k]["haiku_en"]
		content.append(get_html_haiku(haiku_ja,furigana,haiku_en,sep_display=sep_display))
	write_page(content=sep_haiku.join(content),fn=page_fn)

def main():
	# ~ pick_types=["cop","v5u","adj-na","adv"]
	
	# ~ create_page(N=70,translator_choice=ts.google,sep_trans="",batch_translate=True,pick_types=None)
	folder="data"
	fn="haikus_2"
	# ~ create_json_for_translate(N=100,fn=fn,folder=folder)
	# ~ merge_translation_json(fn=fn,folder=folder)
	create_page_from_json(fn=fn,folder=folder,page_fn="haikus_collection_b.html")
	disclaimer="These haikus make no sense in japanese, although they respect the superficial poetic form. It is the translator which infuses them with meaning, by earnestly trying to convey their content in english, in a valid and coherent fashion, although no coherent content is present in the first place. You might understand these as wholly english works inspired by complete misunderstanding and straightforward misdirection. Indeed, translation is art."


if __name__ == "__main__":
	main()