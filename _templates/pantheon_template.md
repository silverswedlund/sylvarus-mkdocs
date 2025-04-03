# {{ name }}
{% for example_image_path in example_image_paths %}
<img src="{{ example_image_path }}" alt="example_image of a {{ name }}" style="height: 600px; width: auto;" />
{% endfor %}
---

## 🏛️ Pantheon Overview
**Era of Creation:**  
  - {{ era_of_creation }}  
**Founding Member:**  
  - {{ founding_member }}  
**Current Leader:**  
  - {{ current_leader }}  


{{ custom_details }}

---


## 🧙 Members
|members_table|
