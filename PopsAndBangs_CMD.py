#!/usr/bin/env python3
"""Pops&Bangs CMD v1.5

Command-line Pops & Bangs installer for the VAG 20VT ME7.5 platform.
Detection and byte modifications are reproduced from the supplied application source code.

The program does not correct ECU checksums, matching the source application.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

APP_NAME = "Pops&Bangs CMD"
APP_VERSION = "1.5"
SOURCE_APP_VERSION = "1.2.0.1"
EXPECTED_SIZE = 1_048_576


class PopsAndBangsError(RuntimeError):
    pass


@dataclass(frozen=True)
class Profile:
    name: str
    kfzwmn: int
    kfnwegm: int
    kftvsa: int
    kftvsakat: int


# Values copied from Make20VTVag() in mMain.cs.
PROFILES = {
    "low": Profile("Low", 230, 170, 150, 255),
    "medium": Profile("Medium", 223, 170, 200, 255),
    "high": Profile("High", 216, 170, 255, 255),
}

# Exact KFNWEGM patterns copied from Process20VTVag() in mMain.cs.
KFNWEGM_PATTERN_1 = bytes([128] * 30 + [26])
KFNWEGM_PATTERN_2 = bytes([
    128, 128, 126, 125, 124, 123, 145, 141,
    128, 128, 125, 124, 122, 121, 148, 145,
    128, 128, 125, 124, 122, 121, 149, 146,
    128, 128, 125, 124, 122, 121, 26,
])

KFZWMN_OFFSETS = (
    96, 97, 108, 109, 120, 121, 132, 133, 144, 145, 156, 157,
    168, 169, 170, 171, 180, 181, 182, 183, 184, 185,
)

KFTVSA_WRITES = (
    (3, -100), (4, -50), (5, 0), (6, 0), (7, 0),
    (11, -100), (12, -50), (13, 0), (14, 0), (15, 0),
    (19, -100), (20, -50), (21, 0), (22, 0), (23, 0),
    (27, -100), (28, -50), (29, 0), (30, 0), (31, 0),
    (35, -100), (36, -50), (37, 0), (38, 0), (39, 0),
)

# Exact write order/addresses from Make20VTVag().
KFTVSAKAT_OFFSETS = (
    7, 4, 5, 6,
    15, 12, 13, 14,
    20, 21, 22, 23,
    28, 29, 30, 31,
)


def parse_hex(value: str) -> int:
    try:
        return int(value.strip().lower().removeprefix("0x"), 16)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid hexadecimal address: {value}") from exc


def find_last(data: bytes, pattern: bytes) -> tuple[int | None, int]:
    """Return last match + pattern length, matching the original application behavior."""
    last: int | None = None
    count = 0
    start = 0
    while True:
        pos = data.find(pattern, start)
        if pos < 0:
            return (None if last is None else last + len(pattern)), count
        last = pos
        count += 1
        start = pos + 1


def detect_kfzwmn(data: bytes) -> tuple[int | None, int]:
    """Exact source condition; the last match is selected, as in the original application."""
    selected: int | None = None
    matches = 0

    # mMain.cs uses array[i + 193], although its decompiled loop bound says -30.
    # A safe bound avoids an IndexError and does not alter any valid match.
    for i in range(0, max(0, len(data) - 193)):
        if (
            data[i] == 16
            and data[i + 1] == 12
            and data[i + 2] > 10
            and data[i + 2] < 30
            and data[i + 193] > 128
        ):
            selected = i + 30
            matches += 1
    return selected, matches


def detect_addresses(data: bytes) -> tuple[int, int, int, int, list[str]]:
    log: list[str] = []
    log.append("Please Note : This application will not detect addresses if Pops&Bangs is enabled/has been attempted.\n")
    log.append("Use the original file to detect the addresses and manually input them.\n")
    log.append("Automatic detection...")

    log.append("Looking for KFZWMN...")
    kfzwmn, kfzwmn_count = detect_kfzwmn(data)

    log.append("Looking for KFNWEGM...")
    kfnwegm, alg1_count = find_last(data, KFNWEGM_PATTERN_1)
    algorithm = 1 if kfnwegm is not None else None
    alg2_count = 0

    if kfnwegm is None:
        log.append("Switching algorithm to KFNWEGM/2...")
        kfnwegm, alg2_count = find_last(data, KFNWEGM_PATTERN_2)
        algorithm = 2 if kfnwegm is not None else None

    if kfnwegm is None:
        log.append("Narrowband ECU Detected - Not Supported!")
        raise PopsAndBangsError("KFNWEGM was not found by either original application algorithm.")

    log.append("Calculating KFTVSA & KFTVSAKAT...")
    kftvsa = kfnwegm + 40
    log.append(f"KFTVSA - {kftvsa:X}")
    kftvsakat = kftvsa + 40
    # The GUI source contains a display typo here and prints tbKFTVSA.
    # CLI prints the actual calculated KFTVSAKAT address.
    log.append(f"KFTVSAKAT - {kftvsakat:X}")

    if kfzwmn is None:
        raise PopsAndBangsError("KFZWMN was not found by the original application source algorithm.")

    log.append("")
    log.append(f"KFZWMN matches: {kfzwmn_count}; selected last match")
    log.append(f"KFNWEGM algorithm: {algorithm}; matches: {alg1_count if algorithm == 1 else alg2_count}")
    return kfzwmn, kfnwegm, kftvsa, kftvsakat, log


def validate_address(data: bytes | bytearray, address: int, largest_offset: int, name: str) -> None:
    if address < 0 or address + largest_offset >= len(data):
        raise PopsAndBangsError(
            f"{name} address/range is outside the BIN: 0x{address:X}..0x{address + largest_offset:X}"
        )


def apply_source_modifications(
    original: bytes,
    profile: Profile,
    kfzwmn: int,
    kfnwegm: int,
    kftvsa: int,
    kftvsakat: int,
) -> tuple[bytes, list[str], int]:
    data = bytearray(original)
    log: list[str] = []
    changed = 0

    validate_address(data, kfzwmn, max(KFZWMN_OFFSETS), "KFZWMN")
    validate_address(data, kfnwegm, 39, "KFNWEGM")
    validate_address(data, kftvsa, 39, "KFTVSA")
    validate_address(data, kftvsakat, max(KFTVSAKAT_OFFSETS), "KFTVSAKAT")

    def write(address: int, value: int) -> None:
        nonlocal changed
        value &= 0xFF
        if data[address] != value:
            changed += 1
        data[address] = value

    log.append("Processing KFZWMN...")
    for offset in KFZWMN_OFFSETS:
        write(kfzwmn + offset, profile.kfzwmn)

    log.append("Processing KFNWEGM...")
    for offset in range(40):
        write(kfnwegm + offset, profile.kfnwegm)

    log.append("Processing KFTVSA...")
    for offset, adjustment in KFTVSA_WRITES:
        write(kftvsa + offset, profile.kftvsa + adjustment)

    log.append("Processing KFTVSAKAT...")
    for offset in KFTVSAKAT_OFFSETS:
        write(kftvsakat + offset, profile.kftvsakat)

    return bytes(data), log, changed


def choose_profile() -> Profile:
    print("\nSelect profile:")
    print("  [1] Low")
    print("  [2] Medium")
    print("  [3] High")
    print("  [0] Exit")
    choices = {"1": PROFILES["low"], "2": PROFILES["medium"], "3": PROFILES["high"]}
    while True:
        choice = input("\nChoice: ").strip()
        if choice == "0":
            raise KeyboardInterrupt
        if choice in choices:
            return choices[choice]
        print("Invalid choice. Enter 0, 1, 2 or 3.")


def default_output(input_path: Path, profile: Profile) -> Path:
    return input_path.with_name(f"{input_path.stem}_POPS_BANGS_{profile.name.upper()}{input_path.suffix}")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Bosch ME7.5 VAG 20VT Pops & Bangs command-line installer."
    )
    p.add_argument("input", type=Path, help="Original input BIN")
    p.add_argument("-p", "--profile", choices=tuple(PROFILES), help="low, medium or high")
    p.add_argument("-o", "--output", type=Path, help="Output BIN")
    p.add_argument("--kfzwmn", type=parse_hex, help="Manual KFZWMN address")
    p.add_argument("--kfnwegm", type=parse_hex, help="Manual KFNWEGM address")
    p.add_argument("--kftvsa", type=parse_hex, help="Manual KFTVSA address")
    p.add_argument("--kftvsakat", type=parse_hex, help="Manual KFTVSAKAT address")
    p.add_argument("--allow-any-size", action="store_true", help="Allow BIN other than 1 MiB")
    return p


def main() -> int:
    args = parser().parse_args()

    print("=" * 60)
    print(f"{'Bosch ME7.5 Pops & Bangs Installer':^60}")
    print("=" * 60)
    print(f"Version          : {APP_VERSION}")
    print(f"Source version   : {SOURCE_APP_VERSION}")

    input_path = args.input.expanduser().resolve()
    if not input_path.is_file():
        raise PopsAndBangsError(f"Input file not found: {input_path}")

    original = input_path.read_bytes()
    print(f"Input file       : {input_path.name}")
    print(f"File size        : {len(original)} bytes")
    if len(original) != EXPECTED_SIZE and not args.allow_any_size:
        raise PopsAndBangsError(
            f"Expected a 1 MiB BIN ({EXPECTED_SIZE} bytes). Use --allow-any-size to override."
        )

    manual_any = any(x is not None for x in (args.kfzwmn, args.kfnwegm, args.kftvsa, args.kftvsakat))
    detection_log: list[str] = []

    if manual_any:
        # Detect first so unspecified addresses still follow source behavior.
        try:
            detected = detect_addresses(original)
            dkfzwmn, dkfnwegm, dkftvsa, dkftvsakat, detection_log = detected
        except PopsAndBangsError:
            dkfzwmn = dkfnwegm = dkftvsa = dkftvsakat = None

        kfzwmn = args.kfzwmn if args.kfzwmn is not None else dkfzwmn
        kfnwegm = args.kfnwegm if args.kfnwegm is not None else dkfnwegm
        if kfnwegm is None:
            raise PopsAndBangsError("KFNWEGM is required when automatic detection fails.")
        kftvsa = args.kftvsa if args.kftvsa is not None else (dkftvsa if dkftvsa is not None else kfnwegm + 40)
        kftvsakat = args.kftvsakat if args.kftvsakat is not None else (dkftvsakat if dkftvsakat is not None else kftvsa + 40)
        if kfzwmn is None:
            raise PopsAndBangsError("KFZWMN is required when automatic detection fails.")
        detection_log.append("Manual address override applied.")
    else:
        kfzwmn, kfnwegm, kftvsa, kftvsakat, detection_log = detect_addresses(original)

    print("\nDetection log")
    print("-" * 60)
    for line in detection_log:
        print(line)

    print("\nDetected addresses")
    print("-" * 60)
    print(f"KFZWMN           : 0x{kfzwmn:06X}")
    print(f"KFNWEGM          : 0x{kfnwegm:06X}")
    print(f"KFTVSA           : 0x{kftvsa:06X}")
    print(f"KFTVSAKAT        : 0x{kftvsakat:06X}")

    profile = PROFILES[args.profile] if args.profile else choose_profile()
    print(f"\nPops level       : {profile.name}")

    modified, processing_log, changed = apply_source_modifications(
        original, profile, kfzwmn, kfnwegm, kftvsa, kftvsakat
    )
    for line in processing_log:
        print(line)

    output_path = args.output.expanduser().resolve() if args.output else default_output(input_path, profile)
    if output_path == input_path:
        raise PopsAndBangsError("Output path must be different from input path.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(modified)

    log_path = output_path.with_suffix(".log")
    log_lines = [
        f"{APP_NAME} v{APP_VERSION}",
        f"Source version: {SOURCE_APP_VERSION}",
        f"Input: {input_path}",
        f"Output: {output_path}",
        f"Profile: {profile.name}",
        f"KFZWMN: 0x{kfzwmn:06X}",
        f"KFNWEGM: 0x{kfnwegm:06X}",
        f"KFTVSA: 0x{kftvsa:06X}",
        f"KFTVSAKAT: 0x{kftvsakat:06X}",
        f"Changed bytes: {changed}",
        "Checksum: NOT corrected",
        "",
        *detection_log,
        *processing_log,
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print("\nResult")
    print("-" * 60)
    print(f"Changed bytes    : {changed}")
    print(f"Output BIN       : {output_path}")
    print(f"Log file         : {log_path}")
    print("Checksum         : NOT corrected (same as source application)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
        raise SystemExit(130)
    except PopsAndBangsError as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
    except OSError as exc:
        print(f"\n[ERROR] File operation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
