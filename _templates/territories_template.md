# {{ name }} — ({{ world }})

{% if aesthetic_image_path or map_image_path or world_location_image_path %}
<div style="display: flex; gap: 2rem; align-items: flex-start; flex-wrap: wrap;">

  <div style="display: flex; flex-direction: column; gap: 1rem;">
    {% if map_image_path %}
    <div>
      <div><strong>Map</strong></div>
      <img src="{{ map_image_path }}" alt="{{ name }} Map" width="400" />
    </div>
    {% endif %}

    {% if world_location_image_path %}
    <div>
      <div><strong>World Location</strong></div>
      <img src="{{ world_location_image_path }}" alt="{{ name }} World Location" width="400" />
    </div>
    {% endif %}
  </div>

  {% if aesthetic_image_path %}
  <div>
    <div><strong>Visual Example</strong></div>
    <img src="{{ aesthetic_image_path }}" alt="{{ name }} Aesthetic Visual" width="500" />
  </div>
  {% endif %}

</div>
{% endif %}

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

