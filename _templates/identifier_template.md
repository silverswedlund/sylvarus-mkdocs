# {{ name }}

<!-- Optional -->
<img src="{{ image_path }}" alt="{{ name }}" width="400" />
---

## 📍 Basic Information
**Description:**  
  - {{ description }}  
**Related Identifiers:** 
{% for related_id in related_identifiers %}  
  - {{ related_id }}  
{% endfor %}

---

## 👥 List of Identifier-Havers  
{% include "identifiers/{{ type }}/{{ name|lower }}_id_havers_table.md_insert" %}

---
