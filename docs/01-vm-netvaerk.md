# Modul 1: VM-opsætning og netværk

[Overblik](../README.md) · [Modul 2 →](02-active-directory.md)

> **Gennemført og dokumenteret** · DC01 og CLIENT01

## Formål

At etablere et isoleret VirtualBox-lab, hvor en Windows Server og en Windows-klient kan kommunikere på et separat internt netværk uden at påvirke andre netværk.

## Udførte opgaver

DC01 blev installeret med **Windows Server 2025 Standard Evaluation, Desktop Experience**, og CLIENT01 med **Windows 11 Enterprise Evaluation**. Begge maskiner blev tilsluttet samme Internal Network, fik statiske IPv4-adresser og blev omdøbt i Windows.

### IP-plan

| Maskine | IPv4 | Subnetmaske | DNS | Gateway |
|---|---|---|---|---|
| DC01 | `192.168.50.10` | `255.255.255.0` | `192.168.50.10` | Ingen |
| CLIENT01 | `192.168.50.20` | `255.255.255.0` | `192.168.50.10` | Ingen |

Netværket hedder **`labnet-khr`**. Windows-netværksprofilen blev sat til **Private** på begge maskiner under dette modul. DNS-adressen blev forberedt til DC01; selve AD DS/DNS-rollen blev først installeret i [Modul 2](02-active-directory.md).

### Netværkstest og oprydning

Den indbyggede regel `FPS-ICMP4-ERQ-In-V2` blev aktiveret midlertidigt til pingtesten. Begge retninger gav fire svar og **0 % pakketab**. Derefter blev den samme regel deaktiveret igen.

```powershell
# På begge VM’er, i forbindelse med den dokumenterede test:
Enable-NetFirewallRule -Name "FPS-ICMP4-ERQ-In-V2"

# På DC01:
ping 192.168.50.20

# På CLIENT01:
ping 192.168.50.10

# Efter testen på begge VM’er:
Disable-NetFirewallRule -Name "FPS-ICMP4-ERQ-In-V2"
```

En tidligere brugerdefineret regel, `SecureBase Lab - ICMPv4 Echo`, blev fjernet ved firewallnulstillingen. Et efterfølgende opslag efter dette navn gav ingen resultater på begge VM’er.

### Hostnames og Guest Additions

`hostname` returnerede henholdsvis **DC01** og **CLIENT01**. `Get-Service VBoxService` viste **Running** på begge maskiner.

## Sikkerhedsmæssig begrundelse

Internal Network blev valgt for at holde labtrafikken adskilt fra de øvrige netværk. Faste adresser gør DC01 forudsigelig som kommende DNS- og domænetjeneste. Klienten blev derfor konfigureret med DC01 som DNS.

Windows Firewall blev ikke efterladt deaktiveret. Den midlertidige pingtilladelse blev brugt til en konkret forbindelsestest og derefter deaktiveret igen. Bred aktivering af fil- og printerdeling blev ikke bevaret som slutkonfiguration.

## Dokumentation / bevis

### Resultater

| Kontrol | Observeret resultat | Bevis |
|---|---|---|
| IP og DNS på DC01 | `192.168.50.10/24`, DNS `192.168.50.10` | [Åbn billede](../evidence/01-vm-netvaerk/01-dc01-ipv4.png) |
| IP og DNS på CLIENT01 | `192.168.50.20/24`, DNS `192.168.50.10` | [Åbn billede](../evidence/01-vm-netvaerk/02-client01-ipv4.png) |
| DC01 → CLIENT01 | 4/4 svar, 0 % pakketab | [Åbn billede](../evidence/01-vm-netvaerk/03-dc01-ping-og-oprydning.png) |
| CLIENT01 → DC01 | 4/4 svar, 0 % pakketab | [Åbn billede](../evidence/01-vm-netvaerk/04-client01-ping-og-oprydning.png) |
| Tidligere custom-regel | Ingen resultater ved opslag på begge VM’er | [Åbn billede](../evidence/01-vm-netvaerk/05-custom-firewallregel-fravaerende.png) |
| Windows-hostnames | `DC01` og `CLIENT01` | [DC01](../evidence/01-vm-netvaerk/06-dc01-hostname.png) · [CLIENT01](../evidence/01-vm-netvaerk/07-client01-hostname.png) |
| VirtualBox-netværk | Internal Network `labnet-khr` på begge | [DC01](../evidence/01-vm-netvaerk/08-dc01-internal-network.png) · [CLIENT01](../evidence/01-vm-netvaerk/09-client01-internal-network.png) |
| Guest Additions | `VBoxService` er Running på begge | [DC01](../evidence/01-vm-netvaerk/10-dc01-guest-additions.png) · [CLIENT01](../evidence/01-vm-netvaerk/11-client01-guest-additions.png) |

### Pingbevis — begge retninger

![DC01 pinger CLIENT01 og deaktiverer testreglen](../evidence/01-vm-netvaerk/03-dc01-ping-og-oprydning.png)

*DC01 → CLIENT01: vellykket pingtest efterfulgt af deaktivering af testreglen.*

![CLIENT01 pinger DC01 og deaktiverer testreglen](../evidence/01-vm-netvaerk/04-client01-ping-og-oprydning.png)

*CLIENT01 → DC01: fire svar, intet pakketab og efterfølgende oprydning.*

[Åbn hele bevisoversigten — 11 screenshots →](../evidence/01-vm-netvaerk/README.md)

## Overvejelser og fravalg

**DHCP og default gateway.** To statiske adresser var tilstrækkelige til labbet. Der blev ikke konfigureret en router på det interne segment, og gateway-feltet blev derfor efterladt tomt.

**Firewallfejlsøgning.** Både en bred fil-/printerdelingsregelgruppe og en separat ICMP-regel blev afprøvet undervejs, men blev rullet tilbage ved firewallnulstilling. Den afsluttende test brugte den indbyggede pingregel midlertidigt. Det relevante læringspunkt er forskellen mellem netværksforbindelse og tilladelse til en bestemt trafiktype.

**Afgrænsning.** Pingbeviserne viser forbindelsen på testtidspunktet. De er ikke et bevis for, at DNS, domænejoin eller alle senere tjenester fungerer; disse forhold dokumenteres i de følgende moduler. Opslaget efter den fjernede regel kontrollerer kun det angivne navn, ikke hele firewallkonfigurationen.

## Status

- [x] Isoleret Internal Network `labnet-khr` dokumenteret.
- [x] IP-plan og DNS-adresser dokumenteret.
- [x] Vellykket netværkstest i begge retninger.
- [x] Midlertidig pingregel deaktiveret og tidligere custom-regel kontrolleret fraværende.
- [x] Windows-hostnames verificeret.
- [x] Guest Additions-tjenesten verificeret som Running på begge VM’er.

**Modul 1 er gennemført og dokumenteret.** Ovenstående er modulets dokumenterede afslutning; DC01’s og CLIENT01’s domæneopsætning følger i Modul 2.

---

[Overblik](../README.md) · [Modul 2 →](02-active-directory.md)
