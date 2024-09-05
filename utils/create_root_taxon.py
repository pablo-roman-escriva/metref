import os
import sys
sys.path.append("/home/pablo/metref")
print(sys.path)
import subprocess
import django 
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metref.settings")
django.setup()
from django.conf import settings
from django.core.files import File
from taxonomy.models import Genome
from taxonomy.models import Version
from taxonomy.models import Taxon
from taxonomy.models import Traits

import subprocess
import csv
from django.db.models import Q

BASE_URL = settings.PROJECT_ROOT
""" taxa = Taxon(tax_id=1, parent_tax_id = 0, rank="no rank", name = "cellular organisms")
taxa.save()
for version in Version.objects.all():
    taxa.version.add(version) """
taxa = Taxon.objects.all().filter(Q(name="Archaea") | Q(name="Eukaryota") | Q(name="Bacteria")).update(parent_tax_id=1)
