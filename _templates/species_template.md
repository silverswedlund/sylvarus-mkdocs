# {{ name }}  

{% for example_image_path in example_image_paths %}
<img src="{{ example_image_path }}" alt="example_image of a {{ name }}" style="width: 450; height: auto;" />
{% endfor %}
---

## 🧬 Classification  
**Type:**  
  - {{ type }}  
**Origin:**  
  - {{ origin }}  
**Average Lifespan:**  
  - {{ lifespan }}  
**Average Size:**  
  - {{ average_size_range }}  
**Typical Physique:**  
  - {{ physique }} 
{% if languages %}
**Common Languages:**  
{% for language in languages %}
  - {{ language }}  
{% endfor %}
{% endif %}

{% if custom_details %}
**Additional Details:**  
  - {{ custom_details }}
{% endif %}

---

## 🌍 Distribution  
**Homeland(s):**  
  - {{ homelands }}  
**Presence in Other Regions:**  
  - {{ other_regions }}
{{ distribution }}

---

{% if history %}
## 📜 Historical Background  
  - {{ history }}
{% endif %}

---

{% if religion %}
## 🧑‍🤝‍🧑 Society & Culture
**Religious Beliefs:**  
  - {{ religion }}  
{% endif %}
{% if traditions %}
**Traditions & Customs:**  
{% for tradition in traditions %}
  - {{ tradition }}  
{% endfor %}
{% endif %}
---

{% if notable_figures %}
## 🧙 Notable Figures  
{% for notable_figure in notable_figures %}
  - {{ notable_figure }}  
{% endfor %}
{% endif %}
---

{% if relationships %}
## 🔗 Relationships with Other Species  
{% for relationship in relationships %}
  - {{ relationship }}  
{% endfor %}
{% endif %}
---

{% if species_members %}
## 🧑‍🤝‍🧑 Species Members  
{% include "species/{{name|lower}}/species_members_table.md_insert" %}
{% endif %}
