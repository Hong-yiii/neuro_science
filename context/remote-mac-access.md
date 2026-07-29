# Remote Mac Access

Created: 2026-07-29

Goal: control a lab Mac workstation remotely through the lab SSH gateway `cortex.nus.edu.sg`.

Do not store passwords or private keys in this repo.

## Current Local Setup

Hongyi already has local SSH keys:

- `~/.ssh/id_rsa`
- `~/.ssh/id_ed25519`

The local SSH config now has a shortcut:

```sshconfig
Host cortex
    HostName cortex.nus.edu.sg
    User hippocampus
    IdentityFile ~/.ssh/id_rsa
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

Status on 2026-07-29:

- `cortex.nus.edu.sg` is reachable from this laptop/network.
- The host key has been accepted into local `known_hosts`.
- Gateway login is not authorized yet: SSH returns `Permission denied (publickey,password)`.
- The next step is to send the local RSA public key to a lab member who can add it to the gateway authorized keys.
- Current workstation IP from Hongyi: `10.0.0.202`.

To copy the public key again:

```sh
pbcopy < ~/.ssh/id_rsa.pub
```

## Setup Checklist

1. Be on the NUS network or connected to NUS VPN.
2. Give the lab an SSH public key to add to the `hippocampus` authorized keys on `cortex`.
3. Test gateway login:

```sh
ssh cortex
```

4. Pick the lab workstation number or IP.
   - Current workstation IP: `10.0.0.202`.
5. Open a tunnel from the laptop to the workstation VNC service:

```sh
ssh -L 1220:10.0.0.202:5900 cortex
```

For another `workXX`, replace the IP with that workstation's IP.

6. While the tunnel window stays open, connect from Finder:

```text
Go -> Connect to Server...
vnc://localhost:1220
```

7. Log into the workstation with the lab-provided workstation account.

## Notes

- If Finder says someone else is using the computer, choose the option to log in with your own username rather than taking over someone else's session.
- Keep the SSH tunnel terminal open while using VNC.
- If the VNC connection fails, check in this order:
  1. NUS VPN/network is connected.
  2. `ssh cortex` works.
  3. the workstation number/IP is correct.
  4. the workstation is awake and reachable.
  5. no other local process is already using port `1220`.
