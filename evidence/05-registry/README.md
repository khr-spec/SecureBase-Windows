# Billedbeviser · Modul 5

[Overblik](../../README.md) · [Til modulet](../../docs/05-registry.md) · [Alle beviser](../README.md)

**8 screenshots · Registry Editor · CLIENT01**

Klik på et billedlink for originalen. Billederne er bevaret uændret og følger forløbet fra før-tilstand til den afsluttende genoprettelse.

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

## Eksporter og sluttilstand

`before-policies.reg` og `after-policies.reg` er dokumenteret på CLIENT01 i `C:\SecureBaseRegistry`. De originale eksportfiler er ikke vedlagt vaulten; deres oprettelse og de relevante værdier vises i billederne.

Billede 07 viser udført rollback, ikke sluttilstanden. Billede 08 viser genoprettelsen og den endelige kontrol: **NoDriveTypeAutoRun = 0xff** og **DontDisplayLastUserName = 0x1**.

---

[Tilbage til Modul 5 →](../../docs/05-registry.md)
