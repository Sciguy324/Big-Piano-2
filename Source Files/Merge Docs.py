# Import modules
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import AnnotationBuilder
import re
from os import path

# Load documents
initial_docs = PdfReader('Larger Than Life Piano Partial Documentation.pdf')
dimension_files = ['Full Piano Drawing.pdf',
                   'All Exploded Keys Drawing.pdf',
                   'Module Box Drawing.pdf',
                   'Potentiometer Knob Drawing.pdf']

# Merge the two, applying rotations to the second document
writer = PdfWriter()
for page in initial_docs.pages:
    writer.addPage(page)

# Rebuild annotations/links in table-of-contents page
pages = initial_docs.outline[1]['/Page']['/Parent']['/Kids']
new_annotations = []
for i, annotation in enumerate(writer.pages[1].annotations):
    obj = annotation.get_object()
    # Extract hitbox from annotation
    rect = obj['/Rect']
    # Extract page number
    dest = obj['/Dest'][0]
    page_num = pages.index(dest)
    # Create new annotation
    anno = AnnotationBuilder.link(rect=rect, target_page_index=page_num, fit='/FitH', fit_args=(123,))
    new_annotations.append(anno)


# Add table of contents to outline
writer.add_outline_item('Table of Contents', 1)

# Copy over existing outline
def buildOutline(doc, writer, outline, parent=None):
    most_recent = None
    for i in outline:
        if isinstance(i, list):
            buildOutline(doc, writer, i, parent=most_recent)
        
        else:
            title = i['/Title']
            pageNum = pages.index(i.get('/Page'))
            most_recent = writer.add_outline_item(title, pageNum, parent=parent)

    return most_recent

final_item = buildOutline(initial_docs, writer, initial_docs.outline)


# Clear existing annotations and set new ones
writer.pages[1].annotations.clear()
for anno in new_annotations:
    writer.add_annotation(page_number=1, annotation=anno)

# Get page size for later scaling
size = writer.pages[0].mediabox
width = size[2] - size[0]
height = size[3] - size[1]

# Rotate the dimension docs and add to document
pageCount = len(initial_docs.pages)
for file in dimension_files:
    dimension_docs = PdfReader(file)
    for page in dimension_docs.pages:
        page.rotateCounterClockwise(-90) # Rotate
        # Rescale
        page.scale_to(height, width)
        writer.addPage(page) # Add to document

    # Add to outline
    title = path.splitext(file)[0]
    writer.add_outline_item(title, pageCount, parent=final_item)
    pageCount += len(dimension_docs.pages)

# Write merged document
writer.write('Larger Than Life Piano Docs (WIP).pdf')
