"""
This is the script that was used to create the dataset.
This script only runs from the context of the Edusources harvester.
It is added here for reference and documentation only.
"""
from core.models import DatasetVersion, Document


dv = DatasetVersion.objects.get_current_version()


counter = 0
for doc in Document.objects.filter(collection__name="edusources", dataset_version=dv, pipeline__tika__success=True, properties__technical_type="document"):
    if doc.properties["text"] and len(doc.properties["text"]) >= 25000:
        print(
            doc.reference,
            "PDF" if doc.properties["files"][0]["mime_type"] == "application/pdf" else "WRD",
            doc.properties["files"][0]["url"],
            doc.pipeline["tika"]["id"]
        )
        counter += 1
        if counter >= 20:
            break

"""
OUTPUT FROM AWS DEV ON 2023-03-03

47be7709-02f6-4604-bab5-9a375a808d5c PDF https://acc.surfsharekit.nl/objectstore/0b6a47dc-b50b-42a5-b7bb-2f6249cc4577 38034 *  # powerpoint
7d6808ec-96a9-4544-927e-089c21607381 PDF https://acc.surfsharekit.nl/objectstore/1d863ed1-1609-453e-a6f3-5b5e107be543 38018 ** # onderzoek naar leermateriaal
5d7d3c4c-000c-4210-ac18-9a57646c46f4 PDF https://acc.surfsharekit.nl/objectstore/8d5015a1-ace2-49ba-8c80-8e5c254b32cc 37886 ** # inhoudsopgave, part-of?
f6661c21-66bf-41bd-910b-effda1cd58f7 PDF https://acc.surfsharekit.nl/objectstore/27f3d9a1-d752-4704-b6b8-0fe0439f0859 39478 ** # inhoudsopgave, bijlage, literatuurlijst, lesprogramma
b9c2f3ac-766e-4eda-a778-4770845eef65 WRD https://acc.surfsharekit.nl/objectstore/145cae9f-c834-4c38-8c34-4c76479da3ca 37835 ** # literatuurlijst, part-of
7107d7d9-3d08-419d-8080-728899e563da PDF https://acc.surfsharekit.nl/objectstore/980c703f-1a5b-4ede-ab0d-ae73346df39c 38124 ** # bijlage, literatuurlijst
8c5b0b25-722a-4bec-b6b6-38b6b86ef5c4 WRD https://acc.surfsharekit.nl/objectstore/a66199a5-3224-4de2-bb97-736d791506a2 38979 ** # bijlage, literatuurlijst, lesprogramma
2e29c6f8-992c-469c-9d6b-9bed0799e6b7 WRD https://acc.surfsharekit.nl/objectstore/b44e49ee-b7b8-4996-a417-bd5dda40894a 37826 ** # literatuurlijst, part-of
ac075e5d-5509-4d28-872b-93e093d2bd1b WRD https://acc.surfsharekit.nl/objectstore/c6e37500-6421-4797-a118-fa381fff30f3 38726 *  # inhoudsopgave, lesprogamma
669faa13-9177-4459-b2ce-146579858d39 PDF https://acc.surfsharekit.nl/objectstore/dd08ca16-7933-4790-8c06-14c491c92f96 39167 ** # part-of
52314966-68d3-415a-a803-8414431cb1d4 PDF https://acc.surfsharekit.nl/objectstore/f0d3deb0-8a9e-424d-b8ee-0216d04f97e6 38340 *  # inhoudsopgave, bijlage, literatuurlijst
30744e04-b805-4b0a-a4db-541c4435a605 WRD https://acc.surfsharekit.nl/objectstore/fb0c08c2-6bfc-43ee-b132-71cda7265964 38965 ** # inhoudsopgave, bijlage, literatuurlijst, lesprogramma

DISCARDED OUTPUT

d5e45645-6162-4a77-ab7e-cdb0cb6a284c PDF https://acc.surfsharekit.nl/objectstore/59d19226-46f4-4240-9d91-b0de168ed5ec 37916
12d8fce7-e7b3-4fe9-8a21-699201f889a9 WRD https://acc.surfsharekit.nl/objectstore/564d3811-9fd4-4e1e-8807-691101c4f058 37987
9045e99f-9ba3-4159-bf92-576b6da52b6f WRD https://acc.surfsharekit.nl/objectstore/ad93eaaa-eba5-4a8d-93dd-b0943ee31a1d 37904
a5af5a2a-cfe9-43c8-a4f8-f7b514cde792 PDF https://acc.surfsharekit.nl/objectstore/7e3de5bc-361c-4aa8-a432-9a55e2dde295 37915
c117bcaa-6024-4817-9cbb-787a85fba65f PDF https://acc.surfsharekit.nl/objectstore/6cfb5070-dfb1-4ef0-be2e-cd67cd788b75 38019
bc96f255-c9a5-4cd0-85d6-997323d07564 WRD https://acc.surfsharekit.nl/objectstore/d52469fe-0013-4ab1-aa8c-f6bcb04d8057 38315
c9a43387-1810-4fa6-b181-26caa228f51f WRD https://acc.surfsharekit.nl/objectstore/2577f63c-ff8b-4152-8d5b-71426391d715 37816
b8720906-06ac-4b0a-ae1e-a0a2cffa9970 PDF https://acc.surfsharekit.nl/objectstore/789f035d-004b-48b3-955c-d13c76316f94 37891
"""
