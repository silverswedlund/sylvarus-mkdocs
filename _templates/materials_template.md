# {% if page_title %}{{ page_title }}{% else %}{{ name }}{% endif %}

<!-- Optional -->
<img src="{{ image_path }}" alt="{{ name }}" style="width: 450px; height: auto;" />
---

## 📕 Details
**Type:**  
  - {{ type }}  
**Properties:**  
{% for property in properties %}
  - {{ property }}  
{% endfor %}  
**Uses:**  
{% for use in uses %}
  - {{ use }}  
{% endfor %}  
**Origin:**  
  - {{ origin }}  

{% if rarity %}
**Rarity:**  
  - {{ rarity }}  
{% endif %}

**Additional Details:**  
  - {{ custom_details }}

---

## 📜 History
  - {{ history }}

---