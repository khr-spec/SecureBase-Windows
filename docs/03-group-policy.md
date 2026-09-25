# Modul 3: Group Policy

[Overblik](../README.md) · [← Modul 2](02-active-directory.md) · [Billedbeviser](../evidence/03-group-policy/README.md) · [Modul 4 →](04-powershell.md)

> **DC01 og CLIENT01** · Domænepolitik og målrettet brugerpolitik med verificeret effekt.

## Formål

At håndhæve centrale sikkerhedsindstillinger med Group Policy og kontrollere både de effektive værdier og den synlige virkning på klienten.

## Udførte opgaver

| GPO | Link | Formål |
|---|---|---|
| `SecureBase - Domain Account Policy` | `securebase.local` · Link Order 1 | Password- og account-lockout-politik |
| `SecureBase - IT User Policy` | `SecureBase/IT` | Blokering af Run-dialogen for IT-brugere |

`Default Domain Policy` blev placeret som Link Order 2. Projektets GPO’er har **Enforced: No**.

| Indstilling | Konfiguration |
|---|---|
| Minimum password length | 12 tegn |
| Password must meet complexity requirements | Enabled |
| Account lockout threshold | 5 fejlede loginforsøg |
| Account lockout duration | 15 minutter |
| Reset account lockout counter after | 15 minutter |
| Allow Administrator account lockout | Disabled |
| Remove Run menu from Start Menu | Enabled i IT-brugerpolitikken |

De øvrige passwordfelter blev efterladt **Not Defined** i den nye GPO og kan dermed fortsat få værdier fra andre gældende politikker.

## Sikkerhedsmæssig begrundelse

Passwordlængde og kompleksitet begrænser brugen af svage passwords, mens lockout-grænsen begrænser gentagne online passwordgæt. Kontopolitikken blev linket til domæneroden for at styre domænekonti. [Microsoft: Account Policies](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/account-policies).

`Allow Administrator account lockout` blev konfigureret som en labundtagelse for at begrænse risikoen for administrativ udelukkelse under tests. Indstillingen fremgår af GPO’en; Administrator-kontoens lockout-adfærd blev ikke funktionstestet særskilt.

IT-politikken blev kun linket til IT-OU’en. Run-restriktionen blev valgt som en synlig demonstration af målretning — ikke som generel blokering af programkørsel.

## Dokumentation / bevis

### Effektiv password- og lockout-politik

På DC01 blev følgende værdier læst:

```powershell
Get-ADDefaultDomainPasswordPolicy |
Select-Object MinPasswordLength,ComplexityEnabled,LockoutThreshold,LockoutDuration,LockoutObservationWindow
```

![Effektiv password- og lockout-politik på DC01](../evidence/03-group-policy/09-effective-domain-password-policy.png)

*12 tegn, complexity True, threshold 5 og 15 minutters lockout/observationsvindue.*

### Brugerpolitikken på CLIENT01

Som `SECUREBASE\ejensen` blev politikken opdateret og kontrolleret:

```powershell
gpupdate /force
gpresult /r
```

![IT-brugerpolitikken er anvendt på CLIENT01](../evidence/03-group-policy/07-gpresult-it-policy.png)

*SecureBase - IT User Policy vises under Applied Group Policy Objects for Emil Jensen i IT-OU’en.*

![Run-dialogen er blokeret](../evidence/03-group-policy/08-run-restricted.png)

*Forsøg på at åbne Run gav en restrictions-besked.*

### Indstillinger og prioritet

| Bevis | Dokumenterer |
|---|---|
| [Password Policy](../evidence/03-group-policy/03-password-policy.png) | 12 tegn og complexity Enabled |
| [Account Lockout Policy](../evidence/03-group-policy/04-lockout-policy.png) | De konfigurerede lockout-indstillinger |
| [Remove Run](../evidence/03-group-policy/06-remove-run-enabled.png) | Den synlige brugerindstilling |
| [Domænets linkrækkefølge](../evidence/03-group-policy/10-domain-gpo-link-order.png) | Domain Account Policy før Default Domain Policy |
| [IT’s Group Policy Inheritance](../evidence/03-group-policy/11-it-gpo-inheritance.png) | IT-politikken og de nedarvede domænepolitikker |

## Overvejelser og fravalg

Den første kontrol viste minimumslængde 7 og threshold 0. Efter flytning af Domain Account Policy til Link Order 1 og genindlæsning af computerpolitikken viste kontrollen de ønskede værdier. Derfor blev både GPO-editoren og den effektive konfiguration brugt som dokumentation.

Run-restriktionen krævede ingen billedfil eller netværksdeling. Effekten blev testet for Emil; Sales og Management indgik ikke i en separat sammenligning. En højere minimumslængde er heller ikke et bevis på, at eksisterende passwords er ændret — kravet gælder ved oprettelse eller ændring af passwords.

## Resultat

Domænets effektive password- og lockout-værdier svarer til den valgte politik. IT-brugerpolitikken er dokumenteret med `gpresult /r` og den synlige blokering på CLIENT01.

---

[← Modul 2](02-active-directory.md) · [Alle 11 billeder](../evidence/03-group-policy/README.md) · [Modul 4 →](04-powershell.md)
