import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
import shutil

template_path = r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\Submission_template.docx"
doc = docx.Document(template_path)

# 1. Update cover page
for p in doc.paragraphs:
    if "Lab #" in p.text:
        p.text = "Lab 5"
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(14)
            r.font.bold = True
    elif "Nguyen Van A" in p.text:
        p.text = "Nguyen Le Minh Sang – EEACIU24096"
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(12)
            r.font.bold = True
    elif "Date Submitted" in p.text:
        p.text = "\tDate Submitted:\t\t20/11/2026"
    elif "Date Performed" in p.text:
        p.text = "\tDate Performed:\t\t20/11/2026"
    elif "Group Section" in p.text:
        p.text = "\tGroup Section:\t\t02"
    elif "Course Instructor" in p.text:
        p.text = "\tCourse Instructor:\tDr. Hieu Nguyen"

# 2. Find where Problem 1 starts in template paragraphs
body_start = None
for i, p in enumerate(doc.paragraphs):
    if "Problem 1:" in p.text:
        body_start = i
        break

print("Body start index:", body_start)

# Delete existing template placeholders from body_start onwards
if body_start is not None:
    p_to_del = doc.paragraphs[body_start:]
    for p in p_to_del:
        p._p.getparent().remove(p._p)

# 3. Data for 5 problems
problems = [
    {
        "num": 1,
        "desc": "Create an int variable num = 10 and a pointer ptr to it. Print the address of num; print num’s value through the pointer; change num to 20 using only the pointer; print the new value to verify.",
        "c_file": r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\ex1.c",
        "img": r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\screenshots\ex1_output.png"
    },
    {
        "num": 2,
        "desc": "Read two numbers n1 and n2. Write a function swap(int *a, int *b) that exchanges their values through pointers. Print the values after swapping.",
        "c_file": r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\ex2.c",
        "img": r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\screenshots\ex2_output.png"
    },
    {
        "num": 3,
        "desc": "Read a whole number of seconds. Write a function convert(int total, int *h, int *m, int *s) that returns hours, minutes and seconds through pointer parameters. Print the result in main.",
        "c_file": r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\ex3.c",
        "img": r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\screenshots\ex3_output.png"
    },
    {
        "num": 4,
        "desc": "Read a radius. Write void calcCircle(double radius, double *circ, double *area) that computes both the circumference and the area and returns them through pointers. Print everything from main, not from calcCircle.",
        "c_file": r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\ex4.c",
        "img": r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\screenshots\ex4_output.png"
    },
    {
        "num": 5,
        "desc": "Read one floating-point number (e.g. 3.14159). Write void decompose(double x, int *intPart, double *fracPart) that splits it into its integer and fractional parts and returns them through pointers (no return value). All printing is done in main.",
        "c_file": r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\ex5.c",
        "img": r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab\screenshots\ex5_output.png"
    }
]

for prob in problems:
    # Problem statement paragraph
    p_prob = doc.add_paragraph()
    p_prob.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_prob.paragraph_format.space_before = Pt(14)
    p_prob.paragraph_format.space_after = Pt(4)
    
    r1 = p_prob.add_run(f"Problem {prob['num']}: ")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(13)
    r1.font.bold = True
    
    r2 = p_prob.add_run(prob['desc'])
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)
    
    # Code header
    p_code_hdr = doc.add_paragraph()
    p_code_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_code_hdr.paragraph_format.space_before = Pt(6)
    p_code_hdr.paragraph_format.space_after = Pt(4)
    r_ch = p_code_hdr.add_run("Code:")
    r_ch.font.name = "Times New Roman"
    r_ch.font.size = Pt(12)
    r_ch.font.bold = True
    
    # Code body lines
    with open(prob['c_file'], "r", encoding="utf-8") as fp:
        lines = fp.read().splitlines()
    for l in lines:
        p_line = doc.add_paragraph()
        p_line.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_line.paragraph_format.space_before = Pt(0)
        p_line.paragraph_format.space_after = Pt(0)
        p_line.paragraph_format.line_spacing = 1.0
        
        # Use non-breaking spaces for indent so word justification never stretches it
        indent_len = len(l) - len(l.lstrip(" "))
        content = ("\xa0" * indent_len) + l.lstrip(" ")
        r_l = p_line.add_run(content if content else "")
        r_l.font.name = "Consolas"
        r_l.font.size = Pt(10)
        r_l.font.color.rgb = RGBColor(0, 0, 0)
    
    # Output header
    p_out_hdr = doc.add_paragraph()
    p_out_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_out_hdr.paragraph_format.space_before = Pt(8)
    p_out_hdr.paragraph_format.space_after = Pt(4)
    r_oh = p_out_hdr.add_run("Output:")
    r_oh.font.name = "Times New Roman"
    r_oh.font.size = Pt(12)
    r_oh.font.bold = True
    
    # Output screenshot image
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_img.paragraph_format.space_before = Pt(2)
    p_img.paragraph_format.space_after = Pt(14)
    r_img = p_img.add_run()
    r_img.add_picture(prob['img'], width=Inches(5.3))

# Ensure destinations exist
dest_dir1 = r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\IT091IU_Programming_for_Engineers_Lab"
dest_dir2 = r"C:\Users\LENOVO\OneDrive\Desktop\UNIVERSITY\IU Junior\C lab\lab5"
os.makedirs(dest_dir1, exist_ok=True)
os.makedirs(dest_dir2, exist_ok=True)

dest1 = os.path.join(dest_dir1, "EEACIU24096 - Nguyen Le Minh Sang - Lab 5.docx")
dest2 = os.path.join(dest_dir1, "EEACIU24096_NguyenLeMinhSang_LAB5.docx")
dest3 = os.path.join(dest_dir2, "EEACIU24096 - Nguyen Le Minh Sang - Lab 5.docx")
dest4 = os.path.join(dest_dir2, "EEACIU24096_NguyenLeMinhSang_LAB5.docx")

doc.save(dest1)
shutil.copyfile(dest1, dest2)
shutil.copyfile(dest1, dest3)
shutil.copyfile(dest1, dest4)

# Also copy c files, exes, and pdf to dest_dir2
for f in ["ex1.c", "ex2.c", "ex3.c", "ex4.c", "ex5.c", "ex1.exe", "ex2.exe", "ex3.exe", "ex4.exe", "ex5.exe", "lab5.pdf"]:
    src = os.path.join(dest_dir1, f)
    if os.path.exists(src):
        shutil.copyfile(src, os.path.join(dest_dir2, f))

print("Successfully generated and synchronized all files!")
