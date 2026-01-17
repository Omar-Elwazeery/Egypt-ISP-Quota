# Egypt ISP Quota Manager

A secure, modern desktop application to manage and check internet quotas for **WE (Telecom Egypt)** accounts directly from your PC.

## 🚀 Features

*   **Multi-Account Support**: Add and manage multiple landline or 4G accounts.
*   **Secure Storage**: Credentials are encrypted using `AES` and keys are stored securely in the **Windows Credential Manager**. Your passwords never sit in plain text.
*   **Smart Automation**: Automatically processes CAPTCHAs (where applicable) and navigates the ISP portal.
*   **Headless Mode**: Checks your quota in the background without opening visible browser windows.
*   **4G & Landline Support**: Automatically detects and handles different account types.

## 🛠 Prerequisites

*   **Mozilla Firefox** (Required: The app uses Firefox for web automation)

> **Note for Developers**: If running from source, you'll also need Python 3.10+ and the dependencies in `requirements.txt`.

## 📦 Installation & Usage

1.  **Download** the latest release `.zip` from the [Releases](https://github.com/Omar-Elwazeery/Egypt-ISP-Quota/releases) page.
2.  **Extract** the zip file to any folder.
3.  **Run** `EgyptISPQuota.exe` from the extracted folder.
4.  **No installation required**! The app stores your data securely in your local AppData folder.

### How to use:
1.  Click **"+ Add Account"**.
2.  Enter your **Service Number** and **Password** (the same one you use for the `my.te.eg` website or `My WE` mobile app).
3.  Select the account type (**Internet** for landline, **4G** for mobile internet).
4.  Click **Save**.
5.  Select the account from the list and click **"Check Quota Now"**.

## 🔮 Future Plans

*   [ ] **Full ISP Support**: Adding support for **Vodafone**, **Orange**, and **Etisalat** home internet.
*   [ ] **Auto-Check**: Option to check quota automatically on startup.
*   [ ] **Notifications**: Desktop alerts when quota is low.

## 🔒 Security

*   Data is stored in `%APPDATA%\EgyptISPQuotaChecker\accounts.enc`.
*   This file is encrypted. Moving it to another computer renders it useless without the encryption key stored in your specific Windows User Credential Manager.

## ⚠️ Disclaimer

This tool is an unofficial client and is not affiliated with Telecom Egypt (WE). It automates the login process to the official user portal for convenience. Use responsibly.
