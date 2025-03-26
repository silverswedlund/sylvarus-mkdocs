# {{ name }} — ({{ pronouns }})

<!-- Optional -->
<img src="{{ image_path }}" alt="{{ name }}" width="400" />
---

## 📕 Details
**Pronouns:** {{ pronouns }}  
**Titles/Aliases:**  
{% for alias in aliases %}
  - {{ alias }}  
{% endfor %}

**Pre-ascension Species:** [{{ species }}](../../species/{{ species }})  
**[Time Period](../../history/time_periods/) of Ascension:** [{{ ascension_time_period }}](../../history/time_periods/{{ ascension_time_period | lower | replace(' ', '_') }})  
**[Pantheon](../../../pantheons):** [{{ pantheon }}](../../pantheons/{{ pantheon }})  
**Divine Trial:** {{ trial }}  
**LGBTQ+ Identifications:**  
{% set lgbtq_identifications_with_images = ["agender", "aromantic", "asexual", "demiboy", "demigirl", "disabled", "gay(mlm)", "genderqueer", "lesbian", "nonbinary", "pansexual", "transgender", "bicurious"] %}
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

**Theme Music:**  
<audio controls>
  <source src="{{ music_path }}" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

"{{ song_name }}"  


{{ custom_details }}

---

## 🌀 Current Status
{{ current_status }}

---

## 📜 History
{{ history }}

---

## 👤 Physical Description
{{ physical_description }}

---
{% if relationships %}
## 🧩 Notable Relationships
{% for relationship in relationships %}
  - {{ relationship }}  
{% endfor %}

---
{% endif %}
