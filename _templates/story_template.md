# {{ name }}

<!-- Optional -->
<img src="{{ image_path }}" alt="{{ name }}" width="400" />
---
{% if character_names %}
## 📕 Characters
{% for character_name in character_names %}
  -  {{ character_name }}  
{% endfor %}
---
{% endif %}


## 📕 Details
|story_placeholder|
