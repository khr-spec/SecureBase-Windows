# Billedbeviser · Modul 5

[Overblik](../../README.md) · [Til modulet](../../docs/05-registry.md) · [Alle beviser](../README.md)

**8 screenshots · Registry Editor · CLIENT01**

Billederne følger ændringerne fra før-tilstand til genoprettet hærdning.

| Nr. | Dokumenterer | Billede |
|---|---|---|
| 01 | Lokal labadmin; NoDriveTypeAutoRun findes ikke ved opslaget, og DontDisplayLastUserName er 0 | [Åbn 01](01-client01-registry-foer.png) |
| 02 | Policies-grenen eksporteres før ændring; before-policies.reg findes på CLIENT01 | [Åbn 02](02-registry-foer-eksport.png) |
| 03 | NoDriveTypeAutoRun vises som DWORD 0x000000ff (255) i Registry Editor | [Åbn 03](03-autorun-registry-editor.png) |
| 04 | DontDisplayLastUserName vises som DWORD 0x00000001 (1) | [Åbn 04](04-skjul-brugernavn-registry-editor.png) |
| 05 | Begge værdier kontrolleres; før- og efter-eksporten vises i samme mappe | [Åbn 05](05-vaerdier-og-efter-eksport.png) |
| 06 | Efter log af vises Other user og et tomt brugernavnsfelt | [Åbn 06](06-login-uden-seneste-brugernavn.png) |
| 07 | Rollback-kommandoerne udføres og melder succes | [Åbn 07](07-rollback-kommandoer.png) |
| 08 | Hærdningen genskabes; 0xff og 0x1 verificeres; after-policies.reg opdateres | [Åbn 08](08-sluttilstand-og-ny-efter-eksport.png) |

Billede 07 viser tilbageførsel; billede 08 viser slutkontrollen med **0xff og 0x1**. Eksportkommandoerne er dokumenteret i billede 02, 05 og 08.

---

[Tilbage til Modul 5 →](../../docs/05-registry.md)
