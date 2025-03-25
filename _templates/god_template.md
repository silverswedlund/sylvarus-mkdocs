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
{% for id in lgbtq_identifications %}
  - {{ id }}  
{% endfor %}

**Other Identifications:**  
{% for id in other_identifiers %}
  - {{ id }}  
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

## 🧩 Notable Relationships
{{ relationships }}

---
