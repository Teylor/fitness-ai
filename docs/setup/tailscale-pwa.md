# Remote Access & Android PWA Setup (Tailscale)

This guide explains how to access the Fitness AI dashboard from Android outside your home network and install it as a **PWA (Progressive Web App)** using **Tailscale**.

## 1. Prerequisites
- A free Tailscale account (https://tailscale.com).
- Fitness AI server running on your PC (`python -m src.main`, default `127.0.0.1:9700`).

## 2. Windows PC Setup
1. Install **Tailscale for Windows** from https://tailscale.com/download/windows and sign in.
2. Enable **MagicDNS** and **HTTPS Certificates** in the Tailscale Admin Console (`DNS` tab → Enable MagicDNS + Enable HTTPS).
3. In a terminal (PowerShell) on the PC, expose port `9700` over HTTPS inside your private tailnet:
   ```powershell
   tailscale serve --bg 9700
   ```
   > Tailscale will print your private HTTPS URL, e.g. `https://<pc-name>.<tailnet>.ts.net`.
   > To check or stop it later: `tailscale serve status` / `tailscale serve reset`.

*(Optional)* If you prefer direct HTTP access without `tailscale serve`, you can set `MCP_HOST=0.0.0.0` in `.env`, though Chrome requires HTTPS (`tailscale serve`) to show the **Install app (PWA)** prompt.

## 3. Android Setup & PWA Install
1. Install **Tailscale** from Google Play Store and sign in with the **same account**.
2. Turn **ON** the Tailscale VPN toggle on Android.
3. Open **Chrome** on Android and go to:
   `https://<pc-name>.<tailnet>.ts.net/ui`
4. Open Chrome's `⋮` menu → **Install app** (or **Add to Home screen**).
5. Fitness AI will appear on your home screen with its own icon and open in standalone full-screen mode.
