# Modul 2: Active Directory — struktur og opsætning

[Overblik](../README.md) · [← Modul 1](01-vm-netvaerk.md) · [Modul 3 →](03-group-policy.md)

> **Gennemført og dokumenteret** · DC01 og CLIENT01

## Formål

At etablere DC01 som domænecontroller og DNS-server samt opbygge en OU-, bruger-, gruppe- og klientstruktur til de efterfølgende moduler.

## Udførte opgaver

AD DS blev installeret på DC01. Serveren blev promoveret til første domænecontroller i en ny forest, hvorefter domæne, forest og tjenester blev kontrolleret med PowerShell.

### Domæneindstillinger

| Indstilling | Dokumenteret valg |
|---|---|
| Domæne og forest | `securebase.local` |
| NetBIOS-navn | `SECUREBASE` |
| Domænecontroller | `DC01.securebase.local` |
| Forest- og domain-functional level | Windows Server 2025 |
| DNS Server / Global Catalog | Aktiveret på DC01 |
| RODC / DNS delegation | Ikke valgt |
| AD-database og logfiler | `C:\WINDOWS\NTDS` |
| SYSVOL | `C:\WINDOWS\SYSVOL` |

Promotionens prerequisite check bestod. Efter genstart viste `Get-Service NTDS,DNS` begge tjenester som **Running**.

### AD-struktur ved afslutning af Modul 2

```text
securebase.local
└── SecureBase
    ├── IT
    │   └── Emil Jensen (ejensen)
    ├── Sales
    │   └── Sara Nielsen (snielsen)
    ├── Management
    │   └── Maja Larsen (mlarsen)
    ├── Groups
    │   ├── GG_IT_Users
    │   ├── GG_Sales_Users
    │   └── GG_Management_Users
    └── Workstations
        └── CLIENT01
```

Support-afdelingen tilføjes senere i [Modul 4](04-powershell.md). Figuren ovenfor viser den manuelle opsætning fra dette modul.

### OU → bruger → gruppe → begrundelse

| OU | Bruger / objekt | Gruppe | Begrundelse |
|---|---|---|---|
| IT | Emil Jensen (`ejensen`) | `GG_IT_Users` | Målretning af IT-afdelingens medlemskab og senere brugerpolitikker. |
| Sales | Sara Nielsen (`snielsen`) | `GG_Sales_Users` | Selvstændig organisering af salgsafdelingen. |
| Management | Maja Larsen (`mlarsen`) | `GG_Management_Users` | Logisk adskillelse af ledelsens brugere. |
| Groups | De tre globale sikkerhedsgrupper | — | Samlet administration af grupper til senere rettighedstildeling. |
| Workstations | CLIENT01 | — | Samlet placering af klientobjekter til senere computerpolitikker. |

### Klienttilknytning

På CLIENT01 blev forward-DNS-opslag og LDAP SRV-recorden kontrolleret før domænejoin. Klienten blev tilknyttet `securebase.local` og genstartet. Login med `SECUREBASE\ejensen` blev derefter verificeret. Computerobjektet CLIENT01 blev flyttet fra `Computers` til `SecureBase\Workstations`.

## Sikkerhedsmæssig begrundelse

**Navngivne konti og grupper.** Individuelle konti giver et grundlag for sporbarhed. Afdelingsgrupperne gør det muligt at tildele adgang gennem medlemskaber frem for særskilt til hver bruger. Gruppemedlemskaberne er dokumenteret; der er ikke i dette modul dokumenteret adgang til en bestemt filshare eller applikation.

**OU-struktur.** En separat SecureBase-OU samler labobjekterne uden at blande dem med Windows’ standardcontainere. Afdelinger og klientobjekter har hver deres placering til senere politikstyring.

**DNS før join.** CLIENT01 blev kontrolleret mod DC01 som DNS-server, før domænetilknytningen blev gennemført. Det giver særskilte beviser for DNS-opslag og det efterfølgende domænelogin.

## Dokumentation / bevis

### Kontroller og resultater

| Kontrol | Observeret resultat | Bevis |
|---|---|---|
| Promotion | Prerequisite check bestod | [Prerequisites](../evidence/02-active-directory/07-prerequisites-passed.png) |
| Domæne og tjenester | `securebase.local`; DNS og NTDS Running | [PowerShell-kontrol](../evidence/02-active-directory/09-domain-forest-services.png) |
| Afdelingsbrugere | Én bruger i hver afdelings-OU | [IT](../evidence/02-active-directory/13-user-emil-it.png) · [Sales](../evidence/02-active-directory/14-user-sara-sales.png) · [Management](../evidence/02-active-directory/15-user-maja-management.png) |
| Gruppemedlemskab | Korrekt bruger i hver af de tre grupper | [Medlemskabstabel](../evidence/02-active-directory/21-group-membership-verification.png) |
| Forward-DNS | Domænet og DC01 returnerer `192.168.50.10` | [DNS-opslag](../evidence/02-active-directory/16-client-dns-lookups.png) |
| AD-SRV | DC01 på port 389, adresse `192.168.50.10` | [SRV-opslag](../evidence/02-active-directory/17-ad-srv-record.png) |
| Domænelogin | `securebase\ejensen` på CLIENT01 | [Loginverifikation](../evidence/02-active-directory/19-domain-login-verification.png) |
| Computerobjekt | CLIENT01 i Workstations | [ADUC-placering](../evidence/02-active-directory/20-client01-workstations-ou.png) |

### Samlet ADUC-overblik

![Afsluttende ADUC-struktur](../evidence/02-active-directory/22-final-aduc-structure.png)

*SecureBase med Groups, IT, Management, Sales og Workstations. Brugerne og medlemskaberne fremgår af de tilhørende beviser i tabellen.*

### Gruppemedlemskab og domænelogin

![Tre grupper med deres respektive brugere](../evidence/02-active-directory/21-group-membership-verification.png)

*Entydig PowerShell-visning af gruppe, navn og logonnavn.*

![Domænelogin på CLIENT01](../evidence/02-active-directory/19-domain-login-verification.png)

*`whoami`, `hostname`, `USERDOMAIN` og `USERDNSDOMAIN` efter domænelogin.*

[Åbn hele bevisoversigten — 22 screenshots →](../evidence/02-active-directory/README.md)

## Overvejelser og fravalg

**Én forest og ét domæne.** Der blev ikke tilføjet flere domæner til det lille lab. DC01 er den eneste domænecontroller, og RODC blev derfor fravalgt.

**Stier og delegation.** Standardplaceringerne for NTDS og SYSVOL blev bevaret. DNS-delegation blev ikke oprettet i den nye isolerede forest. Wizarden viste en delegation-advarsel, men prerequisite check bestod.

**DNS-observation.** `nslookup` viste først en timeout og `Server: Unknown`, men returnerede derefter de forventede adresser. Den præcise årsag til den indledende besked blev ikke undersøgt særskilt. SRV-opslag og efterfølgende domænelogin lykkedes og er dokumenteret separat.

## Status

- [x] Ny forest og domæne `securebase.local` etableret.
- [x] DC01 verificeret som domænecontroller med DNS og Global Catalog.
- [x] Tre afdelings-OU’er samt Groups og Workstations oprettet.
- [x] Tre brugere og tre sikkerhedsgrupper oprettet; medlemskaber verificeret.
- [x] CLIENT01 tilknyttet domænet og placeret i Workstations.
- [x] Login med en domænebruger dokumenteret.
- [x] ADUC-bevis og skemaet OU → bruger → gruppe → begrundelse samlet.

**Modul 2 er gennemført og dokumenteret.**

---

[Overblik](../README.md) · [← Modul 1](01-vm-netvaerk.md) · [Modul 3 →](03-group-policy.md)
