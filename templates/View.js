{% autoescape None %}
cider.namespace('{{ namespace }}');

{{ namespace }}.{{ cls }} = cider.extend(cider.View);

{{ namespace }}.{{ cls }}.prototype.templateCode = '{{ template_code }}';