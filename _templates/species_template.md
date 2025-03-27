# {{ name }}

---

## 🧬 Classification
**Type:** {{ type }}  
**Origin:** {{ origin }}  
**Average Lifespan:** {{ lifespan }}  
**Typical Physique:** {{ physique }}  
**Common Languages:**  
{% for language in languages %}
  - {{ language }}  
{% endfor %}
{{ custom_details }}

---

## 🌍 Distribution
**Homeland(s):** {{ homelands }}  
**Presence in Other Regions:** {{ other_regions }}
{{ distribution }}

---

## 📜 Historical Background
{{ history }}

---

## 🧑‍🤝‍🧑 Society & Culture
**Religious Beliefs:** {{ religion }}  
**Traditions & Customs:** {{ traditions }}  

{{ custom_details }}

---

## 🧙 Notable Figures
{% for notable_figure in notable_figures %}
  - {{ notable_figure }}  
{% endfor %}

---

## 🔗 Relationships with Other Species
{{ relationships }}

---
