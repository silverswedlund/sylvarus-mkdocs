# {{ name }} — ({{ world }})

<strong>Visual Example</strong><br />
<img src="{{ aesthetic_image_path }}" alt="{{ name }} Aesthetic Visual" width="700" />

---

## 🗺️ Basic Information
**Region:** {{ region }}  
**Population:** {{ population }}  
**Capital City:** [{{ capital }}](../../cities/{{ capital }})  
**Major Cities:** {{ major_cities }}  
**Government Type:** {{ government_type }}  
**Ruling Power:** {{ ruling_power }}  
**Founding Time Period:** [{{ founding_time_period }}](../../../history/time_periods/{{ founding_time_period_link_name }})  
**Majority Species:** {{ majority_species }}  
**Known For:** {{ known_for }}

{% if anthem_path %}
  **Anthem:** {% if anthem_name %}"{{ anthem_name }}"{% endif %}  
  <audio controls>
    <source src="{{ anthem_path }}" type="audio/mpeg">
    Your browser does not support the audio element.
  </audio>  
  {% if song_title %}"{{ song_title }}"{% endif %}

  {{ custom_details }}
{% endif %}

{% if flag_image_path %}
  <div>
    <strong>Flag</strong><br />
    <img src="{{ flag_image_path }}" alt="{{ name }} Flag Image" width="300" />
  </div>
{% endif %}

---

## 🧭 Description
{{ description }}

---

## 📜 History
{{ history }}

---

## 🎭 Culture
{{ culture }}

---

## 🛡️ Politics & Foreign Relations
{{ politics }}

---

## 🔗 Notable Relationships
{{ relationships }}

---

## 🌆 Territories & Geography
{{ geography }}

---

## 🧩 Additional Notes
{{ notes }}
