import codecs
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
import shutil

def HTMLEntitiesToUnicode(text):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
    text = BeautifulSoup(text, "lxml").text
    return text

def print_content(element):
    """
    Recursively print the content of an element, including nested elements.
    """
    if element.text:
        print(element.text.strip())
    for child in element:
        print_content(child)
    if element.tail:
        print(element.tail.strip())
             

def clean(s):
    s = s.replace("\n"," ").replace("/","-").replace("|","-").replace("(","-").replace(")","-").replace('"'," ")
    s = s.replace(":"," ").replace(";"," ").replace(".","-").replace('\\',"-")
    s = s.replace("?"," ").replace("*"," ").replace(">"," ").replace("<"," ")
    return s
                 
def tag(s):
    s = s.replace(" ","_").replace(".","").replace(",","")
    return s

def createnotes():    
    fout = codecs.open("D:/AdvEng2018.txt", mode="w", encoding="utf-8")
    tree = ET.parse("D:/adveng 2018 (AE2018).xml")
    #tree = ET.parse("D:/AdvEng 2018 (all elements).xml")
    root = tree.getroot()
    c = 0
    count = 0
    currenttag = ""
    lastwas = True
    
    for entry in root.iter('SuperMemoElement'):
        seq = entry.find('./ID').text
        ord = entry.find('./Ordinal')
        ord = ord.text.zfill(5) if ord is not None else ""
        typ = entry.find('./Type').text
        if typ == "Topic":
            #print(entry.text)
            c += 1
            if lastwas is False:
                #currenttag = ""
                currenttag = "::".join(currenttag.split("::")[:-1])
            title = entry.find('./Title')
            if title is not None:
                title = re.sub(r'(\[[^\]]+\]\s)',"", title.text)
                title = tag(title)
                    
                #if lastwas is True:
                currenttag += "::" + title
                #print([seq, typ, title, currenttag])
            else:
                title = ""
            lastwas == True
            
        elif typ == "Item":
            lastwas = False
            #print(seq, ord)
            content = entry.find('./Content')
        
            question = content.find('./Question').text
            question = HTMLEntitiesToUnicode(question)
            
            answer = content.find('./Answer')
            answer = HTMLEntitiesToUnicode(answer.text) if answer is not None else ""
            
            qimg, aimg = [],[]
            qaudio, aaudio = [], []

            images = content.findall('./Image')
            #print(images)
            for image in images:
                imageurl = image.find('./URL').text
                imagetitle = image.find('./Name').text
                imageext = imageurl[-3:]
                imagename = re.search(r'([^\\]+)\.[^\\]+$',imageurl).group(1)
                imageback = image.find('./Answer') #image is seen only on backside
                #imagetag = f'<img src="{imagename}.{imageext}" alt="{imagetitle}">'
                imagetag = f'<img src="{clean(imagetitle)}.{imageext}" alt="{imagetitle}">'

                #print([imagetitle, imagename])
                #copy and rename the media file
                before = "D:/Anki2a/AE2018/collection.media/" + imagename+"."+imageext
                after = "D:/Anki2a/AE2018/collection.media2/" + clean(imagetitle)+"."+imageext
                shutil.copy2(before, after)
                
                if imageback is not None:
                    aimg.append(imagetag)
                else:
                    qimg.append(imagetag)
                
            sounds = content.findall('./Sound')
            for sound in sounds:
                #soundt = clean(sound.find('./Text').text)
                #print("content:")
                #print_content(sound)
                soundtitle = sound.find('./Name').text
                soundurl = sound.find('./URL').text
                soundname = re.search(r'([^\\]+)\.[^\\]+$',soundurl).group(1)
                #avoid names that are too long
                if len(soundtitle)>128:
                    soundtitle = soundtitle[:128]
                soundext = soundurl[-3:]
                soundtag = f"[sound:{clean(soundtitle)}.{soundext}]"
                
                #copy and rename the media file
                
                before2 = "D:/Anki2a/AE2018/collection.media/" + soundname+"."+soundext
                after2 = "D:/Anki2a/AE2018/collection.media2/" + clean(soundtitle) + "." + soundext
                try:
                    shutil.copy2(before2, after2)
                except:
                    print([before2, after2])
                
                audioback = sound.find('./Answer')

                if audioback is not None:
                    #if audioback.text =="T":
                    aaudio.append(soundtag)
                else:
                    qaudio.append(soundtag)

            currenttag = currenttag.replace("::Advanced_English","AE2018")
            note = [ord, question, answer, "".join(qimg), "".join(aimg),
                              "".join(qaudio), "".join(aaudio), currenttag]
            #print(note)
            #print(currenttag)
            fout.write("\t".join(note)+"\r\n")
        
    fout.close()
    print(count)

createnotes()
print("done.")
