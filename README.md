# documanager
Simple web app in Django useful to produce precompiled documents.
Input data: 
  - django .html templates with empty spaces filled with {{ field_name }} tags
  - field_values fillable from a form into the only one ModelClass of the project

It requires WeasyPrint and so the lib libpangocairo. On Ubuntu:
apt install libpangocairo-1.0-0
