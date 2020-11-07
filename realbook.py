from pdfrw import PdfReader, PdfWriter
from string import capwords

def openCsv(path):
    import csv
    results = []
    with open(path) as csvFile:
        reader = csv.reader(csvFile)
        return list(reader)
        
def parseReal(book, index, offset=0):
    index = openCsv(index)
    book = PdfReader(book)
    for i in range(len(index)):
        song = index[i]
        start_page = int(song[1]) + offset
        if i < len(index) - 1:
            end_page = int(index[i+1][1]) + offset
        else:
            end_page = int(index[i][1]) + 1 + offset
        if start_page == end_page: end_page += 1
        print(song, start_page, end_page)
        writer = PdfWriter()
        for p in range(start_page, end_page):
            writer.addpage(book.pages[p])
        writer.write(f'static/pdf/{capwords(song[0])}.pdf')