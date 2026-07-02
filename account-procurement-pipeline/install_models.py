#!/usr/bin/env python3
"""Install offline Argos translation models (source -> English). Cross-platform.

Called by setup.sh (Linux/macOS) and setup.ps1 (Windows). Needs network once;
after this the models run fully offline.
"""

import argostranslate.package as pkg

WANT = ["ru", "zh", "vi", "es", "pt", "tr", "uk", "de", "fr", "id"]


def main():
    pkg.update_package_index()
    available = pkg.get_available_packages()
    installed, missing = [], []
    for code in WANT:
        match = next((p for p in available if p.from_code == code and p.to_code == "en"), None)
        if match is None:
            missing.append(code)
            continue
        pkg.install_from_path(match.download())
        installed.append(code)

    print(f"  installed: {', '.join(installed) or 'none'}")
    if missing:
        print(f"  NOT in Argos index: {', '.join(missing)}")
        print("  (Vietnamese 'vi' often needs an OPUS-MT model converted to .argosmodel;")
        print("   see README 'Vietnamese' section. Detection still works; those posts")
        print("   pass through untranslated and are keyword-matched in their own language.)")


if __name__ == "__main__":
    main()
