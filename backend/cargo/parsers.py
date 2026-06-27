import re
from typing import List, Optional, Tuple

LEGACY_LINE_PATTERN = re.compile(
    r'^\[.*?\]\s*\|\|\s*(?P<cargo_id>[^:\s][^:]*?)\s*::\s*(?P<weight>[\d.]+)\s*>>\s*(?P<destination>.+?)\s*$'
)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def parse_line(trimmed: str) -> Optional[Tuple[str, str, str]]:
    legacy_match = LEGACY_LINE_PATTERN.match(trimmed)
    if legacy_match:
        return (
            legacy_match.group('cargo_id').strip(),
            legacy_match.group('destination').strip(),
            legacy_match.group('weight').strip(),
        )

    parts = [part.strip() for part in trimmed.split(',')]
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]

    return None


def parse_manifest(content: str) -> Tuple[List[dict], List[dict]]:
    """
    Parse legacy manifest lines:
      [DATE] || CARGO_ID :: WEIGHT >> DESTINATION
    Also supports CSV fallback: CARGO_ID,DESTINATION,WEIGHT
    Returns (records_to_save, skipped_entries).
    """
    records = []
    skipped = []

    for line in content.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith('#'):
            continue

        parsed = parse_line(trimmed)
        if parsed is None:
            skipped.append({'line': trimmed, 'reason': 'Invalid format'})
            continue

        cargo_id, destination, weight_raw = parsed

        try:
            weight = float(weight_raw)
        except ValueError:
            skipped.append({'line': trimmed, 'reason': 'Invalid weight'})
            continue

        if not cargo_id or not destination:
            skipped.append({'line': trimmed, 'reason': 'Missing fields'})
            continue

        if 'Sector-7' in destination:
            weight *= 1.45

        weight = round(weight)

        if is_prime(weight):
            skipped.append({
                'cargo_id': cargo_id,
                'destination': destination,
                'weight': weight,
                'reason': 'Prime weight excluded',
            })
            continue

        records.append({
            'cargo_id': cargo_id,
            'destination': destination,
            'weight_kg': weight,
        })

    return records, skipped
