# Night Hunter

Night Hunter is an open-source defensive security workspace for authorized testing. It provides local Nmap profiles, web-security inspection, phishing-link analysis, password checks, cryptography utilities, and report export.

## Downloads

Download only from the official website: https://night-hunter-f2w4.onrender.com/#downloads

Before running a download, verify its SHA-256 value against [SHA256SUMS](SHA256SUMS). The Windows application opens a local dashboard at `http://127.0.0.1:5000`; local Nmap profiles require Nmap to be installed on the device.

## Responsible use

Use Night Hunter only on systems, networks, and URLs you own or are explicitly authorized to assess. Do not use it to access, disrupt, or collect data from systems without permission.

## Trust and policy

- [License](LICENSE)
- [Privacy policy](PRIVACY.md)
- [Security policy](SECURITY.md)
- [Distribution notes](DISTRIBUTION.md)

## Development

```bash
npm ci
npm run build
```

The hosted service is deployed from `main`. Release packages are built by GitHub Actions; direct packages are served through the official website.
