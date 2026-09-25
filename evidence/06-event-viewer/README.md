# Billedbeviser · Modul 6

[Overblik](../../README.md) · [Til modulet](../../docs/06-event-viewer.md) · [Alle beviser](../README.md)

**26 screenshots · Event Viewer og logning · 25. september 2026**

Billederne er samlet efter konfiguration, hændelsestype og oprydning.

## GPO og effektiv audit

| Nr. | Dokumenterer | Billede |
|---|---|---|
| 01 | DC01 · Audit-GPO linket til securebase.local | [Åbn 01](01-audit-gpo-link.png) |
| 02 | Audit Logon: Success and Failure | [Åbn 02](02-audit-logon.png) |
| 03 | Audit User Account Management: Success | [Åbn 03](03-audit-user-account-management.png) |
| 04 | Begge Account Management-underkategorier: Success | [Åbn 04](04-audit-security-group-management.png) |
| 05 | Audit File System: Success and Failure i GPO-editoren | [Åbn 05](05-audit-file-system.png) |
| 06 | DC01 · gpupdate og alle fire effektive audit-underkategorier | [Åbn 06](06-dc01-effektiv-auditpolitik.png) |
| 07 | Mellemtrin · File System er endnu No Auditing på CLIENT01 | [Åbn 07](07-client01-foer-gpupdate.png) |
| 08 | CLIENT01 · GPO anvendt; File System er nu Success and Failure | [Åbn 08](08-client01-gpo-og-file-system.png) |

## Login og domæneforbindelse

| Nr. | Dokumenterer | Billede |
|---|---|---|
| 09 | Supplerende oversigt med 4624, 4625 og 4648; ingen fulde 4648-felter | [Åbn 09](09-logon-eventoversigt.png) |
| 10 | 4625 · ejensen · Type 2 · forkert password, SubStatus 0xC000006A | [Åbn 10](10-event-4625-fejlet-login.png) |
| 11 | 4624 · SECUREBASE\ejensen · Logon Type 11, CachedInteractive | [Åbn 11](11-event-4624-cached-login.png) |
| 12 | DC01 findes; Test-ComputerSecureChannel returnerer True | [Åbn 12](12-client01-dc-og-secure-channel.png) |
| 13 | Læsende hændelsesudtræk for ejensen: Type 7 og Type 11 | [Åbn 13](13-ejensen-logontyper.png) |

## Testkonto og gruppemedlemskab

| Nr. | Dokumenterer | Billede |
|---|---|---|
| 14 | DC01 · testbruger Audit Test i IT-OU | [Åbn 14](14-audittest-oprettet.png) |
| 15 | DL_Audit_Test sammen med eksisterende grupper | [Åbn 15](15-domain-local-testgruppe.png) |
| 16 | Audit Test er medlem af DL_Audit_Test | [Åbn 16](16-testgruppe-medlem.png) |
| 17 | 4720 · Administrator opretter audittest på DC01 | [Åbn 17](17-event-4720-ny-konto.png) |
| 18 | 4732 · audittest tilføjes DL_Audit_Test på DC01 | [Åbn 18](18-event-4732-gruppemedlem.png) |

## Objektadgang

| Nr. | Dokumenterer | Billede |
|---|---|---|
| 19 | Mellemtrin · dialog for mappen med This folder only; ikke den efterfølgende fil-SACL | [Åbn 19](19-sacl-mappe-mellemtrin.png) |
| 20 | Auditing Entry for test · ejensen · Success · Read og Read & execute | [Åbn 20](20-sacl-testfil.png) |
| 21 | Testfilen åbnet i Notepad; kontonavnet fremgår ikke af selve billedet | [Åbn 21](21-testfil-aabnet.png) |
| 22 | 4663 · ejensen → C:\AuditTest\test.txt · explorer.exe · ReadAttributes / 0x80 | [Åbn 22](22-event-4663-readattributes.png) |

## Slutkontrol og oprydning

| Nr. | Dokumenterer | Billede |
|---|---|---|
| 23 | DC01 · Audit Policy står under Applied Group Policy Objects | [Åbn 23](23-dc01-gpresult-slutkontrol.png) |
| 24 | IT-OU efter sletning af Audit Test; Emil Jensen er bevaret | [Åbn 24](24-oprydning-it-ou.png) |
| 25 | Groups efter sletning af DL_Audit_Test; de fire GG-grupper er bevaret | [Åbn 25](25-oprydning-testgruppe.png) |
| 26 | CLIENT01 · Test-Path C:\AuditTest returnerer False efter oprydning | [Åbn 26](26-oprydning-testmappe.png) |

---

[Tilbage til Modul 6 →](../../docs/06-event-viewer.md)
