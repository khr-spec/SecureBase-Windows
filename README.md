# SecureBase Windows

*Windows OS intro · Active Directory-lab · Kasper*

> **6 af 6 moduler er gennemført og dokumenteret.**  
> Samlet aflevering · 25. september 2026 · Konfiguration, testbeviser og afgrænsninger samlet modul for modul.

Et isoleret Windows-lab med domænecontrolleren **DC01** og klienten **CLIENT01**. Forløbet går fra netværksopsætning og Active Directory til Group Policy, PowerShell-automatisering, registry-ændringer og analyse af sikkerhedslogs.

## Moduler

| Modul | Indhold | Status |
|---|---|---|
| [01 · VM og netværk](docs/01-vm-netvaerk.md) | IP-plan, netværkstest og Guest Additions | **Gennemført** |
| [02 · Active Directory](docs/02-active-directory.md) | Domæne, OU’er, grupper og domænelogin | **Gennemført** |
| [03 · Group Policy](docs/03-group-policy.md) | Passwordpolitik, lockout og klienttest | **Gennemført** |
| [04 · PowerShell](docs/04-powershell.md) | Support-afdeling oprettet med script | **Gennemført** |
| [05 · Registry Editor](docs/05-registry.md) | To sikkerhedsændringer, før/efter og rollback | **Gennemført** |
| [06 · Event Viewer](docs/06-event-viewer.md) | Audit-GPO, fem Event ID’er og oprydning | **Gennemført** |

## Lab i korte træk

| Maskine | System og rolle | IPv4 |
|---|---|---|
| **DC01** | Windows Server 2025 Standard Evaluation · AD DS og DNS | `192.168.50.10/24` |
| **CLIENT01** | Windows 11 Enterprise Evaluation · domæneklient | `192.168.50.20/24` |

**Domæne:** `securebase.local` · **NetBIOS:** `SECUREBASE`  
**VirtualBox-netværk:** `labnet-khr` · **Type:** Internal Network

Modulernes billeder viser tilstanden på testtidspunktet. Support-afdelingen tilføjes i Modul 4. Audit-testbrugeren, testgruppen og testmappen fra Modul 6 er efterfølgende ryddet op; audit-GPO’en er bevaret i det dokumenterede forløb.

## Dokumentation og kildekode

[Se alle 85 billedbeviser →](evidence/README.md)  
[Åbn PowerShell-script og kørselsvejledning →](scripts/README.md)  
[Se Event ID-oversigt og overvågningsbegrundelser →](docs/06-event-viewer.md#event-id-oversigt)

Hvert modul samler formål, udførte opgaver, sikkerhedsbegrundelse, beviser, fravalg og status. Billederne kan åbnes i original størrelse via bevisoversigterne. De tekniske fortolkninger i Modul 5 og 6 har links til Microsofts dokumentation; screenshots er beviset for, hvad der blev observeret i labbet.

## Afleveringsgrundlag

Status dækker de seks modulers konkrete opgaver og dokumentationskrav i **Windows OS intro**. Testenes afgrænsninger står i det relevante modul: eksempelvis cached login i Modul 6 og registry-kontrol uden en særskilt medietest i Modul 5. Der er ikke udført en ny samlet geninstallation eller sluttest af alle tidligere indstillinger ved denne samling.

De originale `.reg`-eksporter fra CLIENT01 og rå `.evtx`-logs er ikke vedlagt. Før/efter-værdier og de relevante hændelser er dokumenteret med screenshots; der er ikke konstrueret erstatningsfiler. Opgavens særskilte læringsmål om en **bevidst indbygget mini-incident** er ikke dokumenteret som et selvstændigt øvelsesforløb.

---

*Slutudgave 1.0 · Modul 1–6 · Dokumenteret arbejde, ikke en generel produktionsbaseline.*
