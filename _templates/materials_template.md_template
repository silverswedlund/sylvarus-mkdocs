# {{ name | replace("_", " ") | title }}  
{% if image_paths and image_descriptions %}
<div style="display: flex; flex-wrap: wrap;">
  {% for i in range(image_paths|length) %}
  {% set image_path = image_paths[i] %}
  {% set image_description = image_descriptions[i] %}
    <div style="margin: 10px;">
      <p>{{ image_description }}</p>
      <img src="{{ image_path }}" alt="{{ image_description }}" style="width: 500px; height: auto;" />
    </div>
  {% endfor %}
</div>
{% endif %}
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

{% if history %}
---

## 📜 History
  - {{ history }}
{% endif %}

---