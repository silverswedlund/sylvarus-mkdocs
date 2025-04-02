# {{ name }}

<!-- Optional -->
{% if image_path %}
<img src="{{ image_path }}" alt="{{ name }}" width="400" />
{% endif %}

---
{% if character_names %}
## 📕 Characters
{% for character_name in character_names %}
  -  {{ character_name }}  
{% endfor %}
---
{% endif %}


## 📕 Story
|story_placeholder|
