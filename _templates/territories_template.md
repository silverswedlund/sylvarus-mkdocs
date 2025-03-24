# {{ name }} — ({{ world }})

<div style="display: flex; gap: 20px; align-items: center; margin-top: 1rem; margin-bottom: 1rem;">
  {% if flag_path %}
    <div>
      <strong>Flag</strong><br />
      <img src="{{ flag_path }}" alt="{{ name }} Flag" width="200" />
    </div>
  {% endif %}
  {% if image_path %}
    <div>
      <strong>Visual Example</strong><br />
      <img src="{{ image_path }}" alt="{{ name }} Visual" width="400" />
    </div>
  {% endif %}
</div>

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

**Anthem:**  
<audio controls>
  <source src="{{ anthem_path }}" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>  
"{{ song_name }}"  

{{ custom_details }}

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
