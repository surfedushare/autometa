from invoke import Collection

from tasks.email import convert_mbox_to_eml


namespace = Collection(
    convert_mbox_to_eml
)
