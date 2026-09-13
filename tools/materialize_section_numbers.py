from docx import Document
from docx.oxml.ns import qn
import re

PATH = "/Users/thandoan/Documents/Presentations/DevOps/Network-DevOps-Professional-Study-Guide.docx"
MODULES = {
    "Network Automation Review",
    "Introducing the DevOps Model",
    "Infrastructure as Code and On-Demand Environments",
    "Packaging and Operating Applications",
    "Continuous Integration Delivery and Deployment Validation",
    "Security and Observability",
}

doc = Document(PATH)
in_modules = False
module = -1
major = 0
minor = 0

for p in doc.paragraphs:
    if p.style.name not in {"Heading 1", "Heading 2", "Heading 3"}:
        continue
    bare = re.sub(r"^\d+(?:\.\d+)*\s+", "", p.text.strip())
    if bare in MODULES and p.style.name == "Heading 1":
        in_modules = True
        module += 1
        major = minor = 0
    if not in_modules:
        continue

    ppr = p._p.get_or_add_pPr()
    numpr = ppr.find(qn("w:numPr"))
    if numpr is not None:
        ppr.remove(numpr)

    if bare == "Learning objectives":
        if p.text != bare:
            p.text = bare
        continue

    if p.style.name == "Heading 1":
        number = str(module)
    elif p.style.name == "Heading 2":
        major += 1
        minor = 0
        number = f"{module}.{major}"
    else:
        minor += 1
        number = f"{module}.{major}.{minor}"
    p.text = f"{number} {bare}"

doc.save(PATH)
print(PATH)
