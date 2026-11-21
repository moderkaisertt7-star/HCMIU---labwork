"""
EE091IU Electronics Devices Lab - Lab 5: BJT Biasing in Switching Applications (NPN 2N3904)
Verification, Nonlinear Ebers-Moll Reference Solver, PDF Figure Extraction, and Plotting.
"""

from pathlib import Path
import numpy as np
import pymupdf
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyBboxPatch

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
LAB_DIR = Path(r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\EE091IU_Electronics_Devices_Lab\Lab5")
FIG_DIR = LAB_DIR / "figures"
PDF_PATH = Path(r"C:\Users\LENOVO\OneDrive\Desktop\UNIVERSITY\IU Junior\ED lab\lab5\lab5.pdf")
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# (a) Analytical Verification & Assertions (Piecewise-Linear Textbook Model)
# ---------------------------------------------------------------------------
def verify_analytical():
    v_cc = 5.0          # V
    r_c = 470.0         # Ohm
    r_b_exp1 = 10e3     # Ohm
    v_be_on = 0.70      # V
    v_ce_sat = 0.20     # V
    beta_min = 100.0
    beta_typ = 300.0

    # --- Experiment 1: Vin = 0 V (Cutoff) ---
    exp1_off = dict(v_be=0.0, v_ce=v_cc, v_c=v_cc, v_b=0.0, i_b=0.0, i_c=0.0)
    assert np.isclose(exp1_off["v_ce"], 5.00, atol=1e-9)
    assert np.isclose(exp1_off["i_b"], 0.0, atol=1e-12)
    assert np.isclose(exp1_off["i_c"], 0.0, atol=1e-12)

    # --- Experiment 1: Vin = 5 V (Saturation) ---
    v_in_hi = 5.0
    i_b_1 = (v_in_hi - v_be_on) / r_b_exp1
    i_c_sat_1 = (v_cc - v_ce_sat) / r_c
    beta_forced_1 = i_c_sat_1 / i_b_1

    i_b_min_100_1 = i_c_sat_1 / beta_min
    r_b_max_100_1 = (v_in_hi - v_be_on) / i_b_min_100_1
    odf_100_1 = i_b_1 / i_b_min_100_1

    i_b_min_300_1 = i_c_sat_1 / beta_typ
    r_b_max_300_1 = (v_in_hi - v_be_on) / i_b_min_300_1
    odf_300_1 = i_b_1 / i_b_min_300_1

    p_q_1 = v_ce_sat * i_c_sat_1 + v_be_on * i_b_1
    p_rc_1 = (i_c_sat_1 ** 2) * r_c
    p_rb_1 = (i_b_1 ** 2) * r_b_exp1
    p_q_active_max_1 = (v_cc ** 2) / (4.0 * r_c)  # Collector-emitter peak on load line (V_CE = V_CC/2)
    p_q_total_max_1 = p_q_active_max_1 + v_be_on * ((v_cc / (2.0 * r_c)) / beta_min)

    assert np.isclose(i_b_1 * 1e3, 0.430, atol=1e-4)
    assert np.isclose(i_c_sat_1 * 1e3, 10.2128, atol=1e-3)
    assert np.isclose(beta_forced_1, 23.7506, atol=1e-3)
    assert np.isclose(i_b_min_100_1 * 1e6, 102.1277, atol=1e-2)
    assert np.isclose(r_b_max_100_1 / 1e3, 42.1042, atol=1e-2)
    assert np.isclose(i_b_min_300_1 * 1e6, 34.0426, atol=1e-2)
    assert np.isclose(r_b_max_300_1 / 1e3, 126.3125, atol=1e-2)
    assert np.isclose(p_q_1 * 1e3, 2.3436, atol=1e-2)
    assert np.isclose(p_rc_1 * 1e3, 49.0213, atol=1e-2)
    assert np.isclose(p_rb_1 * 1e3, 1.8490, atol=1e-2)
    assert np.isclose(p_q_active_max_1 * 1e3, 13.2979, atol=1e-2)
    assert beta_forced_1 < beta_min and beta_forced_1 < beta_typ

    # --- Experiment 2: 1 kHz Square Wave ---
    f_sq = 1e3
    t_period = 1.0 / f_sq
    t_half = 0.5 * t_period
    t_d, t_r, t_s, t_f = 35e-9, 35e-9, 200e-9, 50e-9
    t_on = t_d + t_r
    t_off = t_s + t_f
    assert np.isclose(t_period * 1e3, 1.0, atol=1e-9)
    assert np.isclose(t_half * 1e3, 0.5, atol=1e-9)
    assert np.isclose(t_on * 1e9, 70.0, atol=1e-9)
    assert np.isclose(t_off * 1e9, 250.0, atol=1e-9)
    assert (t_on + t_off) / t_half < 0.001

    # --- Experiment 3: LED in series with Rc = 470 Ohm ---
    v_led_nom = 2.0
    v_led_low = 1.8
    i_c_sat_3 = (v_cc - v_led_nom - v_ce_sat) / r_c
    i_c_sat_3_low = (v_cc - v_led_low - v_ce_sat) / r_c

    i_b_min_100_3 = i_c_sat_3 / beta_min
    r_b_max_100_3 = (v_in_hi - v_be_on) / i_b_min_100_3
    i_b_min_300_3 = i_c_sat_3 / beta_typ
    r_b_max_300_3 = (v_in_hi - v_be_on) / i_b_min_300_3

    i_b_min_100_3_low = i_c_sat_3_low / beta_min
    r_b_max_100_3_low = (v_in_hi - v_be_on) / i_b_min_100_3_low

    assert np.isclose(i_c_sat_3 * 1e3, 5.9574, atol=1e-3)
    assert np.isclose(i_c_sat_3_low * 1e3, 6.3830, atol=1e-3)
    assert np.isclose(i_b_min_100_3 * 1e6, 59.5745, atol=1e-2)
    assert np.isclose(r_b_max_100_3 / 1e3, 72.1786, atol=1e-2)
    assert np.isclose(i_b_min_300_3 * 1e6, 19.8582, atol=1e-2)
    assert np.isclose(r_b_max_300_3 / 1e3, 216.5357, atol=1e-2)
    assert np.isclose(r_b_max_100_3_low / 1e3, 67.3667, atol=1e-2)

    rb_list = [4.7e3, 10e3, 22e3, 47e3]
    expected_exp3 = [
        (0.9149, 6.51, 15.36, 46.07),
        (0.4300, 13.85, 7.22, 21.65),
        (0.1955, 30.48, 3.28, 9.84),
        (0.0915, 65.12, 1.54, 4.61),
    ]
    exp3_rows = []
    for rb, (ib_exp, bf_exp, odf100_exp, odf300_exp) in zip(rb_list, expected_exp3):
        ib = (v_in_hi - v_be_on) / rb
        bf = i_c_sat_3 / ib
        odf100 = ib / i_b_min_100_3
        odf300 = ib / i_b_min_300_3
        p_q = v_ce_sat * i_c_sat_3 + v_be_on * ib
        p_rc = (i_c_sat_3 ** 2) * r_c
        p_led = v_led_nom * i_c_sat_3
        assert np.isclose(ib * 1e3, ib_exp, atol=1e-3)
        assert np.isclose(bf, bf_exp, atol=1e-2)
        assert np.isclose(odf100, odf100_exp, atol=1e-2)
        assert np.isclose(odf300, odf300_exp, atol=1e-2)
        assert rb < r_b_max_100_3 and rb < r_b_max_100_3_low
        exp3_rows.append(dict(rb=rb, ib=ib, ic=i_c_sat_3, bf=bf, odf100=odf100, odf300=odf300,
                              p_q=p_q, p_rc=p_rc, p_led=p_led))

    p_q_active_max_3 = ((v_cc - v_led_nom) ** 2) / (4.0 * r_c)

    print("=" * 84)
    print("PART (a): ANALYTICAL VERIFICATION (ALL ASSERTIONS PASSED)")
    print("=" * 84)
    print(f"Exp 1 (Vin=0 V, Cutoff): V_BE={exp1_off['v_be']:.2f} V, V_CE={exp1_off['v_ce']:.2f} V, "
          f"I_B={exp1_off['i_b']*1e3:.3f} mA, I_C={exp1_off['i_c']*1e3:.2f} mA")
    print(f"Exp 1 (Vin=5 V, Sat):    V_BE={v_be_on:.2f} V, V_CE={v_ce_sat:.2f} V, "
          f"I_B={i_b_1*1e3:.3f} mA, I_C={i_c_sat_1*1e3:.2f} mA, beta_f={beta_forced_1:.2f}")
    print(f"  Saturation limits (Exp 1): beta=100 -> I_B(min)={i_b_min_100_1*1e6:.2f} uA, "
          f"R_B(max)={r_b_max_100_1/1e3:.2f} kOhm, ODF={odf_100_1:.2f}")
    print(f"                             beta=300 -> I_B(min)={i_b_min_300_1*1e6:.2f} uA, "
          f"R_B(max)={r_b_max_300_1/1e3:.2f} kOhm, ODF={odf_300_1:.2f}")
    print(f"  Power (Exp 1, Sat):    P_Q={p_q_1*1e3:.2f} mW, P_RC={p_rc_1*1e3:.2f} mW, P_RB={p_rb_1*1e3:.2f} mW")
    print(f"  Power (Exp 1, Active): P_C,max={p_q_active_max_1*1e3:.2f} mW (P_Q,total_max={p_q_total_max_1*1e3:.2f} mW)")
    print(f"Exp 2 (1 kHz sq. wave):  T={t_period*1e3:.1f} ms, T/2={t_half*1e3:.1f} ms, "
          f"t_on<={t_on*1e9:.0f} ns, t_off<={t_off*1e9:.0f} ns, (t_on+t_off)/(T/2)={(t_on+t_off)/t_half*100:.3f}%")
    print("-" * 84)
    print(f"Exp 3 (LED V_LED=2.0 V): I_C(sat)={i_c_sat_3*1e3:.4f} mA (~{i_c_sat_3*1e3:.2f} mA), "
          f"P_C,max(active)={p_q_active_max_3*1e3:.2f} mW")
    print(f"  beta=100: I_B(min)={i_b_min_100_3*1e6:.2f} uA, R_B(max)={r_b_max_100_3/1e3:.2f} kOhm")
    print(f"  beta=300: I_B(min)={i_b_min_300_3*1e6:.2f} uA, R_B(max)={r_b_max_300_3/1e3:.2f} kOhm")
    print(f"Exp 3 Sensitivity (V_LED=1.8 V): I_C(sat)={i_c_sat_3_low*1e3:.4f} mA (~{i_c_sat_3_low*1e3:.2f} mA), "
          f"I_B(min,100)={i_b_min_100_3_low*1e6:.2f} uA, R_B(max,100)={r_b_max_100_3_low/1e3:.2f} kOhm")
    print(f"  {'R_B (kOhm)':>10} | {'I_B (mA)':>9} | {'I_C (mA)':>9} | {'beta_f':>7} | {'ODF_100':>8} | {'ODF_300':>8} | {'P_Q (mW)':>8}")
    for row in exp3_rows:
        print(f"  {row['rb']/1e3:10.1f} | {row['ib']*1e3:9.4f} | {row['ic']*1e3:9.4f} | "
              f"{row['bf']:7.2f} | {row['odf100']:8.2f} | {row['odf300']:8.2f} | {row['p_q']*1e3:8.2f}")

    return dict(
        v_cc=v_cc, r_c=r_c, v_be_on=v_be_on, v_ce_sat=v_ce_sat,
        beta_min=beta_min, beta_typ=beta_typ,
        i_c_sat_3=i_c_sat_3, i_c_sat_3_low=i_c_sat_3_low,
        i_b_min_100_3=i_b_min_100_3, r_b_max_100_3=r_b_max_100_3,
        i_b_min_300_3=i_b_min_300_3, r_b_max_300_3=r_b_max_300_3,
        exp3_rows=exp3_rows,
    )


# ---------------------------------------------------------------------------
# (b) Nonlinear Reference Solver: Ebers-Moll (2N3904) + Shockley LED
# ---------------------------------------------------------------------------
def solve_ebers_moll(v_in, v_cc, r_b, r_c, beta_f=300.0, beta_r=0.7,
                     i_s=6.734e-15, v_t=25.85e-3, r_b_int=10.0, r_c_int=1.0,
                     with_led=False, v_led_ref=2.0, i_led_ref=6.0e-3, n_led=2.0):
    """Damped Newton-Raphson solver for DC operating point of 2N3904 switch."""
    r_b_tot = r_b + r_b_int
    r_c_tot = r_c + r_c_int
    i_s_led = i_led_ref / (np.exp(v_led_ref / (n_led * v_t)) - 1.0)

    def eval_bjt(v_be, v_bc):
        e_be = np.exp(np.clip(v_be / v_t, -100.0, 45.0))
        e_bc = np.exp(np.clip(v_bc / v_t, -100.0, 45.0))
        i_f = i_s * (e_be - 1.0)
        i_r = i_s * (e_bc - 1.0)
        di_f = (i_s / v_t) * e_be
        di_r = (i_s / v_t) * e_bc
        i_b = i_f / beta_f + i_r / beta_r
        i_c = i_f - i_r * (1.0 + 1.0 / beta_r)
        dib_dvbe, dib_dvbc = di_f / beta_f, di_r / beta_r
        dic_dvbe, dic_dvbc = di_f, -di_r * (1.0 + 1.0 / beta_r)
        return i_b, i_c, dib_dvbe, dib_dvbc, dic_dvbe, dic_dvbc

    if not with_led:
        x = np.array([0.70, 0.60]) if v_in > 0.5 else np.array([0.0, -v_cc])
        for _ in range(200):
            v_be, v_bc = x
            i_b, i_c, dib_be, dib_bc, dic_be, dic_bc = eval_bjt(v_be, v_bc)
            f = np.array([
                v_be + i_b * r_b_tot - v_in,
                (v_be - v_bc) + i_c * r_c_tot - v_cc,
            ])
            if np.max(np.abs(f)) < 1e-12:
                break
            J = np.array([
                [1.0 + dib_be * r_b_tot, dib_bc * r_b_tot],
                [1.0 + dic_be * r_c_tot, -1.0 + dic_bc * r_c_tot],
            ])
            dx = np.linalg.solve(J, -f)
            step = np.max(np.abs(dx))
            if step > 0.04:
                dx *= 0.04 / step
            x += dx
        v_be, v_bc = x
        v_led = 0.0
    else:
        x = np.array([0.70, 0.60, 1.98]) if v_in > 0.5 else np.array([0.0, -3.5, 1.5])
        for _ in range(300):
            v_be, v_bc, v_led = x
            i_b, i_c, dib_be, dib_bc, dic_be, dic_bc = eval_bjt(v_be, v_bc)
            e_led = np.exp(np.clip(v_led / (n_led * v_t), -100.0, 50.0))
            i_led = i_s_led * (e_led - 1.0)
            di_led = (i_s_led / (n_led * v_t)) * e_led
            f = np.array([
                v_be + i_b * r_b_tot - v_in,
                (v_be - v_bc) + i_c * r_c_tot + v_led - v_cc,
                i_led - i_c,
            ])
            if np.max(np.abs(f)) < 1e-12:
                break
            J = np.array([
                [1.0 + dib_be * r_b_tot, dib_bc * r_b_tot, 0.0],
                [1.0 + dic_be * r_c_tot, -1.0 + dic_bc * r_c_tot, 1.0],
                [-dic_be, -dic_bc, di_led],
            ])
            dx = np.linalg.solve(J, -f)
            step = np.max(np.abs(dx))
            if step > 0.04:
                dx *= 0.04 / step
            x += dx
        v_be, v_bc, v_led = x

    i_b, i_c, *_ = eval_bjt(v_be, v_bc)
    v_be_term = v_be + i_b * r_b_int
    v_ce_term = (v_be - v_bc) + i_c * r_c_int
    # Verify KVL residuals
    assert abs(v_be_term + i_b * r_b - v_in) < 1e-9
    assert abs(v_ce_term + i_c * r_c + v_led - v_cc) < 1e-9
    return dict(v_be=v_be_term, v_ce=v_ce_term, v_led=v_led, i_b=i_b, i_c=i_c)


def run_ebers_moll_reference():
    print("\n" + "=" * 84)
    print("PART (b): NONLINEAR EBERS-MOLL REFERENCE (2N3904, FOR DISCUSSION ONLY)")
    print("Model: I_S=6.734e-15 A, V_T=25.85 mV, beta_R=0.7, R_B,int=10 Ohm, R_C,int=1 Ohm")
    print("=" * 84)
    header = (f"{'Case':<24} | {'beta_F':>6} | {'V_BE (V)':>8} | {'V_CE (V)':>8} | "
              f"{'V_LED (V)':>9} | {'I_B (mA)':>8} | {'I_C (mA)':>8}")
    print(header)
    print("-" * len(header))

    cases = [
        ("Exp 1: Vin=0V, 10k",  0.0, 10e3, False),
        ("Exp 1: Vin=5V, 10k",  5.0, 10e3, False),
        ("Exp 3: LED, 4.7k",    5.0, 4.7e3, True),
        ("Exp 3: LED, 10k",     5.0, 10e3, True),
        ("Exp 3: LED, 22k",     5.0, 22e3, True),
        ("Exp 3: LED, 47k",     5.0, 47e3, True),
    ]
    results = []
    for label, v_in, r_b, with_led in cases:
        for beta_f in (100.0, 300.0):
            res = solve_ebers_moll(v_in=v_in, v_cc=5.0, r_b=r_b, r_c=470.0,
                                   beta_f=beta_f, with_led=with_led)
            if v_in > 0.5:
                assert 0.65 <= res["v_be"] <= 0.74, f"Unexpected V_BE={res['v_be']}"
                assert 0.04 <= res["v_ce"] <= 0.16, f"Unexpected V_CE={res['v_ce']}"
            else:
                assert abs(res["v_be"]) < 1e-6 and abs(res["v_ce"] - 5.0) < 1e-6
            vled_str = f"{res['v_led']:9.3f}" if with_led else f"{'N/A':>9}"
            print(f"{label:<24} | {beta_f:6.0f} | {res['v_be']:8.4f} | {res['v_ce']:8.4f} | "
                  f"{vled_str} | {res['i_b']*1e3:8.4f} | {res['i_c']*1e3:8.4f}")
            results.append((label, beta_f, res))
    return results


# ---------------------------------------------------------------------------
# (c) Clean PDF Figure Extraction from lab5.pdf
# ---------------------------------------------------------------------------
def trim_whitespace(img: Image.Image, pad: int = 16, thresh: int = 248) -> Image.Image:
    rgb = img.convert("RGB")
    arr = np.asarray(rgb)
    mask = np.any(arr < thresh, axis=2)
    if not np.any(mask):
        return rgb
    ys, xs = np.where(mask)
    y0, y1 = max(0, int(ys.min())), min(arr.shape[0], int(ys.max()) + 1)
    x0, x1 = max(0, int(xs.min())), min(arr.shape[1], int(xs.max()) + 1)
    cropped = rgb.crop((x0, y0, x1, y1))
    out = Image.new("RGB", (cropped.width + 2 * pad, cropped.height + 2 * pad), (255, 255, 255))
    out.paste(cropped, (pad, pad))
    return out


def extract_xref_rgb(doc: pymupdf.Document, xref: int) -> Image.Image:
    pix = pymupdf.Pixmap(doc, xref)
    if pix.alpha:
        bg = pymupdf.Pixmap(pymupdf.csRGB, pix.irect, False)
        bg.set_rect(bg.irect, (255, 255, 255))
        bg.copy(pix, pix.irect)
        pix = bg
    elif pix.colorspace.n != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def extract_pdf_figures():
    doc = pymupdf.open(PDF_PATH)

    # Fig 1 (Page 2): Combine xref 65 (BJT symbols) + xref 66 (2N3904/2N3906 pinout)
    img_sym = trim_whitespace(extract_xref_rgb(doc, 65), pad=12)
    img_pin = trim_whitespace(extract_xref_rgb(doc, 66), pad=12)
    # Upscale pinout cleanly to match ~90% width of symbol image for balanced visual layout
    target_w = int(img_sym.width * 0.90)
    scale = target_w / img_pin.width
    img_pin_rs = img_pin.resize((target_w, int(round(img_pin.height * scale))), Image.Resampling.LANCZOS)

    gap = 24
    pad = 20
    canvas_w = max(img_sym.width, img_pin_rs.width) + 2 * pad
    canvas_h = img_sym.height + img_pin_rs.height + gap + 2 * pad
    fig1 = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
    fig1.paste(img_sym, ((canvas_w - img_sym.width) // 2, pad))
    fig1.paste(img_pin_rs, ((canvas_w - img_pin_rs.width) // 2, pad + img_sym.height + gap))
    fig1.save(FIG_DIR / "fig1_bjt_symbol_pinout.png", dpi=(300, 300))

    # Fig 2 (Page 3, xref 78): Base HIGH -> Vc LOW
    fig2 = trim_whitespace(extract_xref_rgb(doc, 78), pad=18)
    fig2.save(FIG_DIR / "fig2_switch_high.png", dpi=(300, 300))

    # Fig 3 (Page 4, xref 82): Base LOW -> Vc HIGH
    fig3 = trim_whitespace(extract_xref_rgb(doc, 82), pad=18)
    fig3.save(FIG_DIR / "fig3_switch_low.png", dpi=(300, 300))

    # Fig 4 (Page 5, xref 86): Experiment 1 circuit
    fig4 = trim_whitespace(extract_xref_rgb(doc, 86), pad=18)
    fig4.save(FIG_DIR / "fig4_exp1_circuit.png", dpi=(300, 300))

    doc.close()


# ---------------------------------------------------------------------------
# (d) High-Quality Technical Figures (300 DPI)
# ---------------------------------------------------------------------------
def _draw_resistor_h(ax, x0, x1, y, amp=0.22, n_zigs=6, lw=2.0, color="#1a1a1a"):
    lead = 0.16 * (x1 - x0)
    xs = [x0, x0 + lead]
    ys = [y, y]
    body_start, body_end = x0 + lead, x1 - lead
    step = (body_end - body_start) / (n_zigs * 2)
    for k in range(n_zigs * 2):
        xk = body_start + (k + 0.5) * step
        yk = y + (amp if k % 2 == 0 else -amp)
        xs.append(xk)
        ys.append(yk)
    xs.extend([body_end, x1])
    ys.extend([y, y])
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", solid_joinstyle="round")


def _draw_resistor_v(ax, x, y0, y1, amp=0.22, n_zigs=6, lw=2.0, color="#1a1a1a"):
    lead = 0.16 * (y1 - y0)
    ys = [y0, y0 + lead]
    xs = [x, x]
    body_start, body_end = y0 + lead, y1 - lead
    step = (body_end - body_start) / (n_zigs * 2)
    for k in range(n_zigs * 2):
        yk = body_start + (k + 0.5) * step
        xk = x + (amp if k % 2 == 0 else -amp)
        xs.append(xk)
        ys.append(yk)
    xs.extend([x, x])
    ys.extend([body_end, y1])
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", solid_joinstyle="round")


def _draw_ground(ax, x, y, lw=2.0, color="#1a1a1a"):
    ax.plot([x - 0.36, x + 0.36], [y, y], color=color, lw=lw)
    ax.plot([x - 0.24, x + 0.24], [y - 0.13, y - 0.13], color=color, lw=lw)
    ax.plot([x - 0.12, x + 0.12], [y - 0.26, y - 0.26], color=color, lw=lw)


def plot_fig5_exp3_circuit():
    fig, ax = plt.subplots(figsize=(9.6, 5.8), dpi=300)
    ax.set_xlim(0.0, 12.8)
    ax.set_ylim(0.0, 7.6)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ink = "#1a1a1a"
    blue = "#1f5a99"
    red = "#c0392b"
    green = "#1e7e46"

    # Key coordinates
    x_in = 0.95
    x_rb0, x_rb1 = 1.65, 3.85
    x_b_node = 4.55
    x_q = 6.15
    y_q = 2.85
    x_c = 6.50
    y_gnd = 0.75
    y_vcc = 6.85

    # Input terminal Vin
    ax.plot([x_in, x_rb0], [y_q, y_q], color=ink, lw=2.0)
    ax.add_patch(Circle((x_in, y_q), 0.10, facecolor="white", edgecolor=ink, lw=2.0, zorder=5))
    ax.text(x_in - 0.05, y_q + 0.55, r"$V_{in}$", fontsize=13, fontweight="bold", ha="center", color=blue)
    ax.text(x_in - 0.05, y_q - 0.50, "0 V (LOW)\n5 V (HIGH)", fontsize=9.5, ha="center", va="top", color="#333333")

    # Base resistor RB
    _draw_resistor_h(ax, x_rb0, x_rb1, y_q, amp=0.22)
    ax.plot([x_rb1, x_q - 0.28], [y_q, y_q], color=ink, lw=2.0)
    ax.text(0.5 * (x_rb0 + x_rb1), y_q + 0.42, r"$R_B$", fontsize=12.5, fontweight="bold", ha="center", color=ink)
    ax.text(0.5 * (x_rb0 + x_rb1), y_q - 0.42, r"$\{4.7,\ 10,\ 22,\ 47\}\ \mathrm{k\Omega}$",
            fontsize=9.5, ha="center", va="top", color="#333333")

    # Base node dot + I_B arrow
    ax.add_patch(Circle((x_b_node, y_q), 0.07, facecolor=ink, edgecolor=ink, zorder=5))
    ax.text(x_b_node, y_q - 0.34, r"$V_B$", fontsize=11, fontweight="bold", ha="center", color=blue)
    ax.annotate("", xy=(x_b_node + 0.20, y_q + 0.26), xytext=(x_rb1 + 0.15, y_q + 0.26),
                arrowprops=dict(arrowstyle="->", color=blue, lw=1.6))
    ax.text(0.5 * (x_rb1 + x_b_node + 0.25), y_q + 0.38, r"$I_B$", fontsize=10.5, fontweight="bold", ha="center", color=blue)

    # NPN Transistor Q1 (2N3904)
    q_r = 0.68
    ax.add_patch(Circle((x_q, y_q), q_r, facecolor="#f9fafb", edgecolor=ink, lw=2.0, zorder=2))
    x_bar = x_q - 0.28
    ax.plot([x_bar, x_bar], [y_q - 0.38, y_q + 0.38], color=ink, lw=2.8, zorder=3)
    ax.plot([x_bar, x_c], [y_q + 0.16, y_q + 0.52], color=ink, lw=2.0, zorder=3)
    ax.plot([x_bar, x_c], [y_q - 0.16, y_q - 0.52], color=ink, lw=2.0, zorder=3)
    ax.annotate("", xy=(x_c - 0.03, y_q - 0.50), xytext=(x_bar + 0.20, y_q - 0.29),
                arrowprops=dict(arrowstyle="-|>,head_width=0.22,head_length=0.35", color=ink, lw=1.8), zorder=4)
    ax.text(x_bar - 0.22, y_q + 0.16, "B", fontsize=9.5, fontweight="bold", color="#444444")
    ax.text(x_c + 0.18, y_q + 0.54, "C", fontsize=9.5, fontweight="bold", color="#444444")
    ax.text(x_c + 0.18, y_q - 0.62, "E", fontsize=9.5, fontweight="bold", color="#444444")
    ax.text(x_q + 0.88, y_q + 0.06, "Q1\n2N3904\n(NPN)", fontsize=10.5, fontweight="bold",
            va="center", ha="left", color=ink)

    # Emitter to GND
    ax.plot([x_c, x_c], [y_q - 0.52, y_gnd], color=ink, lw=2.0)
    _draw_ground(ax, x_c, y_gnd)
    ax.text(x_c + 0.52, y_gnd - 0.05, r"GND ($V_E = 0\ \mathrm{V}$)", fontsize=9.5, va="center", color="#333333")

    # Collector vertical path: Q1(C) -> node Vc -> LED -> Rc -> Vcc
    y_vc = 3.72
    y_led_bot = 4.05
    y_led_top = 4.65
    y_rc_bot = 5.10
    y_rc_top = 6.55

    ax.plot([x_c, x_c], [y_q + 0.52, y_led_bot], color=ink, lw=2.0)
    ax.add_patch(Circle((x_c, y_vc), 0.07, facecolor=ink, edgecolor=ink, zorder=5))
    ax.text(x_c - 0.24, y_vc, r"$V_C$", fontsize=11, fontweight="bold", ha="right", va="center", color=red)

    # LED symbol (pointing downward: Anode top -> Cathode bottom)
    tri = Polygon([[x_c - 0.28, y_led_top], [x_c + 0.28, y_led_top], [x_c, y_led_bot]],
                  closed=True, facecolor="#fdecea", edgecolor=red, lw=2.0, zorder=4)
    ax.add_patch(tri)
    ax.plot([x_c - 0.28, x_c + 0.28], [y_led_bot, y_led_bot], color=red, lw=2.4, zorder=4)
    ax.annotate("", xy=(x_c + 0.66, y_led_bot + 0.14), xytext=(x_c + 0.34, y_led_bot + 0.38),
                arrowprops=dict(arrowstyle="->", color=red, lw=1.4))
    ax.annotate("", xy=(x_c + 0.66, y_led_bot - 0.08), xytext=(x_c + 0.34, y_led_bot + 0.16),
                arrowprops=dict(arrowstyle="->", color=red, lw=1.4))
    ax.text(x_c + 0.78, 0.5 * (y_led_bot + y_led_top) + 0.05, "LED\n" + r"($V_{LED} \approx 2.0\ \mathrm{V}$)",
            fontsize=9.8, fontweight="bold", va="center", ha="left", color=red)

    # Wire between LED and Rc + Ic arrow
    ax.plot([x_c, x_c], [y_led_top, y_rc_bot], color=ink, lw=2.0)
    ax.annotate("", xy=(x_c - 0.30, y_led_top + 0.02), xytext=(x_c - 0.30, y_rc_bot - 0.02),
                arrowprops=dict(arrowstyle="->", color=red, lw=1.6))
    ax.text(x_c - 0.45, 0.5 * (y_led_top + y_rc_bot), r"$I_C$", fontsize=11, fontweight="bold",
            ha="right", va="center", color=red)

    # Collector resistor Rc
    _draw_resistor_v(ax, x_c, y_rc_bot, y_rc_top, amp=0.22)
    ax.text(x_c + 0.40, 0.5 * (y_rc_bot + y_rc_top), r"$R_C = 470\ \Omega$",
            fontsize=11.5, fontweight="bold", va="center", ha="left", color=ink)

    # Vcc rail
    ax.plot([x_c, x_c], [y_rc_top, y_vcc], color=ink, lw=2.0)
    ax.plot([x_c - 0.32, x_c + 0.32], [y_vcc, y_vcc], color=ink, lw=2.4)
    ax.text(x_c, y_vcc + 0.22, r"$V_{CC} = +5.0\ \mathrm{V}$", fontsize=12, fontweight="bold",
            ha="center", va="bottom", color=ink)

    # V_CE measurement indicator (cleanly separated from V_B and Q1)
    x_vce = 5.18
    ax.annotate("", xy=(x_vce, y_vc - 0.02), xytext=(x_vce, y_gnd + 0.40),
                arrowprops=dict(arrowstyle="<->", color=green, lw=1.35, ls="--"))
    ax.text(x_vce - 0.16, 1.65, r"$V_{CE}$", fontsize=10.5,
            fontweight="bold", ha="right", va="center", color=green)

    # Summary design box on right (ample horizontal clearance from LED label)
    box = FancyBboxPatch((9.15, 1.35), 3.35, 4.90, boxstyle="round,pad=0.18,rounding_size=0.18",
                         facecolor="#f5f8fc", edgecolor="#b8cce4", lw=1.3)
    ax.add_patch(box)
    ax.text(10.825, 5.95, "Experiment 3 Summary", fontsize=10.5, fontweight="bold", ha="center", color="#1a3b5d")
    ax.plot([9.35, 12.30], [5.72, 5.72], color="#b8cce4", lw=1.0)
    info_lines = [
        r"$\bullet\ V_{CC} = 5.0\ \mathrm{V},\ R_C = 470\ \Omega$",
        r"$\bullet\ \mathrm{Q1: 2N3904}\ (\beta \in [100, 300])$",
        r"$\bullet\ V_{BE(\mathrm{on})} = 0.70\ \mathrm{V}$",
        r"$\bullet\ V_{CE(\mathrm{sat})} = 0.20\ \mathrm{V}$",
        r"$\bullet\ V_{LED} = 2.0\ \mathrm{V\ (assumed)}$",
        "",
        "Saturation Target (HIGH):",
        r"$\bullet\ I_{C(\mathrm{sat})} \approx 5.96\ \mathrm{mA}$",
        r"$\bullet\ R_{B(\max)}(\beta=100) = 72.18\ \mathrm{k\Omega}$",
        r"$\bullet\ R_{B(\max)}(\beta=300) = 216.54\ \mathrm{k\Omega}$",
        r"$\bullet\ \mathrm{All\ 4\ } R_B \mathrm{\ values\ saturate}$",
    ]
    y_txt = 5.42
    for line in info_lines:
        is_hdr = line.startswith("Saturation")
        ax.text(9.38, y_txt, line, fontsize=8.8, fontweight="bold" if is_hdr else "normal",
                va="top", ha="left", color="#1a3b5d" if is_hdr else "#222222")
        y_txt -= 0.36 if line else 0.16

    ax.set_title("Experiment 3: NPN BJT Switch Driving an LED with Variable Base Resistor",
                 fontsize=12.5, fontweight="bold", pad=10, color="#111111")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig5_exp3_led_circuit.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_fig6_exp2_waveforms():
    t_ms = np.linspace(0.0, 2.4999, 5000)
    # 1 kHz square wave, D = 50%, HIGH on [0, 0.5), [1.0, 1.5), [2.0, 2.5)
    high = ((t_ms % 1.0) < 0.5).astype(float)
    v_in = 5.0 * high
    v_b = 0.70 * high
    v_c = 5.00 - (5.00 - 0.20) * high  # 0.20 V when HIGH, 5.00 V when LOW

    fig, axes = plt.subplots(3, 1, figsize=(9.2, 6.8), sharex=True, dpi=300)
    fig.patch.set_facecolor("white")

    # Shaded regions for SATURATION (HIGH) vs CUTOFF (LOW)
    sat_intervals = [(0.0, 0.5), (1.0, 1.5), (2.0, 2.5)]
    off_intervals = [(0.5, 1.0), (1.5, 2.0)]
    for ax in axes:
        for a, b in sat_intervals:
            ax.axvspan(a, b, color="#e8f3fc", alpha=0.65, zorder=0)
        for a, b in off_intervals:
            ax.axvspan(a, b, color="#f7f7f7", alpha=0.65, zorder=0)
        ax.grid(True, linestyle=":", linewidth=0.7, color="#cccccc", zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Panel 1: V_in(t)
    axes[0].plot(t_ms, v_in, color="#1b5e9f", lw=2.2, zorder=3)
    axes[0].set_ylim(-0.6, 6.2)
    axes[0].set_yticks([0, 2.5, 5.0])
    axes[0].set_ylabel(r"$V_{in}(t)$ (V)", fontsize=10.5, fontweight="bold")
    axes[0].text(0.25, 5.25, "HIGH = 5.0 V", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1b5e9f")
    axes[0].text(0.75, 0.35, "LOW = 0.0 V", ha="center", va="bottom", fontsize=9, color="#555555")
    axes[0].annotate("", xy=(1.0, 3.0), xytext=(2.0, 3.0),
                     arrowprops=dict(arrowstyle="<->", color="#222222", lw=1.3))
    axes[0].text(1.5, 3.22, r"$T = 1.0\ \mathrm{ms}$ ($T/2 = 0.5\ \mathrm{ms}$)", ha="center",
                 va="bottom", fontsize=9, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#cccccc", alpha=0.9))

    # Panel 2: V_B(t)
    axes[1].plot(t_ms, v_b, color="#d35400", lw=2.2, zorder=3)
    axes[1].axhline(0.70, color="#d35400", ls="--", lw=1.0, alpha=0.7)
    axes[1].set_ylim(-0.15, 1.10)
    axes[1].set_yticks([0.0, 0.35, 0.70, 1.0])
    axes[1].set_ylabel(r"$V_B(t)$ (V)", fontsize=10.5, fontweight="bold")
    axes[1].text(1.25, 0.77, r"Clamped at $V_{BE(\mathrm{on})} \approx 0.70\ \mathrm{V}$ (In-phase with $V_{in}$)",
                 ha="center", va="bottom", fontsize=9, fontweight="bold", color="#a04000")
    axes[1].text(1.75, 0.08, r"$0.0\ \mathrm{V}$ (OFF)", ha="center", va="bottom", fontsize=8.8, color="#555555")

    # Panel 3: V_C(t)
    axes[2].plot(t_ms, v_c, color="#c0392b", lw=2.2, zorder=3)
    axes[2].axhline(5.00, color="#7f8c8d", ls="--", lw=0.9, alpha=0.7)
    axes[2].axhline(0.20, color="#c0392b", ls="--", lw=1.0, alpha=0.7)
    axes[2].set_ylim(-0.6, 6.2)
    axes[2].set_yticks([0.2, 2.5, 5.0])
    axes[2].set_ylabel(r"$V_C(t)$ (V)", fontsize=10.5, fontweight="bold")
    axes[2].set_xlabel("Time $t$ (ms)", fontsize=10.5, fontweight="bold")
    axes[2].set_xlim(0.0, 2.5)
    axes[2].set_xticks([0.0, 0.5, 1.0, 1.5, 2.0, 2.5])
    axes[2].text(0.25, 0.55, "SATURATION (ON)\n" + r"$V_C \approx 0.20\ \mathrm{V}$",
                 ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#922b21")
    axes[2].text(0.75, 5.25, "CUTOFF (OFF): " + r"$V_C = 5.00\ \mathrm{V}$",
                 ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#333333")
    axes[2].text(1.75, 2.55, r"$180^\circ$ Phase Inversion",
                 ha="center", va="center", fontsize=9.2, fontweight="bold", color="#922b21",
                 bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#e6b0aa", alpha=0.95))

    fig.suptitle("Experiment 2: Theoretical Expected Waveforms (f = 1 kHz, D = 50% Assumed)",
                 fontsize=12.5, fontweight="bold", y=0.985, color="#111111")
    fig.text(0.5, 0.008,
             r"Note: 2N3904 datasheet switching times ($t_{\mathrm{on}} \leq 70\ \mathrm{ns}$, "
             r"$t_{\mathrm{off}} \leq 250\ \mathrm{ns}$) are $< 0.07\%$ of $T/2 = 500\ \mathrm{\mu s}$, "
             r"so edges appear vertical at 1 kHz.",
             ha="center", fontsize=8.5, color="#444444", style="italic")
    fig.tight_layout(rect=[0.0, 0.03, 1.0, 0.955])
    fig.savefig(FIG_DIR / "fig6_exp2_theoretical_waveforms.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_fig7_exp3_rb_sweep(data):
    rb_k = np.logspace(0.0, np.log10(500.0), 800)  # 1 kOhm to 500 kOhm
    rb_ohm = rb_k * 1e3
    v_in = 5.0
    v_be = data["v_be_on"]
    i_c_sat = data["i_c_sat_3"] * 1e3      # mA (V_LED = 2.0 V)
    i_c_sat_low = data["i_c_sat_3_low"] * 1e3  # mA (V_LED = 1.8 V)

    i_b_mA = (v_in - v_be) / rb_ohm * 1e3
    i_c_100 = np.minimum(i_c_sat, 100.0 * i_b_mA)
    i_c_300 = np.minimum(i_c_sat, 300.0 * i_b_mA)
    beta_f_100 = i_c_100 / i_b_mA

    rb_lab = np.array([4.7, 10.0, 22.0, 47.0])
    ib_lab = (v_in - v_be) / (rb_lab * 1e3) * 1e3
    ic_lab = np.full_like(rb_lab, i_c_sat)
    bf_lab = ic_lab / ib_lab
    odf100_lab = ib_lab / (data["i_b_min_100_3"] * 1e3)

    rb_max_100 = data["r_b_max_100_3"] / 1e3
    rb_max_300 = data["r_b_max_300_3"] / 1e3

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.4, 7.3), sharex=True, dpi=300)
    fig.patch.set_facecolor("white")

    # --- Top Panel: I_C vs R_B ---
    ax1.axvspan(1.0, rb_max_100, color="#eaf7ee", alpha=0.75, zorder=0,
                label=r"Guaranteed Saturation ($\beta \geq 100$)")
    ax1.plot(rb_k, i_c_100, color="#1a4e8a", lw=2.3, label=r"$I_C(R_B)$ for $\beta_{\min} = 100$", zorder=3)
    ax1.plot(rb_k, i_c_300, color="#0e8a7d", lw=2.1, ls="--", label=r"$I_C(R_B)$ for $\beta_{\mathrm{typ}} = 300$", zorder=3)
    ax1.axhline(i_c_sat_low, color="#8e44ad", lw=1.2, ls=":", alpha=0.85,
                label=r"Sensitivity: $I_{C(\mathrm{sat})} = 6.38\ \mathrm{mA}$ ($V_{LED} = 1.8\ \mathrm{V}$)")

    ax1.axvline(rb_max_100, color="#1a4e8a", lw=1.2, ls="-.", alpha=0.85)
    ax1.axvline(rb_max_300, color="#0e8a7d", lw=1.2, ls="-.", alpha=0.85)
    ax1.text(rb_max_100 * 0.92, 1.35, f"$R_{{B(\\max),100}}$\n$= {rb_max_100:.2f}\\ \\mathrm{{k\\Omega}}$",
             ha="right", va="bottom", fontsize=8.5, fontweight="bold", color="#1a4e8a",
             bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#b6cce2", alpha=0.92))
    ax1.text(rb_max_300 * 1.08, 1.35, f"$R_{{B(\\max),300}}$\n$= {rb_max_300:.2f}\\ \\mathrm{{k\\Omega}}$",
             ha="left", va="bottom", fontsize=8.5, fontweight="bold", color="#0e8a7d",
             bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#a8dcd6", alpha=0.92))

    # Plot 4 lab points
    ax1.scatter(rb_lab, ic_lab, color="#c0392b", edgecolor="white", s=62, zorder=5,
                label=r"Lab $R_B$ values ($4.7, 10, 22, 47\ \mathrm{k\Omega}$)")
    for r_val in rb_lab:
        ax1.annotate(f"{r_val:g} k$\\Omega$", xy=(r_val, i_c_sat), xytext=(0, -18),
                     textcoords="offset points", ha="center", va="top", fontsize=8.3,
                     fontweight="bold", color="#922b21")

    ax1.text(3.2, 6.55, r"Saturation Plateau: $I_{C(\mathrm{sat})} = 5.96\ \mathrm{mA}$ ($V_{LED}=2.0\ \mathrm{V}$)",
             fontsize=8.8, fontweight="bold", color="#145a32")
    ax1.text(140.0, 4.7, "Active Roll-off\n" + r"($I_C = \beta I_B$)", fontsize=8.8,
             ha="center", color="#333333", style="italic")

    ax1.set_ylim(0.0, 7.4)
    ax1.set_ylabel(r"Collector Current $I_C$ (mA)", fontsize=10.5, fontweight="bold")
    ax1.grid(True, which="both", linestyle=":", linewidth=0.65, color="#cccccc")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="lower left", fontsize=8.2, frameon=True, facecolor="white", framealpha=0.95)

    # --- Bottom Panel: I_B (left log axis) & beta_forced (right log axis) ---
    ax2.axvspan(1.0, rb_max_100, color="#eaf7ee", alpha=0.75, zorder=0)
    l1, = ax2.loglog(rb_k, i_b_mA, color="#d35400", lw=2.3, label=r"Base Current $I_B = (V_{in}-V_{BE})/R_B$", zorder=3)
    ax2.axhline(data["i_b_min_100_3"] * 1e3, color="#1a4e8a", lw=1.1, ls="--", alpha=0.85)
    ax2.axhline(data["i_b_min_300_3"] * 1e3, color="#0e8a7d", lw=1.1, ls="--", alpha=0.85)
    ax2.text(77.0, data["i_b_min_100_3"] * 1e3 * 1.18,
             r"$I_{B(\min,100)} = 59.57\ \mathrm{\mu A}$", fontsize=8.0, color="#1a4e8a", fontweight="bold",
             ha="left",
             bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    ax2.text(11.5, data["i_b_min_300_3"] * 1e3 * 0.80,
             r"$I_{B(\min,300)} = 19.86\ \mathrm{\mu A}$", fontsize=8.3, color="#0e8a7d", fontweight="bold",
             ha="left", va="top",
             bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))

    ax2.scatter(rb_lab, ib_lab, color="#d35400", edgecolor="white", s=54, zorder=5)
    # Offset perpendicularly away from the downward-sloping I_B line (above-right or below-left)
    odf_specs = [
        (6, 9, "left", "bottom"),
        (2, 12, "center", "bottom"),
        (-4, -13, "right", "top"),
        (-4, -13, "right", "top"),
    ]
    for r_val, ib_val, odf_val, (dx, dy, ha, va) in zip(rb_lab, ib_lab, odf100_lab, odf_specs):
        ax2.annotate(f"ODF={odf_val:.2f}", xy=(r_val, ib_val), xytext=(dx, dy),
                     textcoords="offset points", ha=ha, va=va, fontsize=8.1,
                     fontweight="bold", color="#a04000")

    ax2.axvline(rb_max_100, color="#1a4e8a", lw=1.2, ls="-.", alpha=0.85)
    ax2.axvline(rb_max_300, color="#0e8a7d", lw=1.2, ls="-.", alpha=0.85)
    ax2.set_ylabel(r"Base Current $I_B$ (mA)", fontsize=10.5, fontweight="bold", color="#a04000")
    ax2.tick_params(axis="y", colors="#a04000")
    ax2.set_ylim(5e-3, 35.0)
    ax2.set_xlim(1.0, 500.0)
    ax2.set_xlabel(r"Base Resistance $R_B$ ($\mathrm{k\Omega}$, log scale)", fontsize=10.5, fontweight="bold")
    ax2.grid(True, which="both", linestyle=":", linewidth=0.65, color="#cccccc")
    ax2.spines["top"].set_visible(False)

    # Right axis: beta_forced (capped at beta=100)
    ax2_r = ax2.twinx()
    l2, = ax2_r.loglog(rb_k, beta_f_100, color="#6c3483", lw=2.0, ls="-", alpha=0.9,
                       label=r"Forced Gain $\beta_{\mathrm{forced}} = I_C / I_B$ ($\beta=100$ limit)")
    ax2_r.scatter(rb_lab, bf_lab, color="#6c3483", marker="s", edgecolor="white", s=46, zorder=5)
    # Offset perpendicularly away from the upward-sloping beta_f line (below-right or above-left)
    bf_specs = [
        (6, -12, "left", "top"),
        (2, -15, "center", "top"),
        (-6, 11, "right", "bottom"),
        (-6, 11, "right", "bottom"),
    ]
    for r_val, bf_val, (dx, dy, ha, va) in zip(rb_lab, bf_lab, bf_specs):
        ax2_r.annotate(f"$\\beta_f$={bf_val:.1f}", xy=(r_val, bf_val), xytext=(dx, dy),
                       textcoords="offset points", ha=ha, va=va, fontsize=8.1,
                       fontweight="bold", color="#5b2c6f")
    ax2_r.set_ylabel(r"Forced Current Gain $\beta_{\mathrm{forced}}$", fontsize=10.5, fontweight="bold", color="#5b2c6f")
    ax2_r.tick_params(axis="y", colors="#5b2c6f")
    ax2_r.set_ylim(1.0, 450.0)
    ax2_r.spines["top"].set_visible(False)

    ax2.legend([l1, l2], [l1.get_label(), l2.get_label()], loc="upper left",
               fontsize=8.2, frameon=True, facecolor="white", framealpha=0.96)

    fig.suptitle("Experiment 3: Collector Current, Base Current, and Saturation Margin vs. $R_B$",
                 fontsize=12.5, fontweight="bold", y=0.985, color="#111111")
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.96])
    fig.savefig(FIG_DIR / "fig7_exp3_rb_sweep.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    data = verify_analytical()
    run_ebers_moll_reference()
    extract_pdf_figures()
    plot_fig5_exp3_circuit()
    plot_fig6_exp2_waveforms()
    plot_fig7_exp3_rb_sweep(data)

    print("\n" + "=" * 84)
    print("GENERATED FIGURES CHECK")
    print("=" * 84)
    expected_figs = [
        "fig1_bjt_symbol_pinout.png",
        "fig2_switch_high.png",
        "fig3_switch_low.png",
        "fig4_exp1_circuit.png",
        "fig5_exp3_led_circuit.png",
        "fig6_exp2_theoretical_waveforms.png",
        "fig7_exp3_rb_sweep.png",
    ]
    for name in expected_figs:
        p = FIG_DIR / name
        assert p.exists() and p.stat().st_size > 10_000, f"Missing or too small: {p}"
        with Image.open(p) as im:
            print(f"  OK | {name:<38} | {im.width:4d}x{im.height:<4d} px | {p.stat().st_size/1024:6.1f} KB")


if __name__ == "__main__":
    main()
