import codecs
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
import shutil

input_xml_file = "data/adveng 2018 (AE2018).xml"
output_csv_file = "C:\\Temp\\AdvEng2018.txt"
source_base_path = "C:/Users/guill/supermemo/SM184/systems/learning/elements/"
dest_base_path = "D:/Anki2a/myitems/collection.media/"

start_node = ""
start_node = "Advanced English|Economics, Law and Political Sciences|Business and Economics|[1] Business and Economics"
start_node = "Advanced English|Economics, Law and Political Sciences|Business and Economics"

def HTMLEntitiesToUnicode(text):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
    text = BeautifulSoup(text, "lxml").text
    return text

def clean(s):
    s = s.replace("\n"," ").replace("/","-").replace("|","-").replace("(","-").replace(")","-").replace('"'," ")
    s = s.replace(":"," ").replace(";"," ").replace(".","-").replace('\\',"-")
    s = s.replace("?"," ").replace("*"," ").replace(">"," ").replace("<"," ")
    return s
                 
def tag(s):
    s = s.replace(" ","_").replace(".","").replace(",","").replace(";","").replace("::","_")
    return s

def read_item_element(element, path):
    ord = element.find('./Ordinal')
    ord = ord.text.zfill(5) if ord is not None else ""

    content = element.find('./Content')
    question = content.find('./Question').text
    question = HTMLEntitiesToUnicode(question)
    question = re.sub(r'#SuperMemo Reference:(.+)',"",question)
    if question[:2] == "##":
        question = question[2:]
        #print(question)

    answer = content.find('./Answer')
    answer = HTMLEntitiesToUnicode(answer.text) if answer is not None else ""

    qimg, aimg = [],[]
    images = content.findall('./Image')
    for image in images:
        imageurl = image.find('./URL').text.replace("[SecondaryStorage]","").replace("\\","/")
        imageurl = imageurl.replace(source_base_path,"") #hardcoded
        imagetitle = image.find('./Name').text
        imagetitle = re.sub(r"(#.+)","",imagetitle).strip()
        
        imageext = imageurl[-3:]
        imagename = re.search(r'([^\\]+)\.[^\\]+$',imageurl).group(1)
        imageback = image.find('./Answer') #image is seen only on backside
        #imagetag = f'<img src="{imagename}.{imageext}" alt="{imagetitle}">'
        imagetag = f'<img src="{clean(imagetitle)}.{imageext}" alt="{imagetitle}">'

        #print([imagetitle, imageurl])
        #copy and rename the media file
        
        before = source_base_path + imageurl #hardcoded
        #before = "D:/learning (grammarcards)_files/Elements/" + imageurl
        after = dest_base_path + clean(imagetitle)+"."+imageext #hardcoded

        try:
            shutil.copy2(before, after)
        except:
            print("Unable to copy image")
            print([before, after])
        
        if imageback is not None:
            aimg.append(imagetag)
        else:
            qimg.append(imagetag)

    qaudio, aaudio = [], []
    sounds = content.findall('./Sound')
    for sound in sounds:
        #soundt = clean(sound.find('./Text').text)
        #print("content:")
        #print_content(sound)
        soundtitle = sound.find('./Name').text
        soundurl = sound.find('./URL').text.replace("[SecondaryStorage]","").replace("\\","/")
        sound_ext = soundurl[-3:]
        soundurl = soundurl.replace("c:/users/guill/supermemo/sm184/systems/learning/elements/","") #hardcoded username
        soundname = re.search(r'([^\\]+)\.[^\\]+$',soundurl).group(1)

        ### avoid names that are too long
        if len(soundtitle)>128:
            soundtitle = soundtitle[:128]

        soundext = soundurl[-3:]
        soundtag = f"[sound:{clean(soundtitle)}.{sound_ext}]"
        
        ### copy and rename the media file
        # print(soundurl)

        before2 = source_base_path + soundurl #hardcoded
        #before2 = "D:/learning (grammarcards)_files/Elements/" + soundurl
        after2 = dest_base_path + clean(soundtitle) + "." + soundext #hardcoded
        try:
            shutil.copy2(before2, after2)
        except:
            print("Unabe to copy sound file")
            print([before2, after2])
        
        audioback = sound.find('./Answer')
        if audioback is not None:
            aaudio.append(soundtag)
        else:
            qaudio.append(soundtag)

    path = [tag(item) for item in path]
    currenttag = "::".join(path)
    currenttag = currenttag.replace("::Advanced_English", "AE2018")
    currenttag = "AE2018::" + currenttag
    note = [ord, question, answer, "".join(qimg), "".join(aimg),
            "".join(qaudio), "".join(aaudio), currenttag]

    return note


def iterate_with_depth(element, fout, path=["root"], depth=0):
    # if element.tag == 'SuperMemoElement':
    #   print(f"{'  ' * depth}SuperMemoElement id: {element.get('id')}, depth: {depth}")

    print(f"in path: {path}")

    seq = element.find('./ID').text
    typ = element.find('./Type').text
    title = element.find('./Title')
    title = title.text if title is not None else None

    if typ == "Topic":
        ### Copy the path to ensure not to overwrite the variable during recursion
        path2 = path[:]

        if title is not None:
            if (len(path2) > 0):
                t2 = re.search(r'^\[\d+\]', title)
                if (t2 is not None):
                    title = title.replace(t2.group(), "")
                
                title = title.strip()
                if path2[-1] != title:
                    path2.append(title)
            else:
                path2.append(title)

        path_str = ">".join(path2)
        # print(f"{'  ' * depth}{path_str}, title: {title}, depth: {depth}")
        print(f"{path_str}, title: {title}, depth: {depth}\n")

        for child in element.findall('SuperMemoElement'):
            child_seq = child.find('./ID').text
            child_typ = child.find('./Type').text
            # child_title = child.find('./Title')
            # child_title = child_title.text if child_title is not None else None

            if child_typ == "Topic":
                iterate_with_depth(child, fout, path2, depth + 1)

            elif child_typ == "Item":
                print(f"{'  ' * (depth+1)}read item node(1), ID: {child_seq}")
                note = read_item_element(child, path2)
                fout.write("\t".join(note) + "\r\n")
        pass

def find_start_node(element, path):
    if start_node != "" and start_node is not None:
        for node_title in start_node.split("|"):
            # node_found = False
            node_title = node_title.strip()

            for element in element.findall('SuperMemoElement'):
                title = element.find('./Title')
                title = title.text if title is not None else None

                if title is not None and title.lower() == node_title.lower():
                    print(f"Node title found: {node_title}")
                    element = element
                    path.append(title)
                    # node_found = True
                    break
                
                # if node_found is not True:
                #     print(f"Unable to find node element {node_title}")
                #     elem1 = None
                #     break

    return element

def main():
    tree = ET.parse(input_xml_file) #hardcoded
    # tree = ET.parse("data/sample1.xml") #hardcoded
    fout = codecs.open(output_csv_file, mode="w", encoding="utf-8") #hardcoded

    root = tree.getroot()
    elem1 = root.find('SuperMemoElement')
    path = []

    elem1 = find_start_node(elem1, path)
    print("")

    if elem1 is not None:
        if len(path) > 0:
            path.pop()
        iterate_with_depth(elem1, fout, path)
        pass
    else:
        print("Node not found")

    fout.close()


main()
print("All done")
