# Usage: python decode_ufn.py input.pdf output.pdf 
    
import argparse
import fitz # fitz is a module of PyMuPDF library, do not install fitz library

import argparse
 
parser = argparse.ArgumentParser(description="Decode PDF files taken from https://ufn.ru/", 
                                 epilog='PyMuPDF is required (pip install PyMuPDF)')
parser.add_argument("input", help="Input PDF file")
parser.add_argument("output", help="Output PDF file")
args = parser.parse_args()

print(fitz.__doc__)

doc = fitz.open(args.input)

# decode metadata

print('\nOld metdata:')
print(doc.metadata)

def swap_bytes(string):
    return ''.join(chr(((n & 255) << 8) + (n >> 8) if n > 2048 else n) for n in map(ord, string))

metadata = doc.metadata
metadata['title'] = swap_bytes(metadata['title'])
metadata['author'] = swap_bytes(metadata['author'])
doc.set_metadata(metadata)

print('\nNew metdata:')
print(doc.metadata)


# decode table of contents

toc = doc.get_toc()
print('\nOld table of contents:')
print(toc)
for entry in toc:
    try:
        entry[1] = entry[1].encode('cp1252').decode('cp1251')
    except:
        print('Unexpected TOC entry')
doc.set_toc(toc)
print('\nNew table of contents:')
print(toc)


# decode the main text

print('\nApplying a new Unicode mapping for the main text.')
cyr_alph = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя' # note Ё and ё here
offset = 161
table = [f'<{i + offset:04x}> <{ord(c):04x}> %{c}' for i, c in enumerate(cyr_alph)]

cmap=f"""/CIDInit /ProcSet findresource begin
12 dict begin
begincmap
/CMapType 2 def
/CMapName /UFN def
1 begincodespacerange
<0000><FFFF>
endcodespacerange
0 beginbfrange
endbfrange
{len(table)} beginbfchar
{chr(10).join(table)}
endbfchar
endcmap
CMapName currentdict /CMap defineresource pop
end end"""

cmap_xref = doc.get_new_xref()
doc.update_object(cmap_xref, "<<>>")
doc.update_stream(cmap_xref, cmap.encode())

for xref in range(1, doc.xref_length()): # skip item 0!
    if doc.xref_is_font(xref):
        doc.xref_set_key(xref, "ToUnicode", f"{cmap_xref} 0 R")
        
       
doc.save(args.output)
doc.close()



