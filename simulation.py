
ARRIVAL_MAP = [
    (0.00, 0.20, 0),
    (0.20, 0.50, 1),
    (0.50, 0.80, 2),
    (0.80, 1.00, 3),
]

def convert_to_passengers(val, m=None):
    if m is not None and m > 0:
        u_value = float(val) / float(m)
    else:
        u_value = float(val)

    for lo, hi, arrivals in ARRIVAL_MAP:
        if lo <= u_value < hi:
            return arrivals
    return ARRIVAL_MAP[-1][2]   

def arrival_band_label(u_value):
    for lo, hi, arrivals in ARRIVAL_MAP:
        if lo <= u_value < hi:
            return f"{lo:.2f} ≤ {u_value:.4f} < {hi:.2f}  →  {arrivals} passenger{'s' if arrivals != 1 else ''}"
    return f"U = {u_value:.4f}  →  {ARRIVAL_MAP[-1][2]} passengers"

def gcd(a, b):
    a_val, b_val = abs(int(a)), abs(int(b))
    while b_val:
        a_val, b_val = b_val, a_val % b_val
    return a_val

def get_prime_factors(n):
    n = abs(int(n))
    factors = []
    if n <= 1:
        return factors
    if n % 2 == 0:
        factors.append(2)
        while n % 2 == 0:
            n //= 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 2
    if n > 1:
        factors.append(n)
    return sorted(factors)

def euler_phi(n):
    """Compute Euler's totient using the product formula — O(√n)."""
    n_val = int(n)
    if n_val <= 0:
        return 0
    if n_val == 1:
        return 1
    result = n_val
    temp = n_val
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

_SUPERSCRIPTS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

def get_prime_factorization(n):
    n_val = abs(int(n))
    factors = []
    if n_val <= 1:
        return factors
    if n_val % 2 == 0:
        exp = 0
        while n_val % 2 == 0:
            exp += 1
            n_val //= 2
        factors.append((2, exp))
    d = 3
    while d * d <= n_val:
        if n_val % d == 0:
            exp = 0
            while n_val % d == 0:
                exp += 1
                n_val //= d
            factors.append((d, exp))
        d += 2
    if n_val > 1:
        factors.append((n_val, 1))
    return factors

def format_factorization(n):
    n_val = int(n)
    if n_val <= 1:
        return f"{n_val} = {n_val}"
    pairs = get_prime_factorization(n_val)
    parts = []
    for p, exp in pairs:
        if exp == 1:
            parts.append(str(p))
        else:
            parts.append(f"{p}{str(exp).translate(_SUPERSCRIPTS)}")
    return f"{n_val} = " + " × ".join(parts)

def get_coprimes_list(n):
    n_val = int(n)
    if n_val <= 0:
        return []
    return [k for k in range(1, n_val + 1) if gcd(k, n_val) == 1]

def euler_phi_breakdown(n):
    n_val = int(n)
    phi_val = euler_phi(n_val)
    if n_val <= 1:
        return {
            "m": n_val,
            "phi_m": phi_val,
            "factorization_str": f"{n_val} = {n_val}",
            "primes": [],
            "formula_str": f"φ({n_val}) = {phi_val} (by definition)",
            "steps": [f"φ({n_val}) = {phi_val}"],
            "coprimes": [1] if n_val == 1 else [],
        }

    primes = [p for p, _ in get_prime_factorization(n_val)]
    fact_str = format_factorization(n_val)

    term1 = " × ".join(f"(1 − 1/{p})" for p in primes)
    step1 = f"φ({n_val}) = {n_val} × {term1}"

    term2 = " × ".join(f"{p - 1}/{p}" for p in primes)
    step2 = f"       = {n_val} × {term2}"

    num_prod = 1
    den_prod = 1
    for p in primes:
        num_prod *= (p - 1)
        den_prod *= p
    step3 = f"       = {n_val} × ({num_prod} / {den_prod})"
    step4 = f"       = {phi_val}"

    coprimes = get_coprimes_list(n_val)

    return {
        "m": n_val,
        "phi_m": phi_val,
        "factorization_str": fact_str,
        "primes": primes,
        "formula_str": "φ(n) = n × ∏(1 − 1/p)",
        "steps": [step1, step2, step3, step4],
        "coprimes": coprimes,
    }

def check_hull_dobell(a, c, m):
    a, c, m = int(a), int(c), int(m)
    m_primes = get_prime_factors(m)

    c1 = (gcd(c, m) == 1)

    c2 = all((a - 1) % p == 0 for p in m_primes)
    c2_failures = [p for p in m_primes if (a - 1) % p != 0]

    c3 = True
    if m % 4 == 0:
        c3 = ((a - 1) % 4 == 0)

    satisfied = c1 and c2 and c3

    reasons = []
    if not c1:
        reasons.append(f"gcd({c}, {m}) = {gcd(c, m)} ≠ 1  →  Condition 1 FAILS")
    if not c2:
        reasons.append(
            f"Prime factor(s) {c2_failures} of m={m} do not divide (a−1)={a-1}  →  Condition 2 FAILS"
        )
    if not c3:
        reasons.append(
            f"4 divides m={m}, but 4 does not divide (a−1)={a-1}  →  Condition 3 FAILS"
        )

    if satisfied:
        explanation = (
            f"All 3 Hull-Dobell conditions are satisfied. "
            f"The LCM sequence will achieve a FULL PERIOD of m = {m}."
        )
    else:
        explanation = "Hull-Dobell NOT satisfied: " + " | ".join(reasons)

    return {
        "condition1": c1,
        "condition2": c2,
        "condition3": c3,
        "satisfied": satisfied,
        "prime_factors_m": m_primes,
        "c2_failures": c2_failures,
        "reasons": reasons,
        "explanation": explanation,
    }

def lcm_next(x, a, c, m):
    return (int(a) * int(x) + int(c)) % int(m)

def lcm_step_breakdown(x, a, c, m):
    x, a, c, m = int(x), int(a), int(c), int(m)
    mult    = a * x
    summed  = mult + c
    next_x  = summed % m
    u_value = next_x / m

    arrivals = convert_to_passengers(u_value)

    calc_detail = (
        f"X(n+1) = (a · X(n) + c) mod m\n"
        f"       = ({a} × {x} + {c}) mod {m}\n"
        f"       = ({mult} + {c}) mod {m}\n"
        f"       = {summed} mod {m}\n"
        f"       = {next_x}\n"
        f"\n"
        f"U = X(n+1) / m = {next_x} / {m} = {u_value:.4f}\n"
        f"\n"
        f"{arrival_band_label(u_value)}"
    )

    calc_short = f"X(n+1) = ({a}·{x}+{c}) mod {m} = {next_x}"

    return {
        "x_current": x,
        "a": a,
        "c": c,
        "m": m,
        "mult": mult,
        "summed": summed,
        "next_x": next_x,
        "u_value": u_value,
        "arrivals": arrivals,
        "calc_detail": calc_detail,   
        "calc_short":  calc_short,    
        "calculation_str": calc_detail,
    }

def compute_period(seed, a, c, m):
    """Compute the actual period length of the LCM sequence starting from seed.

    For a full-period generator (Hull-Dobell satisfied), period == m.
    For suboptimal generators, the period will be shorter than m.
    """
    a, c, m = int(a), int(c), int(m)
    if m <= 0:
        return 0
    x = int(seed) % m
    start = x
    count = 0
    while True:
        x = (a * x + c) % m
        count += 1
        if x == start or count > m:
            return count

def run_simulation(seed=13, a=21, c=3, m=100,
                   duration=30, jeepney_interval=5, jeepney_capacity=12):

    seed, a, c, m = int(seed), int(a), int(c), int(m)
    duration, jeepney_interval, jeepney_capacity = (
        int(duration), int(jeepney_interval), int(jeepney_capacity)
    )

    original_seed  = seed
    seed           = original_seed % m          
    seed_normalized = (original_seed != seed)   

    current_x        = seed
    current_queue    = 0
    total_arrivals   = 0
    total_served     = 0
    max_queue        = 0
    cumulative_queue = 0
    jeepneys_dispatched = 0
    steps = []

    steps.append({
        "minute":          0,
        "time_str":        "08:00",
        "current_x":       current_x,
        "next_x":          None,
        "lcm_value":       current_x,
        "u_value":         None,
        "arrivals":        0,
        "queue_before_jeep": 0,
        "jeepney_arrived": False,
        "served":          0,
        "queue":           0,
        "calculation":     f"Initial Seed X0 = {current_x}"
                           + (f"  (normalized from {original_seed})" if seed_normalized else ""),
        "calc_detail":     (
            f"Initial seed X0 = {current_x}"
            + (f"\n\nNOTE: Original seed {original_seed} ≥ m={m},\n"
               f"normalized: X0 = {original_seed} mod {m} = {current_x}"
               if seed_normalized else "")
        ),
    })

    for minute in range(1, duration + 1):
        hour    = 8 + minute // 60
        min_rem = minute % 60
        time_str = f"{hour:02d}:{min_rem:02d}"

        step_math = lcm_step_breakdown(current_x, a, c, m)
        next_x    = step_math["next_x"]
        u_value   = step_math["u_value"]
        current_x = next_x

        arrivals       = step_math["arrivals"]
        total_arrivals += arrivals
        current_queue  += arrivals

        jeepney_arrived = (minute % jeepney_interval == 0)
        served = 0

        if jeepney_arrived:
            jeepneys_dispatched += 1
            served         = min(current_queue, jeepney_capacity)
            current_queue -= served
            total_served  += served

        max_queue        = max(max_queue, current_queue)
        cumulative_queue += current_queue

        steps.append({
            "minute":          minute,
            "time_str":        time_str,
            "current_x":       step_math["x_current"],
            "next_x":          next_x,
            "lcm_value":       next_x,
            "u_value":         u_value,
            "arrivals":        arrivals,
            "queue_before_jeep": current_queue + served if jeepney_arrived else current_queue,
            "jeepney_arrived": jeepney_arrived,
            "served":          served,
            "queue":           current_queue,
            "calculation":     step_math["calc_short"],
            "calc_detail":     step_math["calc_detail"],
        })

    avg_queue = round(cumulative_queue / duration, 2) if duration > 0 else 0.0

    reconciled = (total_arrivals == total_served + current_queue)

    phi_info   = euler_phi_breakdown(m)
    phi_m      = phi_info["phi_m"]
    gcd_am     = gcd(a, m)
    gcd_cm     = gcd(c, m)
    hd_result  = check_hull_dobell(a, c, m)
    period     = compute_period(seed, a, c, m)

    avg_arrivals_per_min    = round(total_arrivals / duration, 2) if duration > 0 else 0.0
    avg_served_per_jeepney  = (round(total_served / jeepneys_dispatched, 2)
                               if jeepneys_dispatched > 0 else 0.0)
    service_rate_pct        = (round(total_served / total_arrivals * 100, 1)
                               if total_arrivals > 0 else 0.0)

    return {
        "parameters": {
            "seed":            seed,
            "original_seed":   original_seed,
            "seed_normalized": seed_normalized,
            "multiplier":      a,
            "increment":       c,
            "modulus":         m,
            "duration":        duration,
            "jeepney_interval": jeepney_interval,
            "jeepney_capacity": jeepney_capacity,
        },
        "summary": {
            "total_arrivals":         total_arrivals,
            "total_served":           total_served,
            "remaining_queue":        current_queue,
            "max_queue":              max_queue,
            "avg_queue":              avg_queue,
            "jeepneys_dispatched":    jeepneys_dispatched,
            "avg_arrivals_per_min":   avg_arrivals_per_min,
            "avg_served_per_jeepney": avg_served_per_jeepney,
            "service_rate_pct":       service_rate_pct,
            "reconciled":             reconciled,
            "period":                 period,
            "is_full_period":         (period == m),
        },
        "euler_phi": {
            "m":                 m,
            "phi_m":             phi_m,
            "gcd_am":            gcd_am,
            "gcd_cm":            gcd_cm,
            "prime_factors":     phi_info["primes"],
            "factorization_str": phi_info["factorization_str"],
            "coprimes":          phi_info["coprimes"],
            "breakdown":         phi_info,
        },
        "hull_dobell": hd_result,
        "arrival_map": ARRIVAL_MAP,
        "steps":       steps,
    }
