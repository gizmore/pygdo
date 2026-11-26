#!/usr/bin/env bash
# Run the same small ApacheBench workload against PyGDO and Django, in order.
set -euo pipefail

usage() {
    printf '%s\n' \
        'Usage: ./gdo_benchmark.sh [-n requests] [-c concurrency] PYGDO_URL DJANGO_URL' \
        'Defaults: 100 requests, concurrency 5. Use only authorized targets.' \
        'Choose equivalent pages; results are not automatically normalized.'
}

requests=100
concurrency=5
while getopts ':n:c:h' option; do
    case "$option" in
        n) requests=$OPTARG ;;
        c) concurrency=$OPTARG ;;
        h) usage; exit 0 ;;
        *) usage >&2; exit 2 ;;
    esac
done
shift "$((OPTIND - 1))"

if [[ $# != 2 || ! $requests =~ ^[1-9][0-9]*$ || ! $concurrency =~ ^[1-9][0-9]*$ ]]; then
    usage >&2
    exit 2
fi
if (( ${#requests} > 7 || ${#concurrency} > 7 )); then
    printf '%s\n' 'Request and concurrency values are too large.' >&2
    exit 2
fi
if (( concurrency > requests )); then
    printf '%s\n' 'Concurrency cannot exceed the number of requests.' >&2
    exit 2
fi
for url in "$@"; do
    if [[ ! $url =~ ^https?://[^/@[:space:]]+(/[^[:space:]]*)?$ ]]; then
        printf '%s\n' 'URLs must be HTTP(S), contain a host, and have no userinfo or whitespace.' >&2
        exit 2
    fi
done
if ! command -v ab >/dev/null 2>&1; then
    printf '%s\n' 'ApacheBench (ab) is required; install it before running this script.' >&2
    exit 1
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
report=$(mktemp "${TMPDIR:-/tmp}/gdo-benchmark.XXXXXXXX")
trap 'rm -f -- "$report"' EXIT
benchmark_python=${BENCHMARK_PYTHON:-python3}

{
    printf 'Benchmark started: %s\nRequests: %s; concurrency: %s\n' "$(date -u '+%Y-%m-%d %H:%M:%S UTC')" "$requests" "$concurrency"
    printf 'PyGDO revision: %s\n' "$(git -C "$script_dir" rev-parse --short HEAD 2>/dev/null || printf 'unknown')"
    if git -C "$script_dir" status --porcelain --untracked-files=no 2>/dev/null | grep -q .; then
        printf '%s\n' 'PyGDO tracked worktree: modified'
    else
        printf '%s\n' 'PyGDO tracked worktree: clean or unavailable'
    fi
    if command -v "$benchmark_python" >/dev/null 2>&1; then
        "$benchmark_python" -c 'import sys; print("Python:", sys.version.split()[0], "(" + sys.executable + ")"); from importlib.metadata import version, PackageNotFoundError; exec("try:\n print(\"Django package:\", version(\"Django\"))\nexcept PackageNotFoundError:\n print(\"Django package: unavailable\")")'
    else
        printf '%s\n' 'Python and Django versions: unavailable'
    fi
    printf '\n%s\n' '=== PyGDO ==='
    ab -n "$requests" -c "$concurrency" "$1"
    printf '\n%s\n' '=== Django ==='
    ab -n "$requests" -c "$concurrency" "$2"
} | tee "$report"

{
    printf '\n### Run %s\n\n```text\n' "$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    cat "$report"
    printf '\n```\n'
} >> "$script_dir/DOCS/99_BENCHMARKS.md"
printf '\nResults appended to %s\n' "$script_dir/DOCS/99_BENCHMARKS.md"
