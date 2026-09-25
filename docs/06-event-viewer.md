# Modul 6: Event Viewer og logning

[Overblik](../README.md) · [← Modul 5](05-registry.md) · [Billedbeviser](../evidence/06-event-viewer/README.md)

> **DC01 og CLIENT01 · 25. september 2026** · Central audit og analyse af login, kontoændringer og filadgang.

## Formål

At konfigurere relevant audit-logning, fremkalde kontrollerede hændelser og bruge Event Viewer til at identificere aktør, handling og berørt objekt.

## Udførte opgaver

### Central auditpolitik

GPO’en **SecureBase - Audit Policy** blev linket til `securebase.local`. Under **Computer Configuration → Policies → Windows Settings → Security Settings → Advanced Audit Policy Configuration → Audit Policies** blev følgende konfigureret:

| Kategori | Underkategori | Audit |
|---|---|---|
| Logon/Logoff | Audit Logon | Success and Failure |
| Account Management | Audit User Account Management | Success |
| Account Management | Audit Security Group Management | Success |
| Object Access | Audit File System | Success and Failure |

`gpresult` og `auditpol` blev brugt til at kontrollere anvendelsen på begge VM’er. CLIENT01 viste først File System som **No Auditing**; efter en ny computerpolitik-opdatering viste kontrollen **Success and Failure**.

### Testhandlinger

| Maskine | Handling | Hændelse |
|---|---|---|
| CLIENT01 | Ét forkert password for `ejensen` | 4625 |
| CLIENT01 | Vellykket login for `ejensen` | 4624, Type 11 |
| DC01 | Oprettelse af `audittest` i IT-OU’en | 4720 |
| DC01 | `audittest` tilføjet til `DL_Audit_Test` | 4732 |
| CLIENT01 | Adgang til `C:\AuditTest\test.txt` | 4663, ReadAttributes |

Testgruppen var **Domain local / Security**. På testfilen blev der oprettet en **SACL** for `ejensen` med Success og Read/Read & execute. Efter øvelsen blev testbrugeren, testgruppen og testmappen fjernet, mens audit-GPO’en blev bevaret.

## Sikkerhedsmæssig begrundelse

Central auditstyring gør konfigurationen ensartet, mens efterkontrol viser, hvad der faktisk gælder på hver maskine. De konkrete events binder handlinger til konti, objekter og tidspunkter.

Testene blev afgrænset til ét forkert login, særskilte AD-testobjekter og én testfil. SACL’en styrer logning af den valgte adgang; den giver ikke brugeren flere filrettigheder. [Microsoft: Audit File System](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-file-system).

### Event ID-oversigt

| Event ID | Betydning | Hvorfor overvåge |
|---|---|---|
| **4624** | En logonsession er oprettet | Sammenhold konto, tidspunkt, maskine og Logon Type med forventet brug. |
| **4625** | Et loginforsøg mislykkedes | Gentagne fejl kan pege på passwordgæt eller kontoproblemer; fejlårsagen hjælper analysen. |
| **4720** | En brugerkonto blev oprettet | Nye konti bør kunne forbindes med en forventet administrationshandling og en kendt aktør. |
| **4732** | Medlem tilføjet til en lokal/domain-local sikkerhedsgruppe | Uventede medlemskaber kan ændre adgang, afhængigt af gruppens rettigheder. |
| **4663** | En adgangsrettighed blev brugt på et auditeret objekt | Konto, filsti, proces og Accesses viser, hvilken adgang der faktisk blev registreret. |

En hændelse vurderes ud fra sin sammenhæng; et enkelt Event ID er ikke i sig selv bevis på et angreb.

## Dokumentation / bevis

### GPO og effektive auditindstillinger

Kontrollen blev udført med administratorrettigheder på **begge VM’er**:

```powershell
gpupdate /target:computer /force
gpresult /scope computer /r

auditpol /get /subcategory:"Logon"
auditpol /get /subcategory:"User Account Management"
auditpol /get /subcategory:"Security Group Management"
auditpol /get /subcategory:"File System"
```

| Kontrol | Observeret resultat | Bevis |
|---|---|---|
| DC01 | De fire underkategorier svarer til den valgte konfiguration | [auditpol](../evidence/06-event-viewer/06-dc01-effektiv-auditpolitik.png) |
| CLIENT01 | Audit-GPO anvendt; File System er Success and Failure efter opdatering | [gpresult og auditpol](../evidence/06-event-viewer/08-client01-gpo-og-file-system.png) |
| DC01, afsluttende kontrol | Audit-GPO under Applied Group Policy Objects | [gpresult](../evidence/06-event-viewer/23-dc01-gpresult-slutkontrol.png) |

### Login: 4625 og 4624

I **Event Viewer → Windows Logs → Security** blev loggen filtreret på loginhændelser for `ejensen`. Tidspunkterne er aflæst i VM’ens visning den 25. september 2026.

| Event | Tidspunkt | Centrale felter | Bevis |
|---|---|---|---|
| 4625 | 09:56:55 | `ejensen`, Type 2, Status `0xC000006D`, SubStatus `0xC000006A` | [Mislykket login](../evidence/06-event-viewer/10-event-4625-fejlet-login.png) |
| 4624 | 09:57:04 | `SECUREBASE\ejensen`, Type 11, Elevated Token: No | [Vellykket login](../evidence/06-event-viewer/11-event-4624-cached-login.png) |

![Mislykket login for ejensen](../evidence/06-event-viewer/10-event-4625-fejlet-login.png)

*Account For Which Logon Failed viser ejensen. SubStatus 0xC000006A angiver forkert password; Subject er den proces-/systemkontekst, der rapporterer hændelsen.*

Det vellykkede login er **CachedInteractive, Type 11**: der blev brugt lokalt cachede domæneoplysninger. Den efterfølgende [secure-channel-kontrol](../evidence/06-event-viewer/12-client01-dc-og-secure-channel.png) returnerede True og fandt DC01; det er et separat forbindelsesbevis, ikke en ændring af logontypen. [Oversigten over Type 7 og 11](../evidence/06-event-viewer/13-ejensen-logontyper.png) er bevaret som supplement.

### Konto og gruppe: 4720 og 4732

På DC01 blev Security-loggen filtreret på **4720,4732**.

| Event | Tidspunkt | Aktør | Handling | Bevis |
|---|---|---|---|---|
| 4720 | 10:14:16 | `SECUREBASE\Administrator` | Oprettede `audittest` | [Kontooprettelse](../evidence/06-event-viewer/17-event-4720-ny-konto.png) |
| 4732 | 10:15:50 | `SECUREBASE\Administrator` | Tilføjede `audittest` til `DL_Audit_Test` | [Gruppemedlemskab](../evidence/06-event-viewer/18-event-4732-gruppemedlem.png) |

![Tilføjelse af audittest til testgruppen](../evidence/06-event-viewer/18-event-4732-gruppemedlem.png)

*Hændelsen forbinder administratoren, medlemmet audittest og gruppen DL_Audit_Test. Gruppen er en Domain Local Security Group i AD.*

### Filadgang: 4663

[SACL’en på testfilen](../evidence/06-event-viewer/20-sacl-testfil.png) omfattede `ejensen`, Success og læsehandlinger. Filen blev åbnet, og den relevante 4663-hændelse blev undersøgt:

![Metadataadgang til test.txt](../evidence/06-event-viewer/22-event-4663-readattributes.png)

*SECUREBASE\ejensen → C:\AuditTest\test.txt · proces: explorer.exe · ReadAttributes · Access Mask: 0x80.*

**ReadAttributes dokumenterer metadataadgang**, ikke læsning af filens tekstindhold. Det er den konkrete registrerede handling i dette bevis. Der blev ikke udført en særskilt test af afvist filadgang.

### Oprydning

| Testobjekt | Slutkontrol |
|---|---|
| `audittest` | [IT-OU’en viser Emil Jensen uden testbrugeren](../evidence/06-event-viewer/24-oprydning-it-ou.png) |
| `DL_Audit_Test` | [Groups viser de fire afdelingsgrupper](../evidence/06-event-viewer/25-oprydning-testgruppe.png) |
| `C:\AuditTest` | [Test-Path returnerer False](../evidence/06-event-viewer/26-oprydning-testmappe.png) |

Audit-GPO’en blev bevaret. Da testfilen er fjernet, findes dens SACL ikke længere; audit af andre filer kræver passende audit-entries på de pågældende objekter.

## Overvejelser og fravalg

Den centrale GPO blev brugt frem for lokale audit-overstyringer. Testgruppen havde ingen tildelte administratorrettigheder, og cached login blev ikke deaktiveret for at fremtvinge en anden logontype.

Øvelsen dokumenterer de beskrevne audittests og oprydningen. Et separat forløb med en bevidst indbygget fejlkonfiguration (*mini-incident*) er ikke udført.

## Resultat

Login, kontoændringer, gruppemedlemskab og filadgang er knyttet til konkrete hændelser. Auditkonfigurationen er efterprøvet på DC01 og CLIENT01, og de midlertidige testobjekter er ryddet op.

**Tekniske referencer:** Microsofts beskrivelser af [4624](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4624), [4625](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625), [4720](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4720), [4732](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4732) og [4663](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4663).

---

[← Modul 5](05-registry.md) · [Alle 26 billeder](../evidence/06-event-viewer/README.md) · [Til overblikket →](../README.md)
