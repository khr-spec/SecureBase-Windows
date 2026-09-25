# SecureBase Windows

**Kasper Â· Windows OS intro Â· September 2026**

## Design og drift af et lille Active Directory-miljÃ¸

Jeg har opbygget et isoleret Windows-lab med en domÃ¦necontroller og en klient. Afleveringen viser opsÃ¦tning, sikkerhedsvalg og resultater fra netvÃ¦rk og Active Directory til automatisering og analyse af sikkerhedslogs.

[Moduler](#moduler) Â· [Billedbeviser](evidence/README.md) Â· [PowerShell-script](scripts/README.md)

## Moduler

| Modul | Arbejde og dokumentation |
|---|---|
| [01 Â· VM og netvÃ¦rk](docs/01-vm-netvaerk.md) | Isoleret labnet, IP-plan, hostnames og forbindelsestest |
| [02 Â· Active Directory](docs/02-active-directory.md) | DomÃ¦ne, OU-struktur, brugere, grupper og klienttilknytning |
| [03 Â· Group Policy](docs/03-group-policy.md) | Password- og lockout-politik samt en mÃ¥lrettet brugerpolitik |
| [04 Â· PowerShell](docs/04-powershell.md) | Kommenteret script, brugeroprettelse og verificeret genkÃ¸rsel |
| [05 Â· Registry Editor](docs/05-registry.md) | To sikkerhedsÃ¦ndringer med fÃ¸r/efter-kontrol og tilbagefÃ¸rsel |
| [06 Â· Event Viewer](docs/06-event-viewer.md) | Central audit, hÃ¦ndelsesanalyse og overvÃ¥gningsbegrundelser |

## LabmiljÃ¸

| Maskine | System og funktion | IPv4 |
|---|---|---|
| **DC01** | Windows Server 2025 Standard Evaluation Â· AD DS, DNS og Global Catalog | `192.168.50.10/24` |
| **CLIENT01** | Windows 11 Enterprise Evaluation Â· domÃ¦neklient | `192.168.50.20/24` |

**DomÃ¦ne:** `securebase.local` Â· **NetBIOS:** `SECUREBASE`
**NetvÃ¦rk:** VirtualBox Internal Network Â· `labnet-khr`

## Dokumentation og kode

Hvert modul samler fremgangsmÃ¥de, sikkerhedsbegrundelser og testresultater. De centrale screenshots vises i teksten; alle **85 billedbeviser** kan Ã¥bnes fra de tilhÃ¸rende oversigter.

[Se alle billedbeviser â†’](evidence/README.md)
[LÃ¦s scriptet og kÃ¸rselsvejledningen â†’](scripts/README.md)
[Se Event ID-oversigten â†’](docs/06-event-viewer.md#event-id-oversigt)

---

*SecureBase Windows Â· Afleveringsudgave 1.1*
