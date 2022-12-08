"""
This is the script that was used to create the dataset.
This script only runs from the context of the Edusources harvester.
It is added here for reference and documentation only.
"""
from core.models import DatasetVersion, Document


dv = DatasetVersion.objects.get_current_version()


with open("data.json", "w") as json_file:
    import json
    for doc in Document.objects.filter(dataset_version=dv, collection__name="edusources", properties__language__metadata="en"): 
        if not doc.properties.get("learning_material_disciplines", None):
            continue
        text = doc.properties.get("text", None)
        if text is None:
            print(doc.reference)
            continue
        text_lines = [line for line in text.split("\n") if line.strip()]
        document_disciplines = [disciplines for disciplines in doc.properties["learning_material_disciplines"] if "interdisciplinair" not in disciplines]
        if not document_disciplines:
            continue
        data = {"id": doc.properties["external_id"], "title": doc.properties["title"], "description": doc.properties["description"], "text": "\n\n".join(text_lines), "disciplines": document_disciplines}
        json_file.write(json.dumps(data) + "\n")

