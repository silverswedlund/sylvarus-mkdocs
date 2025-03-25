# {{ name }} — ({{ pronouns }})

<!-- Optional -->
<img src="{{ image_path }}" alt="{{ name }}" width="400" />
---

## 📕 Details
**Pronouns:** {{ pronouns }}  
**Titles/Aliases:**
<ul>
{% for alias in aliases %}
  <li>{{ alias }}</li>
{% endfor %}
</ul>

**Pre-ascension Species:** [{{ species }}](../../species/{{ species }})  
**[Time Period](../../history/time_periods/) of Ascension:** [{{ ascension_time_period }}](../../history/time_periods/{{ ascension_time_period | lower | replace(' ', '_') }})  
**[Pantheon](../../../pantheons):** [{{ pantheon }}](../../pantheons/{{ pantheon }})  
**Divine Trial:** {{ trial }}  
**LGBTQ+ Identifications:**
<ul>
{% for id in lgbtq_identifications %}
  <li>{{ id }}</li>
{% endfor %}
</ul>

**Other Identifications:**
{% for id in other_identifiers %}
  <li>{{ id }}</li>
{% endfor %}
</ul> 


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
