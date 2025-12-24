# 🔮 Privalyse Next-Gen Roadmap

Hier definieren wir die Zukunft von Privacy-AI. Weg von "Tools", hin zu "Platform".

## A) Risiko-gesteuerte Generalisierung (Adaptive Privacy)
*Status: Visionär*
Aktuell sind unsere Regeln statisch (Stadt bleibt immer).
**Next Level:** Dynamische Entscheidung basierend auf Re-Identifikations-Risiko.
- **Idee**: Ist "Springfield" ein 500-Seelen-Dorf? -> Maskiere zu `{Region_US_Midwest}`. Ist es "New York"? -> Bleibt "New York".
- **Tech**: Benötigt Geo-Datenbank / Lookup-Table für Populationsdichte oder Häufigkeit von Namen.
- **Mehrwert**: Maximale Utility bei garantiertem k-Anonymity Level.

## B) Scope-Determinismus (Lifecycle Management)
*Status: Operational Excellence*
Aktuell nutzen wir `seed` manuell.
**Next Level:** Automatische Verwaltung von Scopes.
- **Idee**: `masker.set_scope("session_123")` oder `masker.rotate_keys(frequency="daily")`.
- **Feature**: "Private Memory" -> Ein Agent erinnert sich an `{Name_X}` über mehrere Tage, aber ein anderer Agent (oder Admin) kann es nicht auflösen.
- **Mehrwert**: Sicherheit durch "Key Rotation" und strikte Datentrennung zwischen Mandanten/Usern.

## C) Output-Policy Enforcement (Granular Unmasking)
*Status: Enterprise Governance*
Aktuell ist `unmask` ein "Alles oder Nichts".
**Next Level**: Role-Based Unmasking.
- **Idee**: Der Support-Agent darf den Namen sehen, aber nicht die IBAN. Der Finance-Bot darf die IBAN sehen, aber nicht den Namen.
- **Tech**: `unmask(text, mapping, role="support")` -> Filtert Mapping basierend auf Policies.
- **Mehrwert**: Zero-Trust Architecture bis zum End-User.

## D) Eval Harness "Utility vs Privacy" (The Proof)
*Status: Game Changer (Market Differentiator)*
Alle behaupten "es funktioniert". Wir messen es.
**Next Level**: Automatisierte Benchmark-Suite.
- **Metrik 1: Privacy Score**: Wie viel PII ist *wirklich* weg? (Presidio Recall/Precision).
- **Metrik 2: Utility Score**: Löst das LLM die Aufgabe trotz Maskierung? (Task Success Rate).
- **Szenarien**:
    1.  **RAG**: Findet das LLM das richtige Dokument basierend auf `{Date_October_2000}`?
    2.  **Support**: Kann das LLM empathisch antworten ("Hallo {Name_X}")?
    3.  **Extraction**: Extrahiert es die korrekten Entitäten?
