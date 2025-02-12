Ci sono dei problemi con le porte che espone tempo.

Quali cazzo deve usare????



Questo viene dall'altro repo
otlphttp/traces:
    endpoint: http://localhost:4418
    tls:
      insecure: true


Forse tempo ha due porte
- interfacia per le sue api e interrogazioni -> la devo dare a grafana
- potra per protocollo oltp -> ci devo fare il binding, la devo dare ad otel