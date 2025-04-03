# {{ name }}
{% for example_image_path in example_image_paths %}
<img src="{{ example_image_path }}" alt="example_image of a {{ name }}" style="height: 600px; width: auto;" />
{% endfor %}
---

## 🧬 Classification  
**Type:** {{ type }}  
**Origin:** {{ origin }}  
**Average Lifespan:** {{ lifespan }}  
**Average Size:** {{ average_size_range }}  
**Typical Physique:** {{ physique }}  
**Common Languages:**  
{% for language in languages %}
  - {{ language }}  
{% endfor %}

{% if custom_details %}
**Additional Details:**  
  - {{ custom_details }}
{% endif %}

---

## 🌍 Distribution  
**Homeland(s):** {{ homelands }}  
**Presence in Other Regions:** {{ other_regions }}
{{ distribution }}

---

{% if history %}
## 📜 Historical Background  
{{ history }}
{% endif %}

---

## 🧑‍🤝‍🧑 Society & Culture
**Religious Beliefs:**  
  - {{ religion }}  
**Traditions & Customs:**  
{% for tradition in traditions %}
  - {{ tradition }}  
{% endfor %}

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
