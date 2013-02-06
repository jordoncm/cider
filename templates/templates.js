{% autoescape None %}
cider.namespace('cider.templates');
{% if template_type %}
cider.namespace('cider.templates.{{ template_type }}');
{% end %}
{% for k, v in templates.items() %}
cider.templates.{{ k }} = '{{ v.replace('\n', '\\n').replace('\'', '\\\'') }}';
{% end %}
