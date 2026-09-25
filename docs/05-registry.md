# Modul 5: Registry Editor

[Overblik](../README.md) · [← Modul 4](04-powershell.md) · [Modul 6 →](06-event-viewer.md)

> **Gennemført og dokumenteret** · CLIENT01 · 23. september 2026  
> To afgrænsede ændringer, før/efter-eksport og verificeret sluttilstand.

## Formål

At foretage kontrollerede sikkerhedsændringer i Windows Registry, dokumentere før- og eftertilstanden og beskrive, hvordan ændringerne kan tilbageføres uden at berøre uvedkommende indstillinger.

## Udførte opgaver

Arbejdet blev udført på **CLIENT01**, logget ind som den lokale konto `CLIENT01\labadmin` med en administratoråbnet PowerShell. DC01 blev ikke ændret i dette modul. De to værdier blev først undersøgt, og den relevante Policies-gren blev eksporteret, før ændringerne blev foretaget manuelt i Registry Editor.

| Værdi | Type | Observeret før | Verificeret sluttilstand |
|---|---|---|---|
| `NoDriveTypeAutoRun` | `REG_DWORD` | Ikke fundet ved opslaget | `0xff` / 255 |
| `DontDisplayLastUserName` | `REG_DWORD` | `0x0` | `0x1` |

### De to ændringer

**AutoRun for alle drevtyper.** Under følgende nøgle blev værdien `NoDriveTypeAutoRun` oprettet som **DWORD (32-bit)** og sat til **ff** med Hexadecimal valgt:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer
```

**Skjul seneste brugernavn.** Den eksisterende værdi `DontDisplayLastUserName` blev ændret fra **0** til **1** under:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
```

Efter ændringerne blev værdierne kontrolleret med `reg query`, og der blev lavet en efter-eksport. Ved log af blev den synlige effekt af brugernavnsindstillingen kontrolleret. Rollback-kommandoerne blev efterfølgende udført; derefter blev **begge hærdningsværdier sat tilbage til 0xff og 0x1**, kontrolleret igen og efter-eksporten opdateret.

## Sikkerhedsmæssig begrundelse

**Afgrænset mediepolitik.** `NoDriveTypeAutoRun=0xff` er den valgte AutoRun-relaterede indstilling for alle drevtyper. Microsoft beskriver denne værdi under politikken *Turn off AutoPlay*. Formålet er at begrænse automatisk behandling ved indsættelse af medier; dette modul dokumenterer den konkrete registry-værdi, ikke en fuld test af alle medietyper. [Microsofts beskrivelse af indstillingen](https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/issues-autoplay-disabled-group-policy).

**Mindre information på login-skærmen.** Med `DontDisplayLastUserName=1` vises den senest indloggede konto ikke som en forudfyldt loginidentitet. Det reducerer den information om kontonavne, som kan aflæses ved konsollen. Indstillingen erstatter ikke passwordkrav eller adgangskontrol. [Microsofts beskrivelse af loginpolitikken](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/interactive-logon-do-not-display-last-user-name).

**Kontrol før og efter.** Ændringerne er begrænset til to navngivne værdier på klienten. Før-eksporten dokumenterer udgangspunktet, mens efter-eksport og læsende opslag dokumenterer den ønskede konfiguration. Der blev ikke slettet en hel policy-gren eller ændret firewallregler i dette forløb.

## Dokumentation / bevis

### Før-tilstand

![Lokal administrator og registry-værdier før ændringerne](../evidence/05-registry/01-client01-registry-foer.png)

*På CLIENT01 viser whoami den lokale konto labadmin. Opslaget efter NoDriveTypeAutoRun finder ikke den angivne nøgle eller værdi; DontDisplayLastUserName returneres som DWORD 0x0.*

**Før — forkortet afskrift af opslagene:**

```text
NoDriveTypeAutoRun:
ERROR: The system was unable to find the specified registry key or value.

DontDisplayLastUserName    REG_DWORD    0x0
```

At en eksplicit værdi ikke blev fundet, dokumenterer ikke i sig selv, hvordan alle medier blev behandlet før ændringen.

### Før- og efter-eksport

Policies-grenen blev eksporteret med disse kommandoer **før** og **efter** ændringerne. Den sidste kommando blev gentaget efter genoprettelsen af hærdningen:

```powershell
# Før ændringerne — den oprindelige før-eksport bevares.
reg export "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies" "C:\SecureBaseRegistry\before-policies.reg" /y

# Efter ændringerne — opdateret igen efter rollback og genoprettelse.
reg export "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies" "C:\SecureBaseRegistry\after-policies.reg" /y
```

`reg export` skriver den valgte gren til en fil. `/y` tillader, at en eksisterende fil med samme navn overskrives; derfor blev før-eksporten ikke kørt igen efter ændringerne. [Microsoft: reg export](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-export).

| Eksport | Dokumenteret placering på CLIENT01 | Bevis |
|---|---|---|
| Før | `C:\SecureBaseRegistry\before-policies.reg` | [Før-eksport lykkes; filen findes](../evidence/05-registry/02-registry-foer-eksport.png) |
| Efter | `C:\SecureBaseRegistry\after-policies.reg` | [Før/efter-filer vises sammen](../evidence/05-registry/05-vaerdier-og-efter-eksport.png) · [Endelig efter-eksport lykkes](../evidence/05-registry/08-sluttilstand-og-ny-efter-eksport.png) |

**Eksportfilerne er oprettet på CLIENT01, men de originale `.reg`-filer er ikke vedlagt denne vault.** Før-/efterdokumentationen i pakken består af de faktiske screenshots og de viste nøgleoutput. Opgaven tillader screenshots af de ændrede nøgler som dokumentation.

### Slutkontrol — efter genoprettet hærdning

De læsende kontrolkommandoer var:

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun

reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v DontDisplayLastUserName
```

**Efter — forkortet afskrift af de verificerede værdier:**

```text
NoDriveTypeAutoRun         REG_DWORD    0xff
DontDisplayLastUserName    REG_DWORD    0x1
```

![Endelig genoprettelse af de to værdier, kontrol og efter-eksport](../evidence/05-registry/08-sluttilstand-og-ny-efter-eksport.png)

*Det afsluttende screenshot viser både rollback, genoprettelse, de to reg query-resultater og en vellykket opdatering af after-policies.reg. Slutværdierne er 0xff og 0x1 — ikke rollback-værdierne.*

### Funktionstest af login-skærmen

Efter den første ændring til `DontDisplayLastUserName=1` blev CLIENT01 logget af med `shutdown /l`. Login-skærmen viste derefter **Other user** med tomt brugernavnsfelt:

![Login-skærm uden den seneste brugers navn](../evidence/05-registry/06-login-uden-seneste-brugernavn.png)

*Seneste kontonavn vises ikke. Domænet SECUREBASE er fortsat synligt; testen dokumenterer skjult brugernavn, ikke skjult domæne eller fuld anonymisering.*

Den synlige test blev udført før rollback. Efter genoprettelsen er registry-værdien verificeret igen, men der er ikke et nyt login-screenshot fra netop den sidste genoprettelse. AutoRun-indstillingen er verificeret på registry-niveau; en særskilt funktionstest med eksternt medie er ikke dokumenteret.

### Supplerende beviser

| Bevis | Indhold |
|---|---|
| [AutoRun-værdi i Registry Editor](../evidence/05-registry/03-autorun-registry-editor.png) | NoDriveTypeAutoRun som DWORD 0x000000ff (255) |
| [Loginværdi i Registry Editor](../evidence/05-registry/04-skjul-brugernavn-registry-editor.png) | DontDisplayLastUserName som DWORD 0x00000001 (1) |
| [Første efter-kontrol](../evidence/05-registry/05-vaerdier-og-efter-eksport.png) | Værdier og eksporter kontrolleret før rollback |
| [Udført rollback](../evidence/05-registry/07-rollback-kommandoer.png) | De to tilbageførselskommandoer melder succes |

[Åbn hele bevisoversigten — 8 screenshots →](../evidence/05-registry/README.md)

## Overvejelser og fravalg

### Risiko og afgrænsning

En forkert nøgle, et forkert værdinavn eller et forkert talgrundlag kan give en anden konfiguration end den tilsigtede. Ved NoDriveTypeAutoRun skal **ff** bruges i hexadecimal eller **255** i decimal. Førværdier, fulde stier og efterfølgende opslag gør ændringen efterprøvbar.

Eksporten omfatter hele den valgte `Policies`-gren og dermed flere værdier end de to ændrede. En ukritisk import kan derfor også påvirke andre indstillinger i grenen. Til tilbageførsel af netop dette forløb blev de to værdier håndteret enkeltvis, mens selve Explorer- og System-nøglerne blev bevaret.

### Rollback — dokumentation af det udførte forløb

> **Ikke et næste trin.** Nedenstående kommandoer fjerner de to hærdningsændringer. De blev kørt under forløbet, men CLIENT01 skal efterlades med de verificerede slutværdier **0xff og 0x1**.

```powershell
# TILBAGEFØRSEL: slet kun den nye værdi, ikke Explorer-nøglen.
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /f

# TILBAGEFØRSEL: gendan den observerede førværdi 0.
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v DontDisplayLastUserName /t REG_DWORD /d 0 /f
```

Begge kommandoer meldte *The operation completed successfully*. Der blev ikke gemt særskilte `reg query`-resultater mellem rollback og genoprettelse. Beviset er derfor succesmeldingerne fra rollback-kommandoerne samt den efterfølgende, eksplicitte slutkontrol.

En almindelig import af før-eksporten er ikke det samme som at fjerne værdier, der er oprettet senere. `reg import` indlæser filens indhold; den nye NoDriveTypeAutoRun-værdi tilbageføres her ved en specifik sletning med `/v`, ikke ved at slette hele nøglen. [Microsoft: reg import](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-import) · [Microsoft: reg delete](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-delete).

### Genoprettelse af den ønskede sluttilstand

Efter rollback blev følgende kommandoer udført. De satte værdierne tilbage til den ønskede hærdning, hvorefter begge værdier blev læst og efter-eksporten opdateret:

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 255 /f

reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v DontDisplayLastUserName /t REG_DWORD /d 1 /f
```

Registry Editor blev valgt til den første ændring, fordi modulet handler om kontrolleret registry-redigering. Der blev ikke oprettet en ny GPO til disse to indstillinger. Ingen af kommandoerne i denne note skal køres for at åbne eller læse vaulten.

## Status

- [x] AutoRun-relateret policy sat til alle drevtyper med NoDriveTypeAutoRun = 0xff.
- [x] Ekstra sikkerhedsændring: DontDisplayLastUserName = 1.
- [x] Før/efter reg export udført på CLIENT01 og dokumenteret med screenshots.
- [x] Begge slutværdier verificeret med reg query efter genoprettelsen.
- [x] Skjult seneste brugernavn demonstreret på login-skærmen.
- [x] Sikkerhedsbegrundelser, risici og præcis tilbageførsel dokumenteret.
- [x] Rollback-kommandoer og genoprettet hærdning er tydeligt adskilt.

**Modul 5 er gennemført og dokumenteret.** Audit og hændelsesanalyse følger i [Modul 6](06-event-viewer.md).

---

[Overblik](../README.md) · [← Modul 4](04-powershell.md) · [Modul 6 →](06-event-viewer.md)
