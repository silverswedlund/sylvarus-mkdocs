# {{ name }} — ({{ pronouns }})

<!-- Optional -->
<img src="{{ image_path }}" alt="{{ name }}" width="400" />
---

## 📕 Details
**Pronouns:** {{ pronouns }}  
**Aliases:**  
{% for alias in aliases %}
  - {{ alias }}  
{% endfor %}  
**Species:** {{ species }}  
**Divine Trial:** {{ divine_trial }}  
**Pre-Fall Species:** {{ pre_fall_species }}  
**LGBTQ+ Identifications:**  
{% set lgbtq_identifications_with_images = ["agender", "aromantic", "asexual", "demiboy", "demigirl", "disabled", "mlm", "genderqueer", "lesbian", "nonbinary", "pansexual", "transgender", "bicurious"] %}
{% for id in lgbtq_identifications %}
  {% for flag in lgbtq_identifications_with_images %}
    {% if flag in (id | lower | replace(' ', '_')) %}
      <img src="../../flags/{{ flag }}.jpg" alt="{{ id }} flag" width="30" style="vertical-align: middle; margin-right: 6px;">
    {% endif %}
  {% endfor %}
  {{ id }}  
{% endfor %}

**Other Identifications:**  
{% set other_identifiers_with_images = ["adhd", "autism", "disabled", "polyamorous", "neurodivergent"] %}
{% for id in other_identifiers %}
  {% for flag in other_identifiers_with_images %}
    {% if flag in (id | lower | replace(' ', '_')) %}
      <img src="../../flags/{{ flag }}.jpg" alt="{{ id }} flag" width="30" style="vertical-align: middle; margin-right: 6px;">
    {% endif %}
  {% endfor %}
  {{ id }}  
{% endfor %}

{% if song_name and music_path %}
{% if song_name != "" and music_path != "" %}
**Theme Music:**  
<audio controls>
  <source src="{{ music_path }}" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

"{{ song_name }}"  
{% endif %}
{% endif %}

{{ custom_details }}

---

## 🌀 Current Status
{{ current_status }}

---

## 📜 History
{{ history }}

---

## 🧠 Description
{{ description }}

---

{% if relationships %}
## 🧩 Notable Relationships
{% for relationship in relationships %}
  - {{ relationship }}  
{% endfor %}

---
{% endif %}
