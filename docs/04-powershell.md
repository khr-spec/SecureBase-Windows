# Modul 4: Command Line og PowerShell

[Overblik](../README.md) · [← Modul 3](03-group-policy.md) · [Billedbeviser](../evidence/04-powershell/README.md) · [Modul 5 →](05-registry.md)

> **DC01** · En ny afdeling oprettet med et kommenteret script og kontrolleret ved genkørsel.

## Formål

At automatisere oprettelse af en OU, brugere og en sikkerhedsgruppe samt kontrollere, at eksisterende objekter genbruges ved en ny kørsel.

## Udførte opgaver

Scriptet **New-SecureBaseSupport.ps1** blev oprettet på DC01. PowerShell-parseren fandt ingen syntaksfejl, og de eksisterende OU’er `SecureBase` og `Groups` blev kontrolleret før kørslen.

| Objekt | Placering / medlemskab |
|---|---|
| Support-OU | Under `SecureBase` |
| `GG_Support_Users` | Global sikkerhedsgruppe i `SecureBase/Groups` |
| Nora Hansen (`nhansen`) | Support; medlem af `GG_Support_Users` |
| Oliver Madsen (`omadsen`) | Support; medlem af `GG_Support_Users` |
| Freja Thomsen (`fthomsen`) | Support; medlem af `GG_Support_Users` |

Første kørsel oprettede objekterne. Resultatet blev kontrolleret med `Get-ADUser`, `Get-ADGroupMember` og ADUC. Anden kørsel fandt objekterne og medlemskaberne som eksisterende.

### Script og kørsel

[Åbn kildekoden og den samlede kørselsvejledning →](../scripts/README.md)

Den dokumenterede kørsel på DC01 var:

```powershell
& "C:\SecureBaseScripts\New-SecureBaseSupport.ps1"
```

Scriptet kræver ActiveDirectory-modulet, oprettelsesrettigheder og de to eksisterende OU’er. Det læser et midlertidigt password interaktivt med `Read-Host -AsSecureString`. Nye konti oprettes med krav om passwordskift ved næste login.

## Sikkerhedsmæssig begrundelse

Brugerne defineres i én liste, så samme kode opretter deres egenskaber og gruppemedlemskaber. Kontrol før oprettelse reducerer fejl ved gentagen kørsel.

Support blev valgt som en ny afdeling, så den manuelle opsætning fra Modul 2 forblev urørt. Scriptet tildeler afdelingsmedlemskab, ikke administratorrettigheder. Passwordet er ikke indskrevet i kildekoden eller vist i klartekst i kørselsbeviserne.

## Dokumentation / bevis

### Kontrol af oprettede objekter

```powershell
Get-ADUser `
  -SearchBase "OU=Support,OU=SecureBase,DC=securebase,DC=local" `
  -Filter * |
Select-Object Name,SamAccountName,Enabled

Get-ADGroupMember "GG_Support_Users" |
Select-Object Name,SamAccountName
```

![De tre Support-brugere og deres gruppemedlemskab](../evidence/04-powershell/04-ad-verification.png)

*Alle tre konti er Enabled = True og medlemmer af GG_Support_Users.*

### Første kørsel og genkørsel

![Første kørsel opretter OU, gruppe og brugere](../evidence/04-powershell/03-first-script-run.png)

*CREATED angiver oprettelser; ADDED angiver nye gruppemedlemskaber.*

![Genkørsel finder eksisterende objekter](../evidence/04-powershell/05-second-script-run.png)

*Anden kørsel viser EXISTS for OU, gruppe, brugere og medlemskaber.*

| Supplerende bevis | Indhold |
|---|---|
| [Før-billede](../evidence/04-powershell/01-before-support-ou.png) | ADUC uden Support-OU |
| [Syntaks og forudsætninger](../evidence/04-powershell/02-syntax-prerequisites.png) | Ingen parserfejl; nødvendige OU’er findes |
| [Support i ADUC](../evidence/04-powershell/06-support-ou-users.png) | Nora, Oliver og Freja i den nye OU |
| [Support-gruppen](../evidence/04-powershell/07-support-group.png) | Den nye gruppe sammen med de øvrige afdelingsgrupper |

## Overvejelser og fravalg

Scriptet er afgrænset til dette lab. Fejlhåndteringen består af kontrol af eksisterende objekter og medlemskaber; den dokumenterede genkørsel er ikke en test af alle forbindelses- eller rettighedsfejl.

Der spørges også efter et password ved genkørsel. Når kontiene allerede findes, anvendes det ikke til at ændre deres passwords. Denne adfærd er bevaret i den afprøvede scriptfil.

## Resultat

PowerShell har oprettet én OU, én sikkerhedsgruppe og tre brugere med de ønskede medlemskaber. Verifikationsoutput og genkørsel er dokumenteret, og den fulde kommenterede kildekode følger med.

---

[← Modul 3](03-group-policy.md) · [Alle 7 billeder](../evidence/04-powershell/README.md) · [Modul 5 →](05-registry.md)
