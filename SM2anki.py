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
    fout = codecs.open("D:/AdvEng2018.txt", mode="w", encoding="utf-8") #hardcoded
    tree = ET.parse("D:/learning (grammarcards).xml") #hardcoded
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
            #c += 1
            content = entry.find('./Content')
        
            question = content.find('./Question').text
            question = HTMLEntitiesToUnicode(question)
            
            question = re.sub(r'#SuperMemo Reference:(.+)',"",question)
            if question[:2] == "##":
                question = question[2:]
                #print(question)
            
            answer = content.find('./Answer')
            answer = HTMLEntitiesToUnicode(answer.text) if answer is not None else ""
            
            qimg, aimg = [],[]
            qaudio, aaudio = [], []

            images = content.findall('./Image')
            #print(images)
            for image in images:
                imageurl = image.find('./URL').text.replace("[SecondaryStorage]","").replace("\\","/")
                imageurl = imageurl.replace("c:/users/guill/supermemo/sm184/systems/learning/elements/","") #hardcoded
                imagetitle = image.find('./Name').text
                imagetitle = re.sub(r"(#.+)","",imagetitle).strip()
                
                
                imageext = imageurl[-3:]
                imagename = re.search(r'([^\\]+)\.[^\\]+$',imageurl).group(1)
                imageback = image.find('./Answer') #image is seen only on backside
                #imagetag = f'<img src="{imagename}.{imageext}" alt="{imagetitle}">'
                imagetag = f'<img src="{clean(imagetitle)}.{imageext}" alt="{imagetitle}">'

                #print([imagetitle, imageurl])
                #copy and rename the media file
                
                before = "C:/Users/guill/supermemo/SM184/systems/learning/elements/" + imageurl #hardcoded
                #before = "D:/learning (grammarcards)_files/Elements/" + imageurl
                after = "D:/Anki2a/myitems/collection.media/" + clean(imagetitle)+"."+imageext #hardcoded

                try:
                    shutil.copy2(before, after)
                except:
                    print([before, after])
                    c+=1
                
                
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
                soundtitletitle = re.sub(r"(#.+)","",soundtitle).strip()
                soundurl = sound.find('./URL').text.replace("[SecondaryStorage]","").replace("\\","/")
                soundurl = soundurl.replace("c:/users/guill/supermemo/sm184/systems/learning/elements/","") #hardcoded username
                soundname = re.search(r'([^\\]+)\.[^\\]+$',soundurl).group(1)
                #avoid names that are too long
                if len(soundtitle)>128:
                    soundtitle = soundtitle[:128]
                soundext = soundurl[-3:]
                soundtag = f"[sound:{clean(soundtitle)}.{soundext}]"
                
                #copy and rename the media file
                #print(soundurl)
                
                before2 = "C:/Users/guill/supermemo/SM184/systems/learning/elements/" + soundurl #hardcoded
                #before2 = "D:/learning (grammarcards)_files/Elements/" + soundurl
                after2 = "D:/Anki2a/myitems/collection.media/" + clean(soundtitle) + "." + soundext #hardcoded
                try:
                    shutil.copy2(before2, after2)
                except:
                    print([before2, after2])
                    c+=1
                
                audioback = sound.find('./Answer')

                if audioback is not None:
                    #if audioback.text =="T":
                    aaudio.append(soundtag)
                else:
                    qaudio.append(soundtag)

            currenttag = currenttag.replace("::Advanced_English","AE2018")
            note = [question, answer, "".join(qimg), "".join(aimg),
                              "".join(qaudio), "".join(aaudio)]
            
            
            #print(len(note))
            #print(note)
            #print(currenttag)
            fout.write("\t".join(note)+"\r\n")
    print(str(c))
    fout.close()
    print(count)

createnotes()
print("done.")
